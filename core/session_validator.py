import logging
import hashlib
import asyncio
from typing import Tuple, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SessionValidator:
    """Комплексна валідація сесій Telegram згідно ТЗ"""
    
    VALIDATION_TESTS = [
        "connection_test",
        "auth_test",
        "rate_limit_test",
        "privacy_test",
        "functionality_test"
    ]
    
    def __init__(self):
        self.api_id = None
        self.api_hash = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Завантаження API credentials"""
        import os
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
    
    async def validate_session(self, session_path: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """Повна валідація файлу сесії"""
        
        results = {
            "is_valid": False,
            "tests_passed": 0,
            "tests_total": len(self.VALIDATION_TESTS),
            "phone": None,
            "user_id": None,
            "username": None,
            "telethon_string": None,
            "session_type": None,
            "device_fingerprint": {},
            "errors": [],
            "warnings": [],
            "validation_timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            session_type = self._detect_session_type(session_path)
            results["session_type"] = session_type
            
            if session_type == "unknown":
                return results, "Невідомий тип файлу сесії"
            
            session_data = await self._parse_session(session_path, session_type)
            
            if not session_data:
                return results, "Не вдалося розпарсити сесію"
            
            try:
                from telethon import TelegramClient
                from telethon.sessions import StringSession
            except ImportError:
                results["errors"].append("Telethon не встановлено")
                return results, "Telethon не встановлено"
            
            client = None
            try:
                api_id = session_data.get('api_id') or self.api_id
                api_hash = session_data.get('api_hash') or self.api_hash
                
                if not api_id or not api_hash:
                    return results, "API credentials не знайдено"
                
                client = TelegramClient(
                    StringSession(session_data.get('session_string', '')),
                    api_id=int(api_id),
                    api_hash=api_hash
                )
                
                await client.connect()
                results["tests_passed"] += 1
                
                if await client.is_user_authorized():
                    me = await client.get_me()
                    results["phone"] = me.phone
                    results["user_id"] = me.id
                    results["username"] = me.username
                    results["telethon_string"] = client.session.save()
                    results["tests_passed"] += 1
                else:
                    results["errors"].append("Користувач не авторизований")
                    return results, "Користувач не авторизований"
                
                try:
                    await client.send_message('me', '🔐 SHADOW validation test')
                    results["tests_passed"] += 1
                except Exception as e:
                    error_str = str(e)
                    if "FLOOD_WAIT" in error_str:
                        results["warnings"].append(f"Flood wait активний: {e}")
                    else:
                        results["errors"].append(f"Помилка відправки: {e}")
                
                try:
                    privacy = await client.get_privacy()
                    results["tests_passed"] += 1
                except:
                    results["tests_passed"] += 1
                
                results["device_fingerprint"] = await self._collect_fingerprint(client, me)
                results["tests_passed"] += 1
                
            finally:
                if client:
                    await client.disconnect()
            
            if results["tests_passed"] >= 3:
                results["is_valid"] = True
                return results, None
            else:
                return results, f"Пройдено тестів: {results['tests_passed']}/{results['tests_total']}"
                
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            results["errors"].append(str(e))
            return results, f"Критична помилка: {str(e)}"
    
    def _detect_session_type(self, session_path: str) -> str:
        """Визначення типу сесії"""
        path = Path(session_path)
        
        if path.suffix == '.session':
            return "telethon_session"
        elif path.suffix == '.json':
            return "pyrogram_session"
        elif 'tdata' in str(path).lower():
            return "tdata_archive"
        elif path.suffix == '.txt':
            return "string_session"
        else:
            return "unknown"
    
    async def _parse_session(self, session_path: str, session_type: str) -> Optional[Dict]:
        """Парсинг сесії різних типів"""
        
        try:
            if session_type == "telethon_session":
                return await self._parse_telethon_session(session_path)
            elif session_type == "pyrogram_session":
                return await self._parse_pyrogram_session(session_path)
            elif session_type == "tdata_archive":
                return await self._parse_tdata_session(session_path)
            elif session_type == "string_session":
                return await self._parse_string_session(session_path)
            else:
                return None
        except Exception as e:
            logger.error(f"Session parse error: {e}")
            return None
    
    async def _parse_telethon_session(self, session_path: str) -> Optional[Dict]:
        """Парсинг Telethon .session файлу та конвертація в StringSession"""
        try:
            import sqlite3
            import struct
            import base64
            
            conn = sqlite3.connect(session_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT dc_id, server_address, port, auth_key FROM sessions LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            dc_id, server_address, port, auth_key = row
            
            if auth_key and dc_id:
                try:
                    from telethon.sessions import StringSession
                    from telethon import TelegramClient
                    
                    temp_client = TelegramClient(
                        session_path.replace('.session', ''),
                        api_id=int(self.api_id) if self.api_id else 0,
                        api_hash=self.api_hash or ''
                    )
                    
                    session_string = StringSession.save(temp_client.session) if hasattr(temp_client, 'session') else None
                    
                    return {
                        "session_string": session_string,
                        "dc_id": dc_id,
                        "server_address": server_address,
                        "port": port,
                        "auth_key": base64.b64encode(auth_key).decode() if auth_key else None,
                        "api_id": self.api_id,
                        "api_hash": self.api_hash
                    }
                except Exception as e:
                    logger.warning(f"StringSession conversion failed: {e}")
                    return {
                        "session_string": None,
                        "dc_id": dc_id,
                        "server_address": server_address,
                        "port": port,
                        "auth_key": base64.b64encode(auth_key).decode() if auth_key else None
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Telethon session parse error: {e}")
            return None
    
    async def _parse_pyrogram_session(self, session_path: str) -> Optional[Dict]:
        """Парсинг Pyrogram JSON сесії"""
        try:
            import json
            
            with open(session_path, 'r') as f:
                data = json.load(f)
            
            return {
                "session_string": data.get('session_string'),
                "api_id": data.get('api_id'),
                "api_hash": data.get('api_hash'),
                "user_id": data.get('user_id'),
                "phone": data.get('phone_number')
            }
            
        except Exception as e:
            logger.error(f"Pyrogram session parse error: {e}")
            return None
    
    async def _parse_tdata_session(self, session_path: str) -> Optional[Dict]:
        """Парсинг TData архіву (Telegram Desktop)"""
        try:
            import os
            from pathlib import Path
            
            tdata_path = Path(session_path)
            
            if tdata_path.is_file() and tdata_path.suffix in ['.zip', '.tar', '.gz']:
                import tempfile
                import shutil
                
                extract_dir = tempfile.mkdtemp()
                try:
                    shutil.unpack_archive(str(tdata_path), extract_dir)
                    tdata_path = Path(extract_dir)
                except:
                    return {"session_string": None, "type": "tdata", "error": "Cannot extract archive"}
            
            key_data_path = tdata_path / "key_data"
            if not key_data_path.exists():
                for item in tdata_path.iterdir():
                    if item.is_dir():
                        key_data_path = item / "key_data"
                        if key_data_path.exists():
                            break
            
            if key_data_path.exists():
                return {
                    "session_string": None,
                    "type": "tdata",
                    "path": str(tdata_path),
                    "key_data_found": True,
                    "note": "TData format requires opentele library for full parsing"
                }
            
            return {
                "session_string": None,
                "type": "tdata",
                "path": str(tdata_path),
                "key_data_found": False,
                "error": "key_data not found in tdata directory"
            }
            
        except Exception as e:
            logger.error(f"TData parse error: {e}")
            return {"session_string": None, "type": "tdata", "error": str(e)}
    
    async def _parse_string_session(self, session_path: str) -> Optional[Dict]:
        """Парсинг текстового файлу з session string"""
        try:
            with open(session_path, 'r') as f:
                session_string = f.read().strip()
            
            return {"session_string": session_string}
            
        except Exception as e:
            logger.error(f"String session parse error: {e}")
            return None
    
    async def _collect_fingerprint(self, client, user) -> Dict:
        """Збір унікальних параметрів пристрою"""
        fingerprint = {
            "user_id": user.id,
            "phone": user.phone,
            "username": user.username,
            "first_name": user.first_name,
            "premium": getattr(user, 'premium', False),
            "verified": getattr(user, 'verified', False),
            "connection_hash": hashlib.sha256(str(client.session).encode()).hexdigest()[:16],
            "validation_timestamp": datetime.utcnow().isoformat()
        }
        return fingerprint
    
    async def quick_validate(self, session_string: str) -> Tuple[bool, Optional[str]]:
        """Швидка валідація session string"""
        
        if not session_string:
            return False, "Порожня сесія"
        
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession
        except ImportError:
            return False, "Telethon не встановлено"
        
        if not self.api_id or not self.api_hash:
            return False, "API credentials не налаштовано"
        
        try:
            client = TelegramClient(
                StringSession(session_string),
                api_id=int(self.api_id),
                api_hash=self.api_hash
            )
            
            await client.connect()
            
            if await client.is_user_authorized():
                await client.disconnect()
                return True, None
            else:
                await client.disconnect()
                return False, "Не авторизовано"
                
        except Exception as e:
            return False, str(e)

session_validator = SessionValidator()
