"""Estimated arrival clock time for an order.

Historical Time_taken (min) is measured from pickup, not from order time:
999 of 40,088 historical rows have Time_taken shorter than the order-to-pickup
wait, which is impossible if it counted from the order. So the arrival time is
pickup time + predicted ETA.
"""
import pandas as pd


def estimated_arrival(order_date, time_ordered, time_picked, eta_min):
    """Return arrival as 'HH:MM' strings, rounded to the nearest minute."""
    date = pd.to_datetime(order_date.astype(str))
    ordered = pd.to_timedelta(time_ordered.astype(str))
    picked = pd.to_timedelta(time_picked.astype(str))
    # Pickup earlier on the clock than the order means it happened after midnight.
    picked = picked.where(picked >= ordered, picked + pd.Timedelta(days=1))
    arrival = date + picked + pd.to_timedelta(eta_min, unit="m")
    return arrival.dt.round("min").dt.strftime("%H:%M")
