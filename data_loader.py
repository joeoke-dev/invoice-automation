"""Load the CSV files, merge them, and turn the rows into Receipt objects."""

import pandas as pd

from receipt import Receipt

SALES_COLUMNS = {
    "invoice_no", "customer_id", "category",
    "quantity", "price", "invoice_date", "shopping_mall",
}
CUSTOMER_COLUMNS = {"customer_id", "gender", "age", "payment_method"}


def _check_columns(df, required, name):
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} is missing columns: {sorted(missing)}")


def load_orders(sales_path, customers_path, emails_path=None, limit=None):
    """Return one merged DataFrame (one row per sold item).

    emails_path is optional: a CSV with customer_id and email columns.
    limit keeps only the first N invoices, which is handy while testing.
    """
    sales = pd.read_csv(sales_path)
    customers = pd.read_csv(customers_path)
    _check_columns(sales, SALES_COLUMNS, "Sales file")
    _check_columns(customers, CUSTOMER_COLUMNS, "Customer file")

    df = sales.merge(customers, on="customer_id", how="left")

    if emails_path:
        emails = pd.read_csv(emails_path)
        _check_columns(emails, {"customer_id", "email"}, "Emails file")
        emails = emails.drop_duplicates(subset="customer_id")
        df = df.merge(emails, on="customer_id", how="left")
    else:
        df["email"] = None

    df["invoice_date"] = pd.to_datetime(df["invoice_date"], dayfirst=True, errors="coerce")

    if limit:
        keep = df["invoice_no"].drop_duplicates().head(limit)
        df = df[df["invoice_no"].isin(keep)]

    return df


def build_receipts(df):
    """Group rows by invoice number and build one Receipt per invoice."""
    receipts = []
    for invoice_no, group in df.groupby("invoice_no", sort=False):
        first = group.iloc[0]
        receipt = Receipt(
            invoice_no,
            first["customer_id"],
            first["invoice_date"],
            first["shopping_mall"],
            first["payment_method"],
            first["email"],
        )
        for _, row in group.iterrows():
            receipt.add_item(row["category"], int(row["quantity"]), float(row["price"]))
        receipts.append(receipt)
    return receipts
