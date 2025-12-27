"""
Background Tasks Manager for heavy operations
Prevents blocking the event loop for OSINT and other long-running tasks
"""
import asyncio
import logging
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BackgroundTask:
    task_id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    user_id: Optional[int] = None


class BackgroundTaskManager:
    """Manages background tasks without blocking the event loop"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.tasks: Dict[str, BackgroundTask] = {}
        self._task_counter = 0
        self._semaphore = asyncio.Semaphore(max_workers)
        self._running_tasks: Dict[str, asyncio.Task] = {}
    
    def _generate_task_id(self) -> str:
        self._task_counter += 1
        return f"task_{self._task_counter}_{datetime.now().timestamp():.0f}"
    
    async def submit(
        self, 
        name: str, 
        coro: Callable, 
        *args, 
        user_id: Optional[int] = None,
        callback: Optional[Callable] = None,
        **kwargs
    ) -> str:
        """Submit a coroutine to run in the background"""
        task_id = self._generate_task_id()
        
        bg_task = BackgroundTask(
            task_id=task_id,
            name=name,
            user_id=user_id
        )
        self.tasks[task_id] = bg_task
        
        async def run_task():
            async with self._semaphore:
                bg_task.status = TaskStatus.RUNNING
                bg_task.started_at = datetime.now()
                
                try:
                    result = await coro(*args, **kwargs)
                    bg_task.result = result
                    bg_task.status = TaskStatus.COMPLETED
                    
                    if callback:
                        await callback(task_id, result)
                        
                except asyncio.CancelledError:
                    bg_task.status = TaskStatus.CANCELLED
                    raise
                except Exception as e:
                    bg_task.error = str(e)
                    bg_task.status = TaskStatus.FAILED
                    logger.error(f"Task {task_id} failed: {e}")
                finally:
                    bg_task.completed_at = datetime.now()
                    self._running_tasks.pop(task_id, None)
        
        asyncio_task = asyncio.create_task(run_task())
        self._running_tasks[task_id] = asyncio_task
        
        logger.info(f"Submitted background task: {task_id} ({name})")
        return task_id
    
    def get_status(self, task_id: str) -> Optional[BackgroundTask]:
        """Get the status of a background task"""
        return self.tasks.get(task_id)
    
    def get_user_tasks(self, user_id: int) -> list:
        """Get all tasks for a specific user"""
        return [t for t in self.tasks.values() if t.user_id == user_id]
    
    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self._running_tasks:
            self._running_tasks[task_id].cancel()
            return True
        return False
    
    def update_progress(self, task_id: str, progress: int):
        """Update the progress of a task (0-100)"""
        if task_id in self.tasks:
            self.tasks[task_id].progress = min(100, max(0, progress))
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove completed tasks older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        
        for task_id, task in self.tasks.items():
            if task.completed_at:
                age = (now - task.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.tasks[task_id]
        
        return len(to_remove)


background_manager = BackgroundTaskManager()


async def run_osint_background(target: str, osint_type: str, user_id: int, callback: Callable = None) -> str:
    """Helper to run OSINT operations in background"""
    from core.osint_engine import osint_engine
    
    async def osint_task():
        if osint_type == "dns":
            return await asyncio.to_thread(osint_engine.dns_lookup, target)
        elif osint_type == "whois":
            return await asyncio.to_thread(osint_engine.whois_lookup, target)
        elif osint_type == "geoip":
            return await asyncio.to_thread(osint_engine.geoip_lookup, target)
        elif osint_type == "email":
            return await asyncio.to_thread(osint_engine.email_verify, target)
        else:
            return {"error": "Unknown OSINT type"}
    
    return await background_manager.submit(
        name=f"OSINT {osint_type}: {target}",
        coro=osint_task,
        user_id=user_id,
        callback=callback
    )


async def run_geo_scan_background(channels: list, user_id: int, callback: Callable = None) -> str:
    """Helper to run geo scanning in background"""
    
    async def geo_task():
        results = []
        for i, channel in enumerate(channels):
            await asyncio.sleep(0.5)
            results.append({
                "channel": channel,
                "coordinates": [],
                "status": "scanned"
            })
            background_manager.update_progress(
                task_id, 
                int((i + 1) / len(channels) * 100)
            )
        return results
    
    task_id = await background_manager.submit(
        name=f"Geo Scan: {len(channels)} channels",
        coro=geo_task,
        user_id=user_id,
        callback=callback
    )
    return task_id
