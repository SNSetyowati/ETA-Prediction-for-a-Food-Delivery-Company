# Escalation Email Trial Report

**Date:** 27 September 2026
**Scope:** One live trial of the escalation emails from `src/notify.py`, sent through Gmail
**Result:** All 3 emails (CS lead, customer, driver) were accepted by Gmail for delivery

---

## 1. Purpose

Until now the escalation flow only produced `.eml` drafts. This trial checks that the three
emails for a high-risk order can be sent through a real mailbox and that their content reads
correctly to each recipient. It is a trial, not a go-live. The real CS lead, customers and
drivers were not contacted.

## 2. Setup

| Item | Value |
|---|---|
| Input | `outputs/active_deliveries_ZC_predicted.csv` (batch ZC, 50 active orders) |
| Escalation rule | Risk category High or Critical (14 orders in batch ZC, 0 Critical) |
| Trial order | **ZC-0040**, first in the escalation queue (highest risk score, then longest ETA) |
| Email content | Built by `notify.build_emails()`, the same code that writes the drafts |
| Channel | Gmail connector, sent from and to the project owner's Gmail account |
| Recipients | All three roles routed to one address (`nugrahenis@gmail.com`) |
| Trial markers | Subject prefix `[TRIAL][<role>]`, plus a footer line noting the routing |

### Trial order: ZC-0040

| Field | Value |
|---|---|
| City | Metropolitan |
| Weather | Fog (Adverse) |
| Road traffic | Jam (Severe) |
| Festival / event | Normal Day |
| Multiple deliveries | 1 |
| Risk score / category | 60 / High |
| Risk drivers | Weather: Fog; Traffic: Jam; Multiple deliveries: 1 |
| Ordered / picked up | 21:35 / 21:40 |
| Predicted ETA | 39.7 min from pickup |
| Estimated arrival | 22:20 |
| Distance | 10.6 km, heading north-east |
| Driver | VADRES20DEL01 (scooter) |

## 3. Results

| # | Role | Subject | Gmail message ID | Status |
|---|---|---|---|---|
| 1 | CS lead | [TRIAL][CS Lead] [HIGH] Delivery risk alert - ZC-0040 (Metropolitian) | `1a0e1a7b1841d320` | Accepted by Gmail |
| 2 | Customer | [TRIAL][Customer] Update on your order ZC-0040: new estimated arrival 22:20 | `1a0e1a7b2552a41f` | Accepted by Gmail |
| 3 | Driver | [TRIAL][Driver] [HIGH] Delay risk on ZC-0040 - route advice | `1a0e1a7b2439dfe7` | Accepted by Gmail |

The send log is in `outputs/notifications/trial_send_log.csv`.

**Verification limit:** Gmail returned a message ID for each email, which means it accepted
them for delivery. The Gmail connector only has permission to send, not to read, so inbox
arrival could not be checked from this session. Please confirm that the three `[TRIAL]`
emails are in the inbox.

## 4. Content review

**CS lead alert:** complete. It shows the risk score, the three risk drivers, weather, traffic,
festival status, predicted ETA with arrival time, order and pickup times, driver and vehicle,
and distance. It also lists suggested actions.

**Customer notification:** gives the reason in plain words ("heavy traffic and fog weather"),
the new arrival time (22:20), and says the ETA counts from pickup at 21:40. It shows no internal
data: no risk score, no driver ID. The tone is apologetic and short.

**Driver alert:** gives conditions, predicted ETA, trip length and heading, four route tips
(jammed traffic, fog, carrying another order, long trip) and a Google Maps directions link
from the restaurant to the customer.

## 5. Findings

| # | Finding | Impact | Suggested fix |
|---|---|---|---|
| 1 | The CS lead subject shows the city as "Metropolitian", a spelling error in the source data | Looks unprofessional | Map "Metropolitian" to "Metropolitan" in the email templates (the dashboard already does this) |
| 2 | Wording "1 other order(s)" in the CS lead and driver emails | Minor readability | Use singular/plural wording |
| 3 | Times show seconds ("21:35:00 / 21:40:00") in the CS lead email | Minor readability | Format as HH:MM |
| 4 | Route advice is rule-based; the Maps link uses `travelmode=driving` | Two-wheelers may get a car route | Acceptable for a trial; consider a two-wheeler routing API later |
| 5 | Gmail connector cannot read the inbox | Delivery cannot be confirmed automatically | Grant read scope, or confirm by hand |
| 6 | In the trial, all three roles go to one inbox | Real routing not yet tested | Fill `data/raw/contacts.csv` and `CS_LEAD_EMAIL` before go-live |

None of these findings block the flow. The emails were built, sent and accepted without errors.

## 6. Recommendations before go-live

1. Fix findings 1-3 in the `src/notify.py` templates and rerun the tests.
2. Add real recipient addresses in `data/raw/contacts.csv` (`Order_ID, customer_email, driver_email`) and set `CS_LEAD_EMAIL`.
3. Choose the send channel: SMTP (`python src/notify.py --send` with `SMTP_*` settings) or a Gmail/n8n workflow.
4. Run one more trial with real internal addresses for the CS lead and a test driver before emailing customers.
5. Keep the dispatch log (`escalation_dispatch_log.csv`) as the audit trail for every send.
