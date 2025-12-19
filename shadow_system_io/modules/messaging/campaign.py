import logging
import asyncio
import uuid
from datetime import datetime, timedelta
from database.crud import (
    create_campaign, update_campaign_status, create_delivery_log
)

logger = logging.getLogger(__name__)

class CampaignManager:
    """Менеджер кампаній з розсилками"""
    
    def __init__(self):
        self.active_campaigns = {}
        self.rate_limiter = {}
    
    async def create_campaign(self, project_id: str, name: str, creator_id: int,
                             recipients: list, messages: list, schedule: dict = None):
        """Створити нову кампанію"""
        campaign_id = f"camp_{uuid.uuid4().hex[:12]}"
        
        campaign_data = {
            "id": campaign_id,
            "project_id": project_id,
            "name": name,
            "creator_id": creator_id,
            "recipients": recipients,
            "messages": messages,
            "schedule": schedule or {"type": "immediate"},
            "stats": {"sent": 0, "delivered": 0, "failed": 0}
        }
        
        try:
            await create_campaign(
                campaign_data["id"],
                project_id,
                name,
                creator_id,
                recipients,
                messages,
                schedule
            )
            
            self.active_campaigns[campaign_id] = campaign_data
            logger.info(f"✅ Campaign created: {campaign_id}")
            
            return campaign_id
        except Exception as e:
            logger.error(f"❌ Campaign creation failed: {e}")
            return None
    
    async def send_campaign_messages(self, campaign_id: str, bot_ids: list):
        """Відправити повідомлення кампанії"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            logger.error(f"Campaign not found: {campaign_id}")
            return
        
        await update_campaign_status(campaign_id, "running")
        logger.info(f"🚀 Starting campaign: {campaign_id}")
        
        for recipient in campaign["recipients"]:
            for bot_id in bot_ids:
                # Перевірка rate limit
                if not self._check_rate_limit(bot_id):
                    await asyncio.sleep(2)
                    continue
                
                # Mock відправка повідомлення
                success = True  # В реальності бути перевіркою Telegram API
                
                await create_delivery_log(
                    campaign_id,
                    bot_id,
                    "chat",
                    str(recipient),
                    success,
                    None if success else "Failed"
                )
                
                campaign["stats"]["sent"] += 1
                if success:
                    campaign["stats"]["delivered"] += 1
                
                await asyncio.sleep(0.5)  # Затримка між повідомленнями
        
        await update_campaign_status(campaign_id, "completed")
        logger.info(f"✅ Campaign completed: {campaign_id}")
    
    def _check_rate_limit(self, bot_id: str) -> bool:
        """Перевірка rate limit для бота"""
        now = datetime.now()
        
        if bot_id not in self.rate_limiter:
            self.rate_limiter[bot_id] = []
        
        # Очистити старі записи (старше 1 хвилини)
        self.rate_limiter[bot_id] = [
            t for t in self.rate_limiter[bot_id]
            if (now - t).seconds < 60
        ]
        
        # Обмеження 10 повідомлень на хвилину
        if len(self.rate_limiter[bot_id]) >= 10:
            return False
        
        self.rate_limiter[bot_id].append(now)
        return True

campaign_manager = CampaignManager()
