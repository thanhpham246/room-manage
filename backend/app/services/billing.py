from app.models import Invoice, MeterReading, Payment
from app.repositories.billing import BillingRepository
from app.repositories.contracts import ContractRepository
from app.schemas.billing import InvoiceBatchCreate, InvoiceReadingInput, PaymentCreate
from app.services.errors import ConflictError, NotFoundError


class BillingService:
    def __init__(self, billing: BillingRepository, contracts: ContractRepository) -> None:
        self.billing = billing
        self.contracts = contracts

    def generate_invoices(self, payload: InvoiceBatchCreate) -> list[Invoice]:
        invoices: list[Invoice] = []
        for reading in payload.readings:
            contract = self.contracts.get(reading.contract_id)
            if contract is None or contract.status != "active":
                raise NotFoundError("Active contract not found")
            if self.billing.invoice_exists(contract.id, payload.billing_month):
                raise ConflictError("Invoice already exists for contract and month")

            meter_reading = MeterReading(
                room_id=contract.room_id,
                billing_month=payload.billing_month,
                electricity_previous=reading.electricity_previous,
                electricity_current=reading.electricity_current,
                water_previous=reading.water_previous,
                water_current=reading.water_current,
            )
            self.billing.create_meter_reading(meter_reading)
            invoices.append(self._build_invoice(payload, reading))

        for invoice in invoices:
            self.billing.create_invoice(invoice)
        return self.billing.commit_invoice_batch(invoices)

    def _build_invoice(
        self,
        payload: InvoiceBatchCreate,
        reading: InvoiceReadingInput,
    ) -> Invoice:
        contract = self.contracts.get(reading.contract_id)
        if contract is None:
            raise NotFoundError("Contract not found")
        electricity_amount = (
            reading.electricity_current - reading.electricity_previous
        ) * payload.electricity_unit_price
        water_amount = (reading.water_current - reading.water_previous) * payload.water_unit_price
        total_amount = (
            contract.monthly_rent
            + electricity_amount
            + water_amount
            + payload.fixed_service_amount
            + reading.surcharge_amount
            - reading.discount_amount
        )
        return Invoice(
            contract_id=contract.id,
            room_id=contract.room_id,
            tenant_id=contract.tenant_id,
            billing_month=payload.billing_month,
            rent_amount=contract.monthly_rent,
            electricity_amount=electricity_amount,
            water_amount=water_amount,
            service_amount=payload.fixed_service_amount,
            surcharge_amount=reading.surcharge_amount,
            discount_amount=reading.discount_amount,
            total_amount=total_amount,
            status="unpaid",
        )

    def list_invoices(
        self,
        billing_month,
        status: str | None,
        skip: int,
        limit: int,
    ) -> tuple[list[Invoice], int]:
        return self.billing.list_invoices(
            billing_month=billing_month,
            status=status,
            skip=skip,
            limit=limit,
        )

    def create_payment(self, payload: PaymentCreate) -> Payment:
        invoice = self.billing.get_invoice(payload.invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found")
        if invoice.paid_amount + payload.amount > invoice.total_amount:
            raise ConflictError("Payment exceeds invoice balance")

        payment = Payment(
            invoice_id=payload.invoice_id,
            amount=payload.amount,
            method=payload.method,
            note=payload.note,
        )
        invoice.paid_amount += payload.amount
        if invoice.paid_amount == 0:
            invoice.status = "unpaid"
        elif invoice.paid_amount < invoice.total_amount:
            invoice.status = "partial"
        else:
            invoice.status = "paid"
        return self.billing.create_payment(payment)

    def list_payments(self, skip: int, limit: int) -> tuple[list[Payment], int]:
        return self.billing.list_payments(skip=skip, limit=limit)
