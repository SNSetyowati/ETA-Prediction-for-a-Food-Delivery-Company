import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import notify  # noqa: E402


def make_order(order_id, category, score, **overrides):
    row = {
        "Order_ID": order_id, "Delivery_person_ID": "BANGRES12DEL02", "City": "Metropolitian",
        "Restaurant_latitude": 12.939496, "Restaurant_longitude": 77.625999,
        "Delivery_location_latitude": 12.959496, "Delivery_location_longitude": 77.645999,
        "Time_Ordered": "20:00:00", "Time_Order_picked": "20:10:00",
        "Weather_conditions": "Fog", "Weather_Label": "Adverse",
        "Road_traffic_density": "Jam", "Traffic_Label": "Severe",
        "Festival": "No", "Festival_Label": "Normal Day",
        "Type_of_vehicle": "motorcycle", "multiple_deliveries": 1, "Distance_km": 3.1,
        "Predicted_ETA_min": 38.4, "Estimated_Arrival": "20:38",
        "Risk_Score": score, "Risk_Category": category,
        "Risk_Drivers": "Weather: Fog; Traffic: Jam; Multiple deliveries: 1",
    }
    row.update(overrides)
    return row


@pytest.fixture
def orders():
    return pd.DataFrame([
        make_order("ZC-1", "Critical", 80, Festival="Yes", Festival_Label="Festival / Event"),
        make_order("ZC-2", "High", 50),
        make_order("ZC-3", "Medium", 30, Weather_conditions="Sunny", Weather_Label="Clear",
                   Road_traffic_density="Medium", Traffic_Label="Moderate"),
        make_order("ZC-4", "Low", 0, Weather_conditions="Sunny", Weather_Label="Clear",
                   Road_traffic_density="Low", Traffic_Label="Smooth", multiple_deliveries=0),
    ])


@pytest.fixture
def contacts():
    return notify.Contacts("lead@zamato.test", {"ZC-1": "cust1@zamato.test"}, {"ZC-1": "drv1@zamato.test"})


def test_split_orders_escalates_only_high_and_critical(orders):
    escalated, rest = notify.split_orders(orders)
    assert list(escalated["Order_ID"]) == ["ZC-1", "ZC-2"]  # highest risk first
    assert set(rest["Risk_Category"]) == {"Medium", "Low"}


def test_three_emails_per_escalated_order(orders, contacts):
    msgs = notify.build_emails(orders.iloc[0].to_dict(), contacts)
    assert [m["X-Recipient-Role"] for m in msgs] == ["cs_lead", "customer", "driver"]
    assert [m["To"] for m in msgs] == ["lead@zamato.test", "cust1@zamato.test", "drv1@zamato.test"]


def test_cs_lead_alert_has_risk_details(orders, contacts):
    body = notify.cs_lead_alert(orders.iloc[0].to_dict(), contacts.cs_lead).get_content()
    for text in ("80 / 100", "Fog", "Jam", "Festival / Event", "20:38"):
        assert text in body


def test_customer_email_hides_internal_risk(orders, contacts):
    msg = notify.customer_notification(orders.iloc[0].to_dict(), "cust1@zamato.test")
    body = msg.get_content()
    assert "20:38" in msg["Subject"] and "20:38" in body
    assert "heavy traffic" in body and "festival" in body
    for internal in ("Risk", "risk", "80", "BANGRES12DEL02"):
        assert internal not in body


def test_driver_alert_contains_route_recommendation(orders, contacts):
    body = notify.driver_alert(orders.iloc[0].to_dict(), "drv1@zamato.test").get_content()
    assert "Route recommendation" in body
    assert "google.com/maps/dir" in body
    assert "jammed" in body and "Fog" in body and "Festival" in body
    assert "deliver ZC-1 first" in body


def test_route_heading_and_sign_flipped_coordinates():
    order = make_order("ZC-9", "High", 50, Restaurant_latitude=-12.9, Restaurant_longitude=-77.6,
                       Delivery_location_latitude=13.0, Delivery_location_longitude=77.6)
    route = notify.route_recommendation(order)
    assert route["heading"] == "north"
    assert "origin=12.900000,77.600000" in route["maps_url"]


def test_dry_run_writes_drafts_and_logs(tmp_path, orders, contacts):
    result = notify.run(orders, tmp_path, contacts=contacts, now=datetime(2026, 9, 26, 12, 0))
    assert result["escalated"] == 2 and result["logged"] == 2 and result["emails"] == 6
    assert result["sent"] == 0
    assert len(list((tmp_path / "outbox").glob("*.eml"))) == 6

    dispatch = pd.read_csv(result["dispatch_log"])
    assert set(dispatch["status"]) == {"drafted"}
    rest = pd.read_csv(result["rest_log"])
    assert list(rest["Order_ID"]) == ["ZC-3", "ZC-4"]
    assert (rest["action"] == "No escalation - monitor only").all()


def test_send_skips_placeholder_addresses(tmp_path, orders, contacts):
    sent = []
    result = notify.run(orders, tmp_path, contacts=contacts, send=sent.append)
    dispatch = pd.read_csv(result["dispatch_log"]).set_index(["Order_ID", "recipient_role"])["status"]
    # ZC-1 has real contacts for everyone; ZC-2 only has the CS lead.
    assert dispatch[("ZC-1", "customer")] == "sent"
    assert dispatch[("ZC-2", "cs_lead")] == "sent"
    assert dispatch[("ZC-2", "customer")] == "skipped: no real address"
    assert dispatch[("ZC-2", "driver")] == "skipped: no real address"
    assert len(sent) == result["sent"] == 4


def test_send_failure_is_logged_not_raised(tmp_path, orders, contacts):
    def broken(msg):
        raise ConnectionError("smtp down")
    result = notify.run(orders, tmp_path, contacts=contacts, send=broken)
    statuses = pd.read_csv(result["dispatch_log"])["status"]
    assert statuses.str.startswith("failed: smtp down").sum() == 4
