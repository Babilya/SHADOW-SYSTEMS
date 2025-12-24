import logging
from typing import TypeVar, Generic, Optional, List
from sqlmodel import Session, select

T = TypeVar('T')
logger = logging.getLogger(__name__)


class BaseRepository(Generic[T]):
    """Base repository for common CRUD operations"""
    
    def __init__(self, session: Session, model: type):
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID"""
        try:
            statement = select(self.model).where(self.model.id == id)
            result = await self.session.exec(statement)
            return result.first()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} by ID {id}: {e}")
            raise
    
    async def create(self, obj: T) -> T:
        """Create new entity"""
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    async def update(self, obj: T) -> T:
        """Update entity"""
        try:
            self.session.add(obj)
            await self.session.commit()
            await self.session.refresh(obj)
            return obj
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating {self.model.__name__}: {e}")
            raise
    
    async def delete(self, id: int) -> bool:
        """Delete entity by ID"""
        try:
            obj = await self.get_by_id(id)
            if obj:
                await self.session.delete(obj)
                await self.session.commit()
                return True
            return False
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {id}: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        try:
            statement = select(self.model).offset(skip).limit(limit)
            result = await self.session.exec(statement)
            return result.all()
        except Exception as e:
            logger.error(f"Error getting all {self.model.__name__}: {e}")
            raise
