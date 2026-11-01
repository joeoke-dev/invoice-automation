"""The Receipt model: one invoice, its line items, and its total."""

import pandas as pd


class Receipt:
    def __init__(self, invoice_no, customer_id, date, mall, payment_method, email=None):
        self.invoice_no = invoice_no
        self.customer_id = customer_id
        self.date = date
        self.mall = mall
        self.payment_method = payment_method
        self.email = email
        self.items = []  # list of (category, quantity, price)

    def add_item(self, category, quantity, price):
        self.items.append((category, quantity, price))

    def total(self):
        return sum(qty * price for _, qty, price in self.items)

    @property
    def date_str(self):
        """Formatted date, or a placeholder if the date failed to parse."""
        if pd.isna(self.date):
            return "Unknown date"
        return f"{self.date:%d %b %Y}"

    def __str__(self):
        lines = [
            f"Receipt {self.invoice_no} | {self.date_str}",
            f"Customer: {self.customer_id} | Mall: {self.mall}",
            f"Paid by: {self.payment_method}",
        ]
        for category, qty, price in self.items:
            lines.append(f"  {category} x{qty} @ {price:.2f} = {qty * price:.2f}")
        lines.append(f"  TOTAL: {self.total():.2f}")
        return "\n".join(lines)
