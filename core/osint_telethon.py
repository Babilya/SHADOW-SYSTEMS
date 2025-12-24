import logging
import json
from typing import List, Dict, Any, Optional
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
import os

logger = logging.getLogger(__name__)


class TelethonOSINT:
    """OSINT operations using Telethon"""
    
    def __init__(self, api_id: int, api_hash: str, session_name: str = "osint_session"):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.client: Optional[TelegramClient] = None
    
    async def connect(self, phone: str) -> bool:
        """Connect to Telegram"""
        try:
            self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
            await self.client.start(phone=phone)
            logger.info(f"✅ Connected as {phone}")
            return True
        except SessionPasswordNeededError:
            logger.warning("2FA password needed")
            return False
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Telegram"""
        try:
            if self.client:
                await self.client.disconnect()
                logger.info("Disconnected from Telegram")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")
    
    async def get_chat_members(self, chat_link: str, limit: int = 1000) -> Dict[str, Any]:
        """Extract chat members"""
        try:
            if not self.client:
                return {"error": "Not connected"}
            
            # Get entity from link
            entity = await self.client.get_entity(chat_link)
            members = []
            
            # Get participants
            async for member in self.client.iterate_participants(entity, limit=limit):
                members.append({
                    "user_id": member.id,
                    "username": member.username,
                    "first_name": member.first_name,
                    "last_name": member.last_name,
                    "is_bot": member.bot,
                    "is_self": member.is_self,
                    "status": str(member.status) if member.status else None
                })
            
            logger.info(f"✅ Extracted {len(members)} members from {chat_link}")
            return {
                "status": "success",
                "chat_link": chat_link,
                "total_members": len(members),
                "members": members
            }
        except Exception as e:
            logger.error(f"❌ Error extracting members: {e}")
            return {"error": str(e)}
    
    async def get_chat_info(self, chat_link: str) -> Dict[str, Any]:
        """Get detailed chat information"""
        try:
            if not self.client:
                return {"error": "Not connected"}
            
            entity = await self.client.get_entity(chat_link)
            full_info = await self.client.get_entity(entity)
            
            info = {
                "entity_id": entity.id,
                "title": getattr(entity, "title", None),
                "description": getattr(entity, "description", None),
                "members_count": getattr(entity, "participants_count", None),
                "is_channel": getattr(entity, "broadcast", False),
                "is_group": getattr(entity, "megagroup", False),
                "verified": getattr(entity, "verified", False),
                "scam": getattr(entity, "scam", False),
                "fake": getattr(entity, "fake", False),
            }
            
            return {
                "status": "success",
                "chat_info": info
            }
        except Exception as e:
            logger.error(f"❌ Error getting chat info: {e}")
            return {"error": str(e)}
    
    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Get user information"""
        try:
            if not self.client:
                return {"error": "Not connected"}
            
            user = await self.client.get_entity(username)
            
            info = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_bot": user.bot,
                "is_verified": getattr(user, "verified", False),
                "is_scam": getattr(user, "scam", False),
                "is_fake": getattr(user, "fake", False),
                "bio": getattr(user, "about", None),
                "status": str(user.status) if user.status else None
            }
            
            return {
                "status": "success",
                "user_info": info
            }
        except Exception as e:
            logger.error(f"❌ Error getting user info: {e}")
            return {"error": str(e)}
    
    async def search_messages(self, chat_link: str, query: str, limit: int = 100) -> Dict[str, Any]:
        """Search messages in chat"""
        try:
            if not self.client:
                return {"error": "Not connected"}
            
            entity = await self.client.get_entity(chat_link)
            messages = []
            
            async for message in self.client.iter_messages(entity, search=query, limit=limit):
                messages.append({
                    "message_id": message.id,
                    "text": message.text[:100] if message.text else None,
                    "sender_id": message.sender_id,
                    "date": message.date.isoformat(),
                    "reply_to": message.reply_to_msg_id if message.reply_to else None
                })
            
            return {
                "status": "success",
                "query": query,
                "total_found": len(messages),
                "messages": messages
            }
        except Exception as e:
            logger.error(f"❌ Error searching messages: {e}")
            return {"error": str(e)}


# Initialize OSINT engine
osint_engine = None


def init_osint(api_id: int, api_hash: str):
    """Initialize OSINT engine"""
    global osint_engine
    osint_engine = TelethonOSINT(api_id, api_hash)
    return osint_engine
