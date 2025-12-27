from core.roles import (
    UserRole, 
    ROLE_PERMISSIONS, 
    ROLE_NAMES, 
    ROLE_DESCRIPTIONS,
    ROLE_HIERARCHY,
    TARIFFS,
    has_permission, 
    get_role_level,
    can_manage_role,
    get_tariff,
    check_role_access
)
from core.campaign_manager import (
    campaign_manager, 
    CampaignManager, 
    CampaignStatus, 
    CampaignType,
    Campaign
)
from core.scheduler import (
    scheduler, 
    CampaignScheduler, 
    TaskStatus, 
    TaskType,
    ScheduledTask
)
from core.audit_logger import (
    audit_logger,
    AuditLogger,
    ActionCategory,
    ActionSeverity,
    AuditEntry
)
from core.alerts import (
    alert_system,
    AlertSystem,
    AlertType,
    AlertPriority,
    Alert
)
from core.ai_service import (
    ai_service,
    AIService
)
from core.advanced_parser import (
    advanced_parser,
    AdvancedTelegramParser,
    initialize_parsers_with_client
)
from core.realtime_parser import (
    realtime_parser,
    RealTimeParser,
    initialize_realtime_with_client
)
from core.botnet_manager import (
    botnet_manager,
    BotnetManager
)
from core.antidetect import (
    antidetect_system,
    AntiDetectSystem
)
from core.recovery_system import (
    recovery_system,
    RecoverySystem
)
from core.session_importer import (
    session_importer,
    SessionImporter
)
from core.advanced_osint_engine import (
    advanced_osint_engine,
    AdvancedOSINTEngine
)
from core.rapid_osint import (
    rapid_osint,
    RapidOSINTParser
)
from core.realtime_monitor import (
    realtime_monitor,
    RealTimeMonitor
)
