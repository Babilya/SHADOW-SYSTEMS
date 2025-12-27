import asyncio
import logging
import hashlib
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ThreatAssessment:
    risk_level: str = "low"
    risk_score: int = 0
    suspicious_users: List[int] = field(default_factory=list)
    flagged_messages: List[Dict] = field(default_factory=list)
    keywords_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class NetworkNode:
    user_id: int
    username: Optional[str]
    connections: List[int] = field(default_factory=list)
    messages_count: int = 0
    influence_score: float = 0.0
    is_admin: bool = False
    risk_flags: List[str] = field(default_factory=list)

class AdvancedOSINTEngine:
    """Розширена OSINT система згідно ТЗ"""
    
    def __init__(self, evidence_storage_path: str = "./evidence"):
        self.evidence_path = Path(evidence_storage_path)
        self.evidence_path.mkdir(exist_ok=True)
        
        self.patterns = {
            'phone_numbers': r'\+?\d{10,15}',
            'coordinates': r'[-+]?\d{1,3}\.\d{4,},\s*[-+]?\d{1,3}\.\d{4,}',
            'crypto_wallets': {
                'btc': r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',
                'eth': r'0x[a-fA-F0-9]{40}',
                'ltc': r'[LM][a-km-zA-HJ-NP-Z1-9]{26,33}'
            },
            'emails': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'urls': r'https?://[^\s<>"{}|\\^`\[\]]+',
            'ips': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'card_numbers': r'\b(?:\d{4}[\s-]?){3}\d{4}\b'
        }
        
        self.suspicious_keywords = {
            'uk': ['зброя', 'вибух', 'координати', 'дрон', 'бомба', 'детонатор', 
                   'теракт', 'диверсія', 'напад', 'вбивство', 'наркотики', 'закладка'],
            'ru': ['оружие', 'взрыв', 'координаты', 'дрон', 'бомба', 'детонатор',
                   'теракт', 'диверсия', 'нападение', 'убийство', 'наркотики', 'закладка'],
            'en': ['weapon', 'explosion', 'coordinates', 'drone', 'bomb', 'detonator',
                   'attack', 'murder', 'drugs', 'stash']
        }
        
        self.risk_weights = {
            'suspicious_keyword': 10,
            'crypto_wallet': 5,
            'phone_number': 3,
            'coordinates': 15,
            'new_account': 5,
            'no_photo': 3,
            'restricted': 8,
            'scam_flag': 20
        }
    
    async def deep_chat_analysis(self, chat_data: Dict, depth: str = "full") -> Dict:
        """Глибокий аналіз чату з різними рівнями деталізації"""
        
        analysis_results = {
            "metadata": {},
            "participants": [],
            "messages_analysis": {},
            "network_graph": {},
            "threat_assessment": {},
            "evidence_files": [],
            "patterns_found": {},
            "timeline": [],
            "summary": ""
        }
        
        try:
            analysis_results["metadata"] = {
                "chat_id": chat_data.get('id'),
                "title": chat_data.get('title', 'Unknown'),
                "username": chat_data.get('username'),
                "participants_count": chat_data.get('participants_count', 0),
                "date_created": chat_data.get('date'),
                "scam": chat_data.get('scam', False),
                "verified": chat_data.get('verified', False),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "depth": depth
            }
            
            if depth in ["participants", "full"]:
                participants = chat_data.get('participants', [])
                for user in participants:
                    user_data = self._analyze_participant(user)
                    analysis_results["participants"].append(user_data)
                    
                    if user_data.get('risk_score', 0) > 30:
                        analysis_results["threat_assessment"].setdefault(
                            "suspicious_users", []
                        ).append(user_data)
            
            if depth in ["messages", "full"]:
                messages = chat_data.get('messages', [])
                messages_analysis = self._analyze_messages(messages)
                analysis_results["messages_analysis"] = messages_analysis
                analysis_results["patterns_found"] = messages_analysis.get('patterns', {})
            
            if depth == "full":
                network_graph = self._build_network_graph(
                    analysis_results["participants"],
                    chat_data.get('messages', [])
                )
                analysis_results["network_graph"] = network_graph
                
                threat = self._assess_threats(analysis_results)
                analysis_results["threat_assessment"] = threat
            
            analysis_results["summary"] = self._generate_summary(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Deep chat analysis error: {e}")
            return {"error": str(e)}
    
    def _analyze_participant(self, user: Dict) -> Dict:
        """Детальний аналіз учасника"""
        
        participant_data = {
            "id": user.get('id'),
            "username": user.get('username'),
            "first_name": user.get('first_name'),
            "last_name": user.get('last_name'),
            "phone": user.get('phone'),
            "bot": user.get('bot', False),
            "premium": user.get('premium', False),
            "verified": user.get('verified', False),
            "scam": user.get('scam', False),
            "fake": user.get('fake', False),
            "restricted": user.get('restricted', False),
            "status": user.get('status', 'unknown'),
            "profile_photo": bool(user.get('photo')),
            "risk_score": 0,
            "flags": []
        }
        
        if participant_data['scam']:
            participant_data['risk_score'] += self.risk_weights['scam_flag']
            participant_data['flags'].append('SCAM_FLAGGED')
        
        if participant_data['restricted']:
            participant_data['risk_score'] += self.risk_weights['restricted']
            participant_data['flags'].append('RESTRICTED_ACCOUNT')
        
        if not participant_data['profile_photo']:
            participant_data['risk_score'] += self.risk_weights['no_photo']
            participant_data['flags'].append('NO_PROFILE_PHOTO')
        
        if participant_data['fake']:
            participant_data['risk_score'] += 15
            participant_data['flags'].append('FAKE_ACCOUNT')
        
        if participant_data['risk_score'] > 30:
            participant_data['threat_level'] = 'high'
        elif participant_data['risk_score'] > 15:
            participant_data['threat_level'] = 'medium'
        else:
            participant_data['threat_level'] = 'low'
        
        return participant_data
    
    def _analyze_messages(self, messages: List[Dict]) -> Dict:
        """Аналіз повідомлень"""
        
        analysis = {
            "total_messages": len(messages),
            "patterns": {
                "phone_numbers": [],
                "coordinates": [],
                "crypto_wallets": [],
                "emails": [],
                "urls": [],
                "ips": []
            },
            "suspicious_content": [],
            "timeline": [],
            "top_senders": {},
            "keywords_detected": []
        }
        
        for msg in messages:
            text = msg.get('text', '')
            if not text:
                continue
            
            for pattern_name, pattern in self.patterns.items():
                if pattern_name == 'crypto_wallets':
                    for wallet_type, wallet_pattern in pattern.items():
                        matches = re.findall(wallet_pattern, text)
                        if matches:
                            for match in matches:
                                analysis['patterns']['crypto_wallets'].append({
                                    'type': wallet_type,
                                    'value': match,
                                    'message_id': msg.get('id'),
                                    'sender': msg.get('sender_id')
                                })
                else:
                    matches = re.findall(pattern, text)
                    if matches:
                        for match in matches:
                            analysis['patterns'][pattern_name].append({
                                'value': match,
                                'message_id': msg.get('id'),
                                'sender': msg.get('sender_id')
                            })
            
            text_lower = text.lower()
            for lang, keywords in self.suspicious_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        analysis['keywords_detected'].append({
                            'keyword': keyword,
                            'language': lang,
                            'message_id': msg.get('id'),
                            'context': text[:200]
                        })
                        analysis['suspicious_content'].append({
                            'message_id': msg.get('id'),
                            'text': text[:500],
                            'reason': f'Suspicious keyword: {keyword}',
                            'sender': msg.get('sender_id')
                        })
            
            sender = msg.get('sender_id')
            if sender:
                analysis['top_senders'][sender] = analysis['top_senders'].get(sender, 0) + 1
        
        return analysis
    
    def _build_network_graph(self, participants: List[Dict], messages: List[Dict]) -> Dict:
        """Побудова мережевого графа зв'язків"""
        
        graph = {
            "nodes": [],
            "edges": [],
            "clusters": [],
            "central_nodes": [],
            "isolated_nodes": []
        }
        
        user_messages = {}
        user_replies = {}
        
        for msg in messages:
            sender = msg.get('sender_id')
            reply_to = msg.get('reply_to_msg_id')
            
            if sender:
                user_messages[sender] = user_messages.get(sender, 0) + 1
                
                if reply_to:
                    for m in messages:
                        if m.get('id') == reply_to:
                            original_sender = m.get('sender_id')
                            if original_sender and original_sender != sender:
                                key = (sender, original_sender)
                                user_replies[key] = user_replies.get(key, 0) + 1
        
        for participant in participants:
            user_id = participant.get('id')
            node = {
                "id": user_id,
                "username": participant.get('username'),
                "messages_count": user_messages.get(user_id, 0),
                "connections": [],
                "influence_score": 0,
                "risk_score": participant.get('risk_score', 0)
            }
            
            total_messages = sum(user_messages.values()) or 1
            node['influence_score'] = (node['messages_count'] / total_messages) * 100
            
            graph['nodes'].append(node)
        
        for (sender, receiver), weight in user_replies.items():
            edge = {
                "source": sender,
                "target": receiver,
                "weight": weight,
                "type": "reply"
            }
            graph['edges'].append(edge)
            
            for node in graph['nodes']:
                if node['id'] == sender:
                    node['connections'].append(receiver)
                elif node['id'] == receiver:
                    node['connections'].append(sender)
        
        graph['central_nodes'] = sorted(
            graph['nodes'],
            key=lambda x: x['influence_score'],
            reverse=True
        )[:5]
        
        graph['isolated_nodes'] = [
            n for n in graph['nodes']
            if not n['connections'] and n['messages_count'] == 0
        ]
        
        return graph
    
    def _assess_threats(self, analysis: Dict) -> Dict:
        """Оцінка загроз"""
        
        threat = {
            "risk_level": "low",
            "risk_score": 0,
            "suspicious_users": [],
            "flagged_content": [],
            "keywords_found": [],
            "patterns_found": [],
            "recommendations": []
        }
        
        participants = analysis.get('participants', [])
        for p in participants:
            if p.get('risk_score', 0) > 20:
                threat['suspicious_users'].append({
                    'id': p.get('id'),
                    'username': p.get('username'),
                    'risk_score': p.get('risk_score'),
                    'flags': p.get('flags', [])
                })
                threat['risk_score'] += p.get('risk_score', 0) // 5
        
        messages_analysis = analysis.get('messages_analysis', {})
        patterns = messages_analysis.get('patterns', {})
        
        for pattern_name, items in patterns.items():
            if items:
                threat['patterns_found'].append({
                    'type': pattern_name,
                    'count': len(items),
                    'samples': items[:3]
                })
                
                if pattern_name == 'coordinates':
                    threat['risk_score'] += len(items) * 10
                elif pattern_name == 'crypto_wallets':
                    threat['risk_score'] += len(items) * 5
        
        keywords = messages_analysis.get('keywords_detected', [])
        if keywords:
            threat['keywords_found'] = keywords[:20]
            threat['risk_score'] += len(keywords) * 8
        
        suspicious = messages_analysis.get('suspicious_content', [])
        threat['flagged_content'] = suspicious[:10]
        
        if threat['risk_score'] > 100:
            threat['risk_level'] = 'critical'
            threat['recommendations'].append('Терміново повідомити правоохоронні органи')
        elif threat['risk_score'] > 50:
            threat['risk_level'] = 'high'
            threat['recommendations'].append('Детальний моніторинг та документування')
        elif threat['risk_score'] > 20:
            threat['risk_level'] = 'medium'
            threat['recommendations'].append('Спостереження за активністю')
        else:
            threat['risk_level'] = 'low'
            threat['recommendations'].append('Стандартний моніторинг')
        
        return threat
    
    def _generate_summary(self, analysis: Dict) -> str:
        """Генерація текстового резюме"""
        
        metadata = analysis.get('metadata', {})
        threat = analysis.get('threat_assessment', {})
        messages = analysis.get('messages_analysis', {})
        
        summary = f"""
📊 OSINT ЗВІТ
═══════════════════════

📌 Об'єкт: {metadata.get('title', 'N/A')}
🆔 ID: {metadata.get('chat_id', 'N/A')}
👥 Учасників: {metadata.get('participants_count', 0)}
📅 Аналіз: {metadata.get('analysis_timestamp', 'N/A')}

⚠️ ОЦІНКА ЗАГРОЗ
───────────────────────
Рівень ризику: {threat.get('risk_level', 'N/A').upper()}
Бал ризику: {threat.get('risk_score', 0)}
Підозрілих користувачів: {len(threat.get('suspicious_users', []))}
Ключових слів виявлено: {len(threat.get('keywords_found', []))}

📈 СТАТИСТИКА
───────────────────────
Повідомлень проаналізовано: {messages.get('total_messages', 0)}
Телефонів знайдено: {len(messages.get('patterns', {}).get('phone_numbers', []))}
Крипто-гаманців: {len(messages.get('patterns', {}).get('crypto_wallets', []))}
Координат: {len(messages.get('patterns', {}).get('coordinates', []))}

📋 РЕКОМЕНДАЦІЇ
───────────────────────
"""
        for rec in threat.get('recommendations', ['Немає рекомендацій']):
            summary += f"• {rec}\n"
        
        return summary.strip()
    
    async def extract_media_metadata(self, file_path: str) -> Dict:
        """Витяг метаданих з медіафайлу"""
        
        from core.osint_tools.image_analyzer import ImageAnalyzer
        
        analyzer = ImageAnalyzer()
        
        path = Path(file_path)
        if not path.exists():
            return {"error": "File not found"}
        
        if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return analyzer.extract_exif_data(file_path)
        else:
            return {"error": "Unsupported file type"}
    
    async def store_evidence(self, data: Dict, project_id: str, evidence_type: str) -> str:
        """Збереження доказів"""
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{evidence_type}_{project_id}_{timestamp}.json"
        filepath = self.evidence_path / filename
        
        evidence_record = {
            "id": hashlib.sha256(f"{project_id}{timestamp}".encode()).hexdigest()[:16],
            "type": evidence_type,
            "project_id": project_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
            "hash": hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(evidence_record, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Evidence stored: {filepath}")
        return str(filepath)

advanced_osint_engine = AdvancedOSINTEngine()
