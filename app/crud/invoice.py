from sqlalchemy.orm import Session
from app.models.invoice import Invoice, InvoiceItem
from app.schemas.invoice import InvoiceCreate
from app.crud.tax_config import get_default_tax_rate
from app.crud.company_profile import get_or_create_profile
from decimal import Decimal

def create_invoice(db: Session, invoice_data: InvoiceCreate, owner_id: int):
    # determine tax rate: prefer payload, else user default if set
    tax_rate = invoice_data.tax_rate
    if tax_rate is None:
        default_rate = get_default_tax_rate(db, owner_id)
        if default_rate is not None:
            tax_rate = Decimal(str(default_rate))

    subtotal = Decimal("0")
    for item in invoice_data.items:
        line_total = item.quantity * item.unit_price
        subtotal += line_total

    tax_amount = Decimal("0")
    if tax_rate:
        tax_amount = subtotal * (tax_rate / Decimal("100"))

    total = subtotal + tax_amount

    invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        due_date=invoice_data.due_date,
        client_name=invoice_data.client_name,
        client_email=invoice_data.client_email,
        currency=invoice_data.currency,
        subtotal=subtotal,
        tax_amount=tax_amount,
        total=total,
        owner_id=owner_id
    )
    # apply optional tax labels/notes (from payload or company profile defaults)
    profile = get_or_create_profile(db, owner_id)
    invoice.tax_label = invoice_data.tax_label or profile.tax_label
    invoice.tax_note = invoice_data.tax_note or profile.tax_note
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    for item in invoice_data.items:
        db_item = InvoiceItem(
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.quantity * item.unit_price,
            invoice_id=invoice.id,
            owner_id=owner_id
        )
        db.add(db_item)
    db.commit()
    return invoice

def get_invoices(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return db.query(Invoice).filter(Invoice.owner_id == owner_id).offset(skip).limit(limit).all()

def get_invoice(db: Session, invoice_id: int, owner_id: int):
    return db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.owner_id == owner_id).first()

def update_invoice_status(db: Session, invoice_id: int, status: str, owner_id: int):
    invoice = get_invoice(db, invoice_id, owner_id)
    if invoice:
        invoice.status = status
        db.commit()
        db.refresh(invoice)
    return invoice
