"""Turn a Receipt into a PDF file."""

from pathlib import Path

from fpdf import FPDF


def _safe(text):
    """The built-in PDF fonts only support basic Latin characters."""
    return str(text).encode("latin-1", "replace").decode("latin-1")


def _line(pdf, text):
    pdf.cell(0, 7, _safe(text), new_x="LMARGIN", new_y="NEXT")


def create_pdf(receipt, folder):
    """Write the receipt to folder/receipt_<invoice_no>.pdf and return the path."""
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "RECEIPT", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    _line(pdf, f"Invoice no: {receipt.invoice_no}")
    _line(pdf, f"Date: {receipt.date_str}")
    _line(pdf, f"Customer ID: {receipt.customer_id}")
    _line(pdf, f"Shopping mall: {receipt.mall}")
    _line(pdf, f"Payment method: {receipt.payment_method}")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(90, 8, "Category", border=1)
    pdf.cell(30, 8, "Qty", border=1, align="C")
    pdf.cell(35, 8, "Price", border=1, align="R")
    pdf.cell(35, 8, "Subtotal", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    for category, qty, price in receipt.items:
        pdf.cell(90, 8, _safe(category), border=1)
        pdf.cell(30, 8, str(qty), border=1, align="C")
        pdf.cell(35, 8, f"{price:,.2f}", border=1, align="R")
        pdf.cell(35, 8, f"{qty * price:,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(155, 10, "TOTAL", border=1, align="R")
    pdf.cell(35, 10, f"{receipt.total():,.2f}", border=1, align="R", new_x="LMARGIN", new_y="NEXT")

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"receipt_{receipt.invoice_no}.pdf"
    pdf.output(str(path))
    return path
