import logging
from typing import Optional, List
from sqlmodel import Session, select, func
from database.models import User, UserRole, LicensePlan
from .base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User model operations"""
    
    def __init__(self, session: Session):
        super().__init__(session, User)
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        try:
            statement = select(User).where(User.telegram_id == telegram_id)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            raise
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            statement = select(User).where(User.username == username)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            raise
    
    async def get_total_users_count(self) -> int:
        """Get total number of users"""
        try:
            statement = select(func.count(User.id))
            result = await self.session.exec(statement)
            return result.scalar_one_or_none() or 0
        except Exception as e:
            logger.error(f"Error counting total users: {e}")
            raise
    
    async def get_users_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role"""
        try:
            statement = select(User).where(User.role == role).offset(skip).limit(limit)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting users by role {role}: {e}")
            raise
