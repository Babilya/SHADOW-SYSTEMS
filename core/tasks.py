import logging
from celery import Celery
from celery.schedules import crontab
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import REDIS_URL

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    'shadow_system_tasks',
    broker=REDIS_URL or 'redis://localhost:6379/0',
    backend=REDIS_URL or 'redis://localhost:6379/0'
)

# Configure Celery
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,
    beat_schedule={
        'cleanup-osint-data-daily': {
            'task': 'core.tasks.cleanup_osint_data_task',
            'schedule': crontab(hour=3, minute=0),
            'args': (30,),
        },
        'monitor-system-health-every-15-minutes': {
            'task': 'core.tasks.monitor_system_health_task',
            'schedule': crontab(minute='*/15'),
        },
    }
)


def run_async_task(coro):
    """Helper function to run async code in Celery task"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(name='core.tasks.cleanup_osint_data_task', bind=True)
def cleanup_osint_data_task(self, retention_days: int = 30):
    """Clean up expired OSINT data"""
    logger.info(f"Starting cleanup of OSINT data older than {retention_days} days")
    try:
        from database.db import get_sync_session
        from database.repositories.osint_data_repository import OSINTDataRepository
        
        session = get_sync_session()
        repo = OSINTDataRepository(session)
        deleted_count = run_async_task(repo.cleanup_expired_data(retention_days))
        
        logger.info(f"✅ Cleaned up {deleted_count} OSINT data entries")
        return {"status": "completed", "deleted_count": deleted_count}
    except Exception as e:
        logger.error(f"❌ Error in cleanup_osint_data_task: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}


@celery_app.task(name='core.tasks.monitor_system_health_task')
def monitor_system_health_task():
    """Monitor system health"""
    logger.info("Monitoring system health...")
    try:
        from database.db import db_manager
        
        health_ok = run_async_task(db_manager.health_check())
        
        status = "✅ Healthy" if health_ok else "❌ Unhealthy"
        logger.info(f"System health check: {status}")
        return {"status": "completed", "health": health_ok}
    except Exception as e:
        logger.error(f"❌ Error in monitor_system_health_task: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}


@celery_app.task(name='core.tasks.validate_sessions_batch_task', bind=True)
def validate_sessions_batch_task(self, user_id: int, session_file_paths: List[str]):
    """Validate batch of bot sessions"""
    logger.info(f"Starting batch validation for user {user_id} with {len(session_file_paths)} files")
    try:
        # This is a placeholder - implement your session validation logic
        logger.info(f"Batch validation for user {user_id} completed")
        return {"status": "completed", "user_id": user_id, "files_count": len(session_file_paths)}
    except Exception as e:
        logger.error(f"Error in batch validation: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}


@celery_app.task(name='core.tasks.run_campaign_task', bind=True)
def run_campaign_task(self, campaign_id: int, user_id: int):
    """Run campaign"""
    logger.info(f"Starting campaign {campaign_id} for user {user_id}")
    try:
        # This is a placeholder - implement your campaign logic
        logger.info(f"Campaign {campaign_id} started")
        return {"status": "completed", "campaign_id": campaign_id, "user_id": user_id}
    except Exception as e:
        logger.error(f"Error running campaign {campaign_id}: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}
