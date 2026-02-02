from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceOut, InvoiceUpdate
from app.crud.invoice import create_invoice, get_invoices, get_invoice, update_invoice_status
from app.core.security import get_current_user
from app.models.user import User
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import qrcode

router = APIRouter()

@router.post("/", response_model=InvoiceOut)
def create_new_invoice(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_invoice(db, invoice_data, current_user.id)

@router.get("/", response_model=list[InvoiceOut])
def list_invoices(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_invoices(db, current_user.id)

@router.get("/{invoice_id}", response_model=InvoiceOut)
def retrieve_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    return invoice

@router.patch("/{invoice_id}")
def mark_status(invoice_id: int, update: InvoiceUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = update_invoice_status(db, invoice_id, update.status, current_user.id)
    if not invoice:
        raise HTTPException(404)
    return {"status": "updated"}


@router.get("/{invoice_id}/pdf")
def download_pdf(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Invoice {invoice.invoice_number}")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Client: {invoice.client_name}")
    y -= 18
    c.drawString(50, y, f"Issue date: {invoice.issue_date}")
    y -= 18
    c.drawString(50, y, f"Due date: {invoice.due_date}")
    y -= 25
    c.drawString(50, y, f"Currency: {invoice.currency}")
    y -= 18
    c.drawString(50, y, f"Subtotal: {invoice.subtotal}")
    y -= 18
    c.drawString(50, y, f"Tax: {invoice.tax_amount}")
    y -= 18
    c.drawString(50, y, f"Total: {invoice.total}")
    y -= 30
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Items:")
    y -= 20
    c.setFont("Helvetica", 11)
    for item in invoice.items:
        c.drawString(60, y, f"{item.description} x{item.quantity} @ {item.unit_price} = {item.line_total}")
        y -= 16
        if y < 100:
            c.showPage()
            y = height - 50
    c.showPage()
    c.save()
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"})


@router.get("/{invoice_id}/qrcode")
def invoice_qr(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    payment_payload = f"invoice:{invoice.invoice_number}|amount:{invoice.total}|currency:{invoice.currency}"
    img = qrcode.make(payment_payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png", headers={"Content-Disposition": f"inline; filename=invoice_{invoice.invoice_number}_qr.png"})


@router.post("/{invoice_id}/email")
def email_invoice(
    invoice_id: int,
    to: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(404, "Invoice not found")
    # Stub: in production integrate with SendGrid/SMTP. For now just acknowledge.
    return {"status": "queued", "to": to, "note": "Email send stubbed; integrate with SendGrid or SMTP."}
