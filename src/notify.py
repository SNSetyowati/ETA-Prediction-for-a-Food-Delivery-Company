"""Escalation emails for high-risk active deliveries.

For every High / Critical order in the scored feed this drafts three emails:

- an alert to the customer service lead,
- a delay notification to the customer (no internal risk details),
- an alert with a route recommendation to the driver.

All other orders are written to a log file instead.

By default nothing leaves the machine: emails are saved as .eml drafts in
outputs/notifications/outbox/. Pass --send to deliver them over SMTP; that
needs SMTP_HOST (and optionally SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM)
plus real recipient addresses in data/raw/contacts.csv and CS_LEAD_EMAIL.

Usage:
    python src/notify.py            # draft only (dry run)
    python src/notify.py --send     # draft and send via SMTP
"""
import argparse
import csv
import math
import os
import smtplib
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCORED_PATH = ROOT / "outputs/active_deliveries_ZC_predicted.csv"
CONTACTS_PATH = ROOT / "data/raw/contacts.csv"
OUT_DIR = ROOT / "outputs/notifications"

ESCALATE_CATEGORIES = {"High", "Critical"}
PLACEHOLDER_DOMAIN = "example.com"  # reserved domain: never deliverable
DEFAULT_SENDER = f"eta-alerts@{PLACEHOLDER_DOMAIN}"
DEFAULT_CS_LEAD = f"cs-lead@{PLACEHOLDER_DOMAIN}"

COMPASS = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]


@dataclass
class Contacts:
    cs_lead: str
    customers: dict
    drivers: dict

    def customer(self, order_id):
        return self.customers.get(order_id) or f"customer+{order_id.lower()}@{PLACEHOLDER_DOMAIN}"

    def driver(self, order_id, driver_id):
        return self.drivers.get(order_id) or f"driver+{driver_id.lower()}@{PLACEHOLDER_DOMAIN}"


def load_contacts(path=CONTACTS_PATH):
    """Optional CSV with columns Order_ID, customer_email, driver_email."""
    customers, drivers = {}, {}
    if Path(path).exists():
        for row in pd.read_csv(path, dtype=str).fillna("").to_dict("records"):
            customers[row["Order_ID"]] = row.get("customer_email", "")
            drivers[row["Order_ID"]] = row.get("driver_email", "")
    return Contacts(os.environ.get("CS_LEAD_EMAIL", DEFAULT_CS_LEAD), customers, drivers)


def split_orders(df):
    """Return (escalated, rest). Escalated = High / Critical, highest risk first."""
    mask = df["Risk_Category"].isin(ESCALATE_CATEGORIES)
    order = ["Risk_Score", "Predicted_ETA_min"]
    return (df[mask].sort_values(order, ascending=False),
            df[~mask].sort_values(order, ascending=False))


# ---------------------------------------------------------------------------
# Route recommendation
# ---------------------------------------------------------------------------
def bearing_deg(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    x = math.sin(lon2 - lon1) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def compass(deg):
    return COMPASS[int((deg + 22.5) // 45) % 8]


def route_recommendation(o):
    """Rule-based route advice from traffic, weather, load and distance."""
    # Some restaurant coordinates are sign-flipped in the source data.
    r_lat, r_lon = abs(o["Restaurant_latitude"]), abs(o["Restaurant_longitude"])
    d_lat, d_lon = abs(o["Delivery_location_latitude"]), abs(o["Delivery_location_longitude"])
    heading = compass(bearing_deg(r_lat, r_lon, d_lat, d_lon))
    maps_url = (f"https://www.google.com/maps/dir/?api=1&origin={r_lat:.6f},{r_lon:.6f}"
                f"&destination={d_lat:.6f},{d_lon:.6f}&travelmode=driving")

    tips = []
    traffic = o["Road_traffic_density"]
    if traffic == "Jam":
        tips.append("Traffic is jammed: avoid main arterial roads and flyovers, follow live-traffic "
                    "rerouting in navigation and prefer inner/local roads.")
    elif traffic == "High":
        tips.append("Heavy traffic: take the fastest live-traffic route and avoid known junction bottlenecks.")
    if o["Weather_conditions"] in {"Stormy", "Sandstorms", "Fog"}:
        tips.append(f"{o['Weather_conditions']}: reduce speed, keep headlights on and avoid flood- or "
                    "debris-prone underpasses. Safety comes before the ETA.")
    elif o["Weather_conditions"] in {"Cloudy", "Windy"}:
        tips.append(f"{o['Weather_conditions']} conditions: keep extra distance and watch for sudden gusts or rain.")
    if o["Festival"] == "Yes":
        tips.append("Festival/event today: expect road closures and crowds near venues; plan a detour.")
    if o["multiple_deliveries"] > 0:
        tips.append(f"You carry {int(o['multiple_deliveries'])} other order(s): if the stops allow, "
                    f"deliver {o['Order_ID']} first to protect its ETA.")
    if o["Distance_km"] >= 10:
        tips.append("Long trip (10 km+): check fuel/charge before leaving the restaurant.")
    if not tips:
        tips.append("Take the fastest route suggested by navigation.")
    return {"heading": heading, "maps_url": maps_url, "tips": tips}


# ---------------------------------------------------------------------------
# Email drafts
# ---------------------------------------------------------------------------
def _message(sender, to, subject, body, order_id, role):
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = sender, to, subject
    msg["X-Order-ID"], msg["X-Recipient-Role"] = order_id, role
    msg.set_content(body, cte="8bit")  # keep drafts human-readable
    return msg


def cs_lead_alert(o, to, sender=DEFAULT_SENDER):
    subject = f"[{o['Risk_Category'].upper()}] Delivery risk alert - {o['Order_ID']} ({o['City']})"
    body = f"""Hi CS Lead,

Order {o['Order_ID']} has been flagged as {o['Risk_Category']} risk and may arrive late.

  Risk score        : {int(o['Risk_Score'])} / 100
  Risk drivers      : {o['Risk_Drivers']}
  Weather           : {o['Weather_conditions']} ({o['Weather_Label']})
  Road traffic      : {o['Road_traffic_density']} ({o['Traffic_Label']})
  Festival / event  : {o['Festival_Label']}
  Predicted ETA     : {o['Predicted_ETA_min']:.0f} min (estimated arrival {o['Estimated_Arrival']})
  Ordered / picked  : {o['Time_Ordered']} / {o['Time_Order_picked']}
  Driver            : {o['Delivery_person_ID']} ({o['Type_of_vehicle']}, {int(o['multiple_deliveries'])} other order(s))
  Distance          : {o['Distance_km']:.1f} km

Suggested actions:
  - The customer and the driver have each been emailed separately.
  - Monitor this order and be ready to handle a complaint or offer a voucher if it runs late.

-- ETA Prediction System
"""
    return _message(sender, to, subject, body, o["Order_ID"], "cs_lead")


def customer_notification(o, to, sender=DEFAULT_SENDER):
    reasons = []
    if o["Traffic_Label"] in {"Heavy", "Severe"}:
        reasons.append("heavy traffic")
    if o["Weather_Label"] != "Clear":
        reasons.append(f"{o['Weather_conditions'].lower()} weather")
    if o["Festival"] == "Yes":
        reasons.append("a local festival/event")
    reason = " and ".join(reasons) if reasons else "high demand"
    subject = f"Update on your order {o['Order_ID']}: new estimated arrival {o['Estimated_Arrival']}"
    body = f"""Hi there,

Thank you for your order {o['Order_ID']}. Because of {reason} in your area, your delivery
may take a little longer than usual.

  Updated estimated arrival: around {o['Estimated_Arrival']} (about {o['Predicted_ETA_min']:.0f} minutes after ordering)

Your rider is on the way and we are keeping a close eye on your order. We're sorry for the
wait, and thank you for your patience.

-- Zamato Customer Care
"""
    return _message(sender, to, subject, body, o["Order_ID"], "customer")


def driver_alert(o, to, sender=DEFAULT_SENDER):
    route = route_recommendation(o)
    tips = "\n".join(f"  {i}. {t}" for i, t in enumerate(route["tips"], 1))
    subject = f"[{o['Risk_Category'].upper()}] Delay risk on {o['Order_ID']} - route advice"
    body = f"""Hi {o['Delivery_person_ID']},

Order {o['Order_ID']} is at {o['Risk_Category']} risk of running late.

  Conditions      : {o['Weather_conditions']} weather, {o['Road_traffic_density']} traffic, {o['Festival_Label']}
  Predicted ETA   : {o['Predicted_ETA_min']:.0f} min (target arrival {o['Estimated_Arrival']})
  Trip            : {o['Distance_km']:.1f} km, heading {route['heading']}

Route recommendation:
{tips}

Open route in maps: {route['maps_url']}

Ride safe.
-- Zamato Operations
"""
    return _message(sender, to, subject, body, o["Order_ID"], "driver")


def build_emails(o, contacts, sender=DEFAULT_SENDER):
    return [
        cs_lead_alert(o, contacts.cs_lead, sender),
        customer_notification(o, contacts.customer(o["Order_ID"]), sender),
        driver_alert(o, contacts.driver(o["Order_ID"], o["Delivery_person_ID"]), sender),
    ]


# ---------------------------------------------------------------------------
# Delivery
# ---------------------------------------------------------------------------
def is_placeholder(address):
    return address.strip().lower().endswith("@" + PLACEHOLDER_DOMAIN) or "@" not in address


def smtp_sender():
    """Return a send(msg) function using SMTP_* environment variables."""
    host = os.environ.get("SMTP_HOST")
    if not host:
        raise RuntimeError("--send needs SMTP_HOST (and SMTP_USER/SMTP_PASSWORD if required).")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user, password = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD")

    def send(msg):
        with smtplib.SMTP(host, port, timeout=30) as s:
            s.starttls()
            if user:
                s.login(user, password or "")
            s.send_message(msg)
    return send


def run(df, out_dir=OUT_DIR, contacts=None, send=None, sender=DEFAULT_SENDER, now=None):
    """Draft (and optionally send) escalation emails; log the rest.

    send: None for a dry run, or a callable taking an EmailMessage.
    Returns a dict with counts and output paths.
    """
    contacts = contacts or load_contacts()
    now = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    out_dir = Path(out_dir)
    outbox = out_dir / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    escalated, rest = split_orders(df)

    dispatch = []
    for o in escalated.to_dict("records"):
        for msg in build_emails(o, contacts, sender):
            role = msg["X-Recipient-Role"]
            path = outbox / f"{o['Order_ID']}_{role}.eml"
            path.write_bytes(bytes(msg))
            if send is None:
                status = "drafted"
            elif is_placeholder(msg["To"]):
                status = "skipped: no real address"
            else:
                try:
                    send(msg)
                    status = "sent"
                except Exception as exc:  # keep going; record the failure
                    status = f"failed: {exc}"
            dispatch.append({"logged_at": now, "Order_ID": o["Order_ID"], "Risk_Category": o["Risk_Category"],
                             "Risk_Score": int(o["Risk_Score"]), "recipient_role": role, "to": msg["To"],
                             "subject": msg["Subject"], "status": status, "draft": str(path.relative_to(out_dir))})

    dispatch_path = out_dir / "escalation_dispatch_log.csv"
    pd.DataFrame(dispatch, columns=["logged_at", "Order_ID", "Risk_Category", "Risk_Score", "recipient_role",
                                    "to", "subject", "status", "draft"]).to_csv(dispatch_path, index=False)

    rest_log = rest[["Order_ID", "Delivery_person_ID", "City", "Weather_conditions", "Road_traffic_density",
                     "Festival", "Predicted_ETA_min", "Estimated_Arrival", "Risk_Score", "Risk_Category",
                     "Risk_Drivers"]].copy()
    rest_log.insert(0, "logged_at", now)
    rest_log["action"] = "No escalation - monitor only"
    rest_path = out_dir / "non_escalated_orders.log.csv"
    rest_log.to_csv(rest_path, index=False, quoting=csv.QUOTE_MINIMAL)

    return {"escalated": len(escalated), "logged": len(rest), "emails": len(dispatch),
            "sent": sum(d["status"] == "sent" for d in dispatch),
            "dispatch_log": dispatch_path, "rest_log": rest_path, "outbox": outbox}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, default=SCORED_PATH)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--send", action="store_true", help="deliver emails via SMTP (default: draft only)")
    args = parser.parse_args()

    sender = os.environ.get("SMTP_FROM", DEFAULT_SENDER)
    result = run(pd.read_csv(args.input), args.out_dir, send=smtp_sender() if args.send else None, sender=sender)
    mode = "sent" if args.send else "drafted (dry run, nothing sent)"
    print(f"Escalated orders: {result['escalated']} -> {result['emails']} emails {mode}; "
          f"{result['sent']} delivered")
    print(f"Other orders logged: {result['logged']} -> {result['rest_log'].relative_to(ROOT)}")
    print(f"Drafts: {result['outbox'].relative_to(ROOT)}  |  Dispatch log: {result['dispatch_log'].relative_to(ROOT)}")


if __name__ == "__main__":
    main()
