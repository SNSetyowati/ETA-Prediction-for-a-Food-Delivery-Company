import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from arrival import estimated_arrival  # noqa: E402

DATE = "2026-09-26"


def arrive(ordered, picked, eta):
    return estimated_arrival(pd.Series([DATE]), pd.Series([ordered]), pd.Series([picked]),
                             pd.Series([eta])).iloc[0]


def test_eta_counts_from_pickup_not_order():
    # ZC-0003: ordered 09:00, picked 09:15, ETA 13.4 min
    assert arrive("09:00:00", "09:15:00", 13.4) == "09:28"


def test_rounds_to_nearest_minute():
    # 21:40 + 39.7 min = 22:19.7 -> 22:20
    assert arrive("21:35:00", "21:40:00", 39.7) == "22:20"


def test_pickup_after_midnight():
    # ZC-0050: ordered 23:55, picked 00:10 the next day, ETA 16.1 min
    assert arrive("23:55:00", "00:10:00", 16.1) == "00:26"


def test_arrival_never_before_pickup_in_outputs():
    root = Path(__file__).resolve().parents[1] / "outputs"
    for name in ("high_critical_orders.csv", "low_medium_orders.csv"):
        df = pd.read_csv(root / name)
        expected = estimated_arrival(pd.Series([DATE] * len(df)), df["Time_Ordered"],
                                     df["Time_Order_picked"], df["Predicted_ETA_min"])
        assert (df["Estimated_Arrival"] == expected).all(), name
