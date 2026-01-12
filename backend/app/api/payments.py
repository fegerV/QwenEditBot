import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Payment
from ..schemas import PaymentCreate, PaymentCreateResponse, PaymentHistoryResponse, PaymentResponse
from ..services.payment_service import PaymentService
from ..services.users import get_user_by_any_id

logger = logging.getLogger(__name__)

router = APIRouter()

payment_service = PaymentService()


@router.post("/create", response_model=PaymentCreateResponse)
async def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    payment = await payment_service.create_payment(db, payload.user_id, payload.amount)

    return PaymentCreateResponse(
        payment_id=payment.id,
        status=payment.status,
        confirmation_url=payment.confirmation_url,
        amount=int(payment.amount / 100),
        created_at=payment.created_at,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    payment = await payment_service.refresh_payment_status(db, payment)

    return PaymentResponse(
        id=payment.id,
        user_id=payment.user_id,
        type=payment.type,
        status=payment.status,
        amount=int(payment.amount / 100),
        confirmation_url=payment.confirmation_url,
        created_at=payment.created_at,
        paid_at=payment.paid_at,
    )


@router.get("/user/{user_id}", response_model=PaymentHistoryResponse)
async def get_user_payments(
    user_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    user = get_user_by_any_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid user_id")

    query = db.query(Payment).filter(Payment.user_id == user.user_id)
    if status_filter:
        query = query.filter(Payment.status == status_filter)

    total = query.count()
    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()

    items = [
        {
            "id": p.id,
            "amount": int(p.amount / 100),
            "status": p.status,
            "type": p.type,
            "created_at": p.created_at,
            "paid_at": p.paid_at,
        }
        for p in payments
    ]

    return PaymentHistoryResponse(payments=items, total=total, limit=limit, offset=offset)
