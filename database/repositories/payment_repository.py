import logging
from typing import List, Optional
from sqlmodel import Session, select, func
from database.models import Payment, User
from datetime import datetime
from .base import BaseRepository

logger = logging.getLogger(__name__)


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment model operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, Payment)
    
    async def get_user_payments(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get all payments for user"""
        try:
            statement = select(Payment).where(Payment.user_id == user_id).offset(skip).limit(limit)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting payments for user {user_id}: {e}")
            raise
    
    async def get_by_invoice_id(self, invoice_id: str) -> Optional[Payment]:
        """Get payment by invoice ID"""
        try:
            statement = select(Payment).where(Payment.invoice_id == invoice_id)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting payment by invoice {invoice_id}: {e}")
            raise
    
    async def update_payment_status(self, payment_id: int, new_status: str, transaction_hash: Optional[str] = None) -> Optional[Payment]:
        """Update payment status"""
        try:
            payment = await self.get_by_id(payment_id)
            if payment:
                payment.status = new_status
                if transaction_hash:
                    payment.transaction_hash = transaction_hash
                if new_status == "completed":
                    payment.completed_at = datetime.utcnow()
                return await self.update(payment)
            return None
        except Exception as e:
            logger.error(f"Error updating payment {payment_id}: {e}")
            raise
    
    async def get_total_revenue(self) -> float:
        """Get total revenue from completed payments"""
        try:
            statement = select(func.sum(Payment.amount)).where(Payment.status == "completed")
            result = await self.session.exec(statement)
            return result.scalar_one_or_none() or 0.0
        except Exception as e:
            logger.error(f"Error calculating total revenue: {e}")
            raise
