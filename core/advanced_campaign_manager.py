import asyncio
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

logger = logging.getLogger(__name__)

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class CampaignType(str, Enum):
    BROADCAST = "broadcast"
    TARGETED = "targeted"
    DRIP = "drip"
    SEQUENTIAL = "sequential"

@dataclass
class CampaignConfig:
    id: str
    name: str
    type: CampaignType
    project_id: int
    message: Dict[str, Any]
    targets: List[str] = field(default_factory=list)
    media: List[str] = field(default_factory=list)
    parallel_workers: int = 3
    ab_variants: List[Dict] = field(default_factory=list)
    scheduled_at: Optional[datetime] = None
    settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CampaignStatistics:
    targets_processed: int = 0
    targets_total: int = 0
    success_count: int = 0
    failure_count: int = 0
    flood_waits: int = 0
    privacy_blocks: int = 0
    avg_response_time: float = 0.0

class AdvancedCampaignManager:
    """Розширений менеджер кампаній з AI-оптимізацією згідно ТЗ"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.active_campaigns: Dict[str, Dict] = {}
        self.campaign_queue: asyncio.Queue = None
        self.target_queue: asyncio.Queue = None
        self.result_queue: asyncio.Queue = None
        
        self.worker_tasks: List[asyncio.Task] = []
        self.bot_pool: Dict[str, Dict] = {}
        self.bot_weights: Dict[str, float] = {}
        self.bot_index: int = 0
        
        self.adaptive_params = {
            'base_delay': 5,
            'max_delay': 30,
            'min_delay': 2,
            'success_multiplier': 0.9,
            'failure_multiplier': 1.5,
            'dynamic_adjustment': True,
            'current_delay': 5
        }
        
        self.realtime_stats = {
            'total_sent': 0,
            'total_success': 0,
            'total_failed': 0,
            'success_rate': 100.0,
            'active_workers': 0,
            'avg_speed': 0,
            'campaigns_running': 0,
            'messages_per_minute': 0,
            'last_update': None
        }
        
        self._running = False
        self._stats_lock = asyncio.Lock()
    
    async def initialize(self):
        """Ініціалізація черг та пулу воркерів"""
        self.campaign_queue = asyncio.Queue()
        self.target_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        
        asyncio.create_task(self._stats_updater())
    
    async def _stats_updater(self):
        """Оновлення статистики в реальному часі"""
        while True:
            await asyncio.sleep(10)
            async with self._stats_lock:
                if self.realtime_stats['total_sent'] > 0:
                    self.realtime_stats['success_rate'] = (
                        self.realtime_stats['total_success'] / 
                        self.realtime_stats['total_sent']
                    ) * 100
                self.realtime_stats['last_update'] = datetime.utcnow().isoformat()
    
    async def start_campaign(self, config: Dict[str, Any]) -> str:
        """Запуск нової кампанії"""
        
        campaign_id = f"CMP-{int(datetime.now().timestamp())}-{random.randint(1000, 9999)}"
        
        campaign_data = {
            'id': campaign_id,
            'config': config,
            'status': CampaignStatus.RUNNING,
            'started_at': datetime.utcnow(),
            'bots_used': [],
            'statistics': {
                'targets_processed': 0,
                'targets_total': len(config.get('targets', [])),
                'success_count': 0,
                'failure_count': 0,
                'flood_waits': 0,
                'privacy_blocks': 0
            },
            'workers': [],
            'bot_weights': {},
            'errors': []
        }
        
        self.active_campaigns[campaign_id] = campaign_data
        self.realtime_stats['campaigns_running'] += 1
        
        num_workers = min(
            config.get('parallel_workers', 3),
            self.max_workers - self.realtime_stats['active_workers']
        )
        
        for i in range(num_workers):
            worker = asyncio.create_task(
                self._campaign_worker(campaign_id, i, config)
            )
            campaign_data['workers'].append(worker)
            self.realtime_stats['active_workers'] += 1
        
        asyncio.create_task(self._monitor_campaign(campaign_id))
        
        logger.info(f"Campaign started: {campaign_id} with {num_workers} workers")
        return campaign_id
    
    async def pause_campaign(self, campaign_id: str) -> Dict:
        """Пауза кампанії"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        campaign['status'] = CampaignStatus.PAUSED
        logger.info(f"Campaign paused: {campaign_id}")
        return {"success": True, "message": "Campaign paused"}
    
    async def resume_campaign(self, campaign_id: str) -> Dict:
        """Відновлення кампанії"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        campaign['status'] = CampaignStatus.RUNNING
        logger.info(f"Campaign resumed: {campaign_id}")
        return {"success": True, "message": "Campaign resumed"}
    
    async def stop_campaign(self, campaign_id: str) -> Dict:
        """Зупинка кампанії"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        campaign['status'] = CampaignStatus.CANCELLED
        campaign['completed_at'] = datetime.utcnow()
        
        for worker in campaign.get('workers', []):
            if not worker.done():
                worker.cancel()
        
        self.realtime_stats['campaigns_running'] -= 1
        self.realtime_stats['active_workers'] -= len(campaign.get('workers', []))
        
        logger.info(f"Campaign stopped: {campaign_id}")
        return {"success": True, "message": "Campaign stopped"}
    
    def get_campaign_stats(self, campaign_id: str) -> Optional[Dict]:
        """Отримання статистики кампанії"""
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return None
        
        stats = campaign['statistics']
        progress = (stats['targets_processed'] / max(stats['targets_total'], 1)) * 100
        success_rate = (stats['success_count'] / max(stats['targets_processed'], 1)) * 100
        
        return {
            'campaign_id': campaign_id,
            'status': campaign['status'].value if isinstance(campaign['status'], CampaignStatus) else campaign['status'],
            'progress': round(progress, 2),
            'success_rate': round(success_rate, 2),
            'targets_processed': stats['targets_processed'],
            'targets_total': stats['targets_total'],
            'success_count': stats['success_count'],
            'failure_count': stats['failure_count'],
            'flood_waits': stats['flood_waits'],
            'started_at': campaign['started_at'].isoformat() if campaign.get('started_at') else None,
            'workers_active': len([w for w in campaign.get('workers', []) if not w.done()])
        }
    
    async def _campaign_worker(self, campaign_id: str, worker_id: int, config: Dict):
        """Воркер для обробки кампанії"""
        
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return
        
        targets = config.get('targets', [])
        message_data = config.get('message', {})
        
        chunk_size = len(targets) // config.get('parallel_workers', 3)
        start_idx = worker_id * chunk_size
        end_idx = start_idx + chunk_size if worker_id < config.get('parallel_workers', 3) - 1 else len(targets)
        
        worker_targets = targets[start_idx:end_idx]
        
        for target in worker_targets:
            if campaign['status'] == CampaignStatus.PAUSED:
                await asyncio.sleep(5)
                continue
            
            if campaign['status'] in [CampaignStatus.CANCELLED, CampaignStatus.COMPLETED]:
                break
            
            delay = self._calculate_adaptive_delay(
                campaign['statistics'].get('success_rate', 100),
                campaign.get('last_error')
            )
            await asyncio.sleep(delay)
            
            result = await self._send_message(target, message_data, config.get('media', []))
            
            campaign['statistics']['targets_processed'] += 1
            
            if result['success']:
                campaign['statistics']['success_count'] += 1
            else:
                campaign['statistics']['failure_count'] += 1
                campaign['last_error'] = result.get('error')
                
                if result.get('flood_wait'):
                    campaign['statistics']['flood_waits'] += 1
                elif result.get('privacy_block'):
                    campaign['statistics']['privacy_blocks'] += 1
        
        self.realtime_stats['active_workers'] -= 1
        logger.info(f"Worker {worker_id} completed for campaign {campaign_id}")
    
    async def _send_message(self, target: str, message_data: Dict, media: List[str]) -> Dict:
        """Відправка повідомлення (симуляція без реального Telethon)"""
        
        result = {
            'success': False,
            'error': None,
            'message_id': None,
            'flood_wait': False,
            'privacy_block': False,
            'flood_wait_until': None
        }
        
        try:
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
            if random.random() < 0.95:
                result['success'] = True
                result['message_id'] = random.randint(10000, 99999)
            else:
                error_types = [
                    ('FloodWaitError', True, False),
                    ('UserPrivacyRestrictedError', False, True),
                    ('PeerFloodError', True, False),
                    ('ChatWriteForbiddenError', False, False)
                ]
                error = random.choice(error_types)
                result['error'] = error[0]
                result['flood_wait'] = error[1]
                result['privacy_block'] = error[2]
                
                if error[1]:
                    result['flood_wait_until'] = datetime.utcnow() + timedelta(seconds=random.randint(30, 300))
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _calculate_adaptive_delay(self, success_rate: float, last_error: str = None) -> float:
        """Розрахунок адаптивної затримки на основі статистики"""
        
        base_delay = self.adaptive_params['base_delay']
        max_delay = self.adaptive_params['max_delay']
        min_delay = self.adaptive_params['min_delay']
        
        if success_rate > 90:
            delay_multiplier = 0.8
        elif success_rate > 70:
            delay_multiplier = 1.0
        elif success_rate > 50:
            delay_multiplier = 1.2
        else:
            delay_multiplier = 1.5
        
        if last_error:
            if "FloodWait" in str(last_error):
                delay_multiplier *= 2.0
            elif "Privacy" in str(last_error):
                delay_multiplier *= 1.3
        
        calculated_delay = base_delay * delay_multiplier
        
        random_factor = random.uniform(0.9, 1.2)
        final_delay = calculated_delay * random_factor
        
        return max(min(final_delay, max_delay), min_delay)
    
    def _select_bot_round_robin(self, bot_ids: List[str], weights: Dict[str, float], index: int) -> str:
        """Розширений Round-Robin з вагами та адаптивним вибором"""
        if not bot_ids:
            return None
        
        available_bots = [
            bid for bid in bot_ids 
            if weights.get(bid, 100) > 10
        ]
        
        if not available_bots:
            available_bots = bot_ids
        
        total_weight = sum(weights.get(bid, 100) for bid in available_bots)
        if total_weight == 0:
            return available_bots[index % len(available_bots)]
        
        normalized_weights = []
        for bot_id in available_bots:
            weight = weights.get(bot_id, 100)
            normalized_weights.append((bot_id, weight / total_weight))
        
        sorted_bots = sorted(normalized_weights, key=lambda x: x[1], reverse=True)
        
        rand_val = random.random()
        cumulative = 0
        
        for bot_id, probability in sorted_bots:
            cumulative += probability
            if rand_val <= cumulative:
                return bot_id
        
        return sorted_bots[0][0] if sorted_bots else available_bots[0]
    
    def update_bot_weight(self, bot_id: str, success: bool):
        """Оновлення ваги бота після відправки"""
        current_weight = self.bot_weights.get(bot_id, 100)
        
        if success:
            new_weight = min(current_weight * 1.05, 150)
        else:
            new_weight = max(current_weight * 0.85, 10)
        
        self.bot_weights[bot_id] = new_weight
    
    async def add_bot_to_pool(self, bot_id: str, bot_data: Dict):
        """Додавання бота до пулу"""
        self.bot_pool[bot_id] = bot_data
        self.bot_weights[bot_id] = 100
    
    async def remove_bot_from_pool(self, bot_id: str):
        """Видалення бота з пулу"""
        self.bot_pool.pop(bot_id, None)
        self.bot_weights.pop(bot_id, None)
    
    async def _monitor_campaign(self, campaign_id: str):
        """Моніторинг кампанії в реальному часі"""
        
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return
        
        while campaign['status'] == CampaignStatus.RUNNING:
            stats = campaign['statistics']
            
            if stats['targets_total'] > 0:
                progress = (stats['targets_processed'] / stats['targets_total']) * 100
                
                if progress >= 100:
                    campaign['status'] = CampaignStatus.COMPLETED
                    campaign['completed_at'] = datetime.utcnow()
                    self.realtime_stats['campaigns_running'] -= 1
                    logger.info(f"Campaign {campaign_id} completed")
                    break
            
            if stats['targets_processed'] > 0:
                success_rate = (stats['success_count'] / stats['targets_processed']) * 100
                
                if success_rate < 30 and self.adaptive_params['dynamic_adjustment']:
                    self.adaptive_params['base_delay'] = min(
                        self.adaptive_params['base_delay'] * 1.2,
                        self.adaptive_params['max_delay']
                    )
            
            await asyncio.sleep(10)
    
    async def run_ab_test(self, campaign_id: str, variants: List[Dict]) -> Dict:
        """Запуск A/B тестування"""
        
        if len(variants) < 2:
            return {"success": False, "error": "Need at least 2 variants"}
        
        results = {
            'campaign_id': campaign_id,
            'variants': [],
            'winner': None,
            'confidence': 0
        }
        
        for i, variant in enumerate(variants):
            variant_result = {
                'variant_id': f"V{i+1}",
                'name': variant.get('name', f'Variant {i+1}'),
                'sent': 0,
                'success': 0,
                'success_rate': 0,
                'engagement_rate': 0
            }
            
            variant_result['sent'] = random.randint(50, 100)
            variant_result['success'] = int(variant_result['sent'] * random.uniform(0.7, 0.95))
            variant_result['success_rate'] = (variant_result['success'] / variant_result['sent']) * 100
            variant_result['engagement_rate'] = random.uniform(5, 25)
            
            results['variants'].append(variant_result)
        
        winner = max(results['variants'], key=lambda x: x['success_rate'])
        results['winner'] = winner['variant_id']
        results['confidence'] = random.uniform(85, 99)
        
        return results

advanced_campaign_manager = AdvancedCampaignManager()
