"""Invoice automation: CSV data -> receipts -> PDFs -> emails.

By default this is a DRY RUN: PDFs are created, but no emails are sent.
Add --send to actually send emails.

Examples
--------
python main.py --sales data/sample_sales.csv --customers data/sample_customers.csv \
               --emails data/sample_emails.csv
python main.py ... --send --test-recipient you@example.com
"""

import argparse
import time
from pathlib import Path

import pandas as pd

from data_loader import build_receipts, load_orders
from emailer import get_credentials, send_receipt, valid_email
from pdf_builder import create_pdf


def parse_args():
    p = argparse.ArgumentParser(description="Generate and email PDF receipts.")
    p.add_argument("--sales", required=True, help="Path to the sales CSV")
    p.add_argument("--customers", required=True, help="Path to the customers CSV")
    p.add_argument("--emails", help="Optional CSV with customer_id and email columns")
    p.add_argument("--output", default="output", help="Folder for PDFs and the send log")
    p.add_argument("--limit", type=int, help="Only process the first N invoices")
    p.add_argument("--send", action="store_true", help="Actually send emails (default: dry run)")
    p.add_argument("--test-recipient", help="Send every email to this address instead")
    p.add_argument("--delay", type=float, default=2.0, help="Seconds to wait between emails")
    return p.parse_args()


def load_already_sent(log_file):
    if not log_file.exists():
        return set()
    log = pd.read_csv(log_file, dtype={"invoice_no": str})
    return set(log.loc[log["status"] == "sent", "invoice_no"])


def main():
    args = parse_args()
    output = Path(args.output)
    pdf_folder = output / "pdfs"
    log_file = output / "send_log.csv"
    output.mkdir(parents=True, exist_ok=True)

    df = load_orders(args.sales, args.customers, args.emails, args.limit)
    receipts = build_receipts(df)
    print(f"Built {len(receipts)} receipts.")

    pdf_paths = [create_pdf(r, pdf_folder) for r in receipts]
    print(f"Created {len(pdf_paths)} PDFs in {pdf_folder}/")

    sender = password = None
    if args.send:
        sender, password = get_credentials()

    already_sent = load_already_sent(log_file)
    results = []

    for receipt, pdf_path in zip(receipts, pdf_paths):
        invoice_no = str(receipt.invoice_no)
        to_address = args.test_recipient or receipt.email

        if invoice_no in already_sent:
            results.append((invoice_no, to_address, "skipped: already sent"))
            continue
        if not valid_email(to_address):
            results.append((invoice_no, to_address, "skipped: missing/invalid email"))
            continue
        if not args.send:
            results.append((invoice_no, to_address, "dry run"))
            continue

        try:
            send_receipt(receipt, pdf_path, to_address, sender, password)
            results.append((invoice_no, to_address, "sent"))
        except Exception as e:  # keep going if one email fails
            results.append((invoice_no, to_address, f"failed: {e}"))
        time.sleep(args.delay)

    new_log = pd.DataFrame(results, columns=["invoice_no", "email", "status"])
    new_log.to_csv(log_file, mode="a", header=not log_file.exists(), index=False)

    print("\nSummary:")
    print(new_log["status"].value_counts().to_string())
    if not args.send:
        print("\nDry run only. Add --send to email the receipts.")


if __name__ == "__main__":
    main()
