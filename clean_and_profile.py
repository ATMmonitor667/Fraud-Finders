"""
RingAlert — Data Cleaning Pipeline (Track 02: Fraud Watch)
Run: python clean_and_profile.py
Outputs:
  data/track02_clean.csv  — cleaned, typed, normalised transactions
"""

import pandas as pd

CSV_IN = "data/track02_fraud_watch.csv"
CSV_OUT = "data/track02_clean.csv"


def load_raw(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {path}: {df.shape[0]:,} rows x {df.shape[1]} cols")
    return df


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[\s\-]+", "_", regex=True)
    )
    rename_map = {
        "txn_id": "transaction_id",
    }
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    required = [
        "transaction_id",
        "account_id",
        "counterparty_id",
        "amount",
        "timestamp",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(r"[$,£€\s]", "", regex=True)
        .pipe(pd.to_numeric, errors="coerce")
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["account_open_date"] = pd.to_datetime(df["account_open_date"], errors="coerce")

    for col in [
        "transaction_id",
        "account_id",
        "counterparty_id",
        "merchant_category",
        "device_id",
        "ip_region",
    ]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def drop_bad_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    before = len(df)
    df = df.dropna(subset=["account_id", "counterparty_id", "amount", "timestamp"])
    df = df[df["amount"] > 0]
    df = df[df["account_id"] != df["counterparty_id"]]
    df = df.drop_duplicates(subset=["transaction_id"])
    dropped = before - len(df)
    print(f"Dropped {dropped} rows ({dropped / before * 100:.1f}%)")
    return df, dropped


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("timestamp").reset_index(drop=True)

    df["counterparty_type"] = df["counterparty_id"].str.extract(r"^([A-Z]+)-", expand=False)
    df["is_account_transfer"] = df["counterparty_type"] == "AC"
    df["is_merchant_payment"] = df["counterparty_type"] == "MR"

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["date"] = df["timestamp"].dt.date
    df["late_night"] = df["hour"].between(2, 4)
    df["in_suspect_range"] = df["amount"].between(400, 900)
    df["is_foreign_ip"] = df["ip_region"].isin(["FR", "JP", "UK"])

    df["edge_key"] = df["account_id"] + "->" + df["counterparty_id"]

    df["sender_tx_seq"] = df.groupby("account_id").cumcount() + 1
    prev_ts = df.groupby("account_id")["timestamp"].shift(1)
    df["hours_since_last"] = (
        (df["timestamp"] - prev_ts).dt.total_seconds() / 3600
    ).round(2)

    return df


def main() -> None:
    df = load_raw(CSV_IN)
    df = normalize_columns(df)
    df = coerce_types(df)
    df, _ = drop_bad_rows(df)
    df = engineer_features(df)

    df.to_csv(CSV_OUT, index=False)
    print(f"Saved {CSV_OUT}: {df.shape[0]:,} rows x {df.shape[1]} cols")


if __name__ == "__main__":
    main()
