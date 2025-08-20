from fastapi import APIRouter
from app.domain.schemas import PaymentWebhook
from app.infrastructure.db import SessionLocal
from app.domain.models import Sale, PaymentStatus

router = APIRouter()

@router.post("/webhook")
def payment_webhook(payload: PaymentWebhook):
    # Idempotência simples: atualizar se existir e status mudou
    with SessionLocal() as db:
        sale = db.query(Sale).filter(Sale.payment_code == payload.paymentCode).first()
        if not sale:
            return {"status": "ignored"}
        desired = PaymentStatus.PAID if payload.status.upper() == "PAID" else PaymentStatus.CANCELED
        if sale.payment_status != desired:
            sale.payment_status = desired
            db.add(sale)
            db.commit()
        return {"status": sale.payment_status}
