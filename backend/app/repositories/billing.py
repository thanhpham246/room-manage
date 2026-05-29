from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Invoice, MeterReading, Payment


class BillingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_invoice(self, invoice_id: int) -> Invoice | None:
        return self.db.get(Invoice, invoice_id)

    def invoice_exists(self, contract_id: int, billing_month: date) -> bool:
        invoice_id = self.db.scalar(
            select(Invoice.id).where(
                Invoice.contract_id == contract_id,
                Invoice.billing_month == billing_month,
            )
        )
        return invoice_id is not None

    def create_meter_reading(self, reading: MeterReading) -> MeterReading:
        self.db.add(reading)
        return reading

    def create_invoice(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        return invoice

    def commit_invoice_batch(self, invoices: list[Invoice]) -> list[Invoice]:
        self.db.commit()
        for invoice in invoices:
            self.db.refresh(invoice)
        return invoices

    def list_invoices(
        self,
        billing_month: date | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[Invoice], int]:
        query = select(Invoice)
        count_query = select(func.count()).select_from(Invoice)
        if billing_month:
            query = query.where(Invoice.billing_month == billing_month)
            count_query = count_query.where(Invoice.billing_month == billing_month)
        if status:
            query = query.where(Invoice.status == status)
            count_query = count_query.where(Invoice.status == status)
        total = self.db.scalar(count_query) or 0
        items = list(self.db.scalars(query.order_by(Invoice.id).offset(skip).limit(limit)))
        return items, total

    def create_payment(self, payment: Payment) -> Payment:
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def list_payments(self, skip: int = 0, limit: int = 50) -> tuple[list[Payment], int]:
        total = self.db.scalar(select(func.count()).select_from(Payment)) or 0
        query = select(Payment).order_by(Payment.id).offset(skip).limit(limit)
        items = list(self.db.scalars(query))
        return items, total
