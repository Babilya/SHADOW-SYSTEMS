from sqlalchemy.orm import Session
from database.models import User, Application, Key, Project
from datetime import datetime, timedelta

class UserCRUD:
    @staticmethod
    def get_or_create(db: Session, telegram_id: str, username: str, first_name: str):
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            db.add(user)
            db.commit()
        return user

class ApplicationCRUD:
    @staticmethod
    def create(db: Session, **kwargs):
        app = Application(**kwargs)
        db.add(app)
        db.commit()
        return app
    
    @staticmethod
    def get_by_id(db: Session, app_id: int):
        return db.query(Application).filter(Application.id == app_id).first()

class KeyCRUD:
    @staticmethod
    def create(db: Session, code: str, tariff: str, key_type: str, expires_at: datetime):
        key = Key(code=code, tariff=tariff, key_type=key_type, expires_at=expires_at)
        db.add(key)
        db.commit()
        return key
    
    @staticmethod
    def get_by_code(db: Session, code: str):
        return db.query(Key).filter(Key.code == code).first()

class ProjectCRUD:
    @staticmethod
    def create(db: Session, **kwargs):
        project = Project(**kwargs)
        db.add(project)
        db.commit()
        return project
    
    @staticmethod
    def get_by_leader(db: Session, leader_id: str):
        return db.query(Project).filter(Project.leader_id == leader_id).first()
