import logging
from typing import Optional
from sqlalchemy.orm import Session
from database.models import User, UserRole
from utils.db import SessionLocal

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def get_user(telegram_id: int) -> Optional[User]:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None) -> User:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if not user:
                user = User(
                    telegram_id=str(telegram_id),
                    username=username or "",
                    first_name=first_name or "",
                    role=UserRole.GUEST
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                logger.info(f"Created new user: {telegram_id} as {UserRole.GUEST}")
            return user
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_user_role(telegram_id: int) -> str:
        user = UserService.get_user(telegram_id)
        if user:
            return user.role
        return UserRole.GUEST
    
    @staticmethod
    def set_user_role(telegram_id: int, role: str) -> bool:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if user:
                user.role = role
                db.commit()
                logger.info(f"Updated role for user {telegram_id} to {role}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error setting user role: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def is_admin(telegram_id: int) -> bool:
        return UserService.get_user_role(telegram_id) == UserRole.ADMIN
    
    @staticmethod
    def is_leader(telegram_id: int) -> bool:
        role = UserService.get_user_role(telegram_id)
        return role in [UserRole.LEADER, UserRole.ADMIN]
    
    @staticmethod
    def is_manager(telegram_id: int) -> bool:
        role = UserService.get_user_role(telegram_id)
        return role in [UserRole.MANAGER, UserRole.LEADER, UserRole.ADMIN]
    
    @staticmethod
    def get_all_users() -> list:
        db = SessionLocal()
        try:
            users = db.query(User).all()
            return users
        finally:
            db.close()
    
    @staticmethod
    def get_users_by_role(role: str) -> list:
        db = SessionLocal()
        try:
            users = db.query(User).filter(User.role == role).all()
            return users
        finally:
            db.close()
    
    @staticmethod
    def activate_key(telegram_id: int, key_code: str) -> tuple:
        from database.models import Key
        db = SessionLocal()
        try:
            key = db.query(Key).filter(Key.code == key_code, Key.is_used == False).first()
            if not key:
                return False, "Ключ не знайдено або вже використано"
            
            user = db.query(User).filter(User.telegram_id == str(telegram_id)).first()
            if not user:
                return False, "Користувача не знайдено"
            
            key.is_used = True
            key.user_id = str(telegram_id)
            
            user.role = UserRole.LEADER
            user.subscription_type = key.tariff
            user.subscription_expires = key.expires_at
            
            db.commit()
            return True, f"Ключ активовано! Тариф: {key.tariff}"
        except Exception as e:
            logger.error(f"Error activating key: {e}")
            db.rollback()
            return False, "Помилка активації ключа"
        finally:
            db.close()

user_service = UserService()
