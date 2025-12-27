# SHADOW SYSTEM iO v2.0 - API Documentation

## Overview

This document describes the internal API structure and integration points of SHADOW SYSTEM iO v2.0.

## Core Modules

### 1. Authentication System

**Files:** `handlers/auth_system.py`, `services/user_service.py`

#### Key Types
- `SHADOW-XXXX-XXXX` - License key for Leaders
- `INV-XXXX` - Invite code for Managers

#### Methods
```python
user_service.get_or_create_user(telegram_id, username, first_name)
user_service.get_user_role(telegram_id)
user_service.set_user_role(telegram_id, role)
user_service.activate_key(telegram_id, key_code)
```

### 2. Role System

**File:** `core/role_constants.py`

| Role | Level | Access |
|------|-------|--------|
| GUEST | 0 | View tariffs, submit applications |
| MANAGER | 1 | Campaigns, bots, analytics, templates |
| LEADER | 2 | OSINT, funnels, team, warming |
| ADMIN | 3 | Full system control |

### 3. Encryption Manager

**File:** `core/encryption.py`

```python
from core.encryption import encryption_manager

# Encrypt session string
encrypted = encryption_manager.encrypt_session_string(session_data)

# Decrypt session string
decrypted = encryption_manager.decrypt_session_string(encrypted)

# Encrypt proxy credentials
encrypted_proxy = encryption_manager.encrypt_proxy_credentials({"host": "...", "port": 1080})
```

### 4. OSINT Engine

**File:** `core/osint_engine.py`

```python
from core.osint_engine import osint_engine

# DNS Lookup
result = osint_engine.dns_lookup("example.com")

# WHOIS Lookup
result = osint_engine.whois_lookup("example.com")

# GeoIP Lookup
result = osint_engine.geoip_lookup("8.8.8.8")

# Email Verification
result = osint_engine.email_verify("user@example.com")
```

### 5. Background Tasks

**File:** `core/background_tasks.py`

```python
from core.background_tasks import background_manager, run_osint_background

# Submit background task
task_id = await background_manager.submit(
    name="My Task",
    coro=my_async_function,
    user_id=12345
)

# Check task status
status = background_manager.get_status(task_id)

# Run OSINT in background
task_id = await run_osint_background(
    target="example.com",
    osint_type="dns",
    user_id=12345
)
```

### 6. Mailing Engine

**File:** `core/mailing_engine.py`

```python
from core.mailing_engine import mailing_engine

# Create mailing task
task = mailing_engine.create_task(
    text="Hello!",
    targets=["@channel1", "@channel2"],
    schedule_time=datetime.now()
)

# Get statistics
stats = mailing_engine.get_stats()
```

### 7. Funnel Service

**File:** `services/funnel_service.py`

```python
from services.funnel_service import funnel_service

# Create funnel
funnel = funnel_service.create_funnel(owner_id, name, description)

# Get funnel steps
steps = funnel_service.get_funnel_steps(funnel_id)

# Add step
step = funnel_service.add_step(funnel_id, text, photo_url)
```

## Database Models

**File:** `database/models.py`

### User
- `telegram_id` - Telegram user ID
- `username` - Username
- `role` - User role (guest/manager/leader/admin)
- `is_blocked` - Block status
- `referral_code` - Referral code

### Funnel
- `owner_id` - Owner's Telegram ID
- `name` - Funnel name
- `description` - Description
- `is_active` - Active status
- `views_count` - View counter
- `conversions` - Conversion counter

### BotSession
- `session_string` - Encrypted session
- `phone` - Phone number
- `status` - Session status
- `warming_phase` - Current warming phase
- `proxy_config` - Proxy configuration (JSON)

### MailingTask
- `text` - Message text
- `media_url` - Media URL
- `status` - Task status
- `sent_count` - Sent messages
- `failed_count` - Failed messages

## UI Components

**File:** `core/ui_components.py`

### Paginator
```python
from core.ui_components import Paginator

paginator = Paginator(items, page=1, per_page=10)
current_items = paginator.current_items
nav_buttons = paginator.get_nav_buttons()
```

### ProgressBar
```python
from core.ui_components import ProgressBar

bar = ProgressBar.render(50)  # [█████░░░░░] 50%
emoji_bar = ProgressBar.render_emoji(75)  # 🟢🟢🟢⚪ 75%
```

### MenuBuilder
```python
from core.ui_components import MenuBuilder

keyboard = MenuBuilder.build_grid([
    ("📧 Розсилка", "mailing_menu"),
    ("🔍 Моніторинг", "monitor_menu")
], columns=2)
```

## FSM States

**File:** `core/states.py`

All FSM states are centralized:
- `AdminStates` - Admin panel states
- `AuthStates` - Authentication states
- `FunnelStates` - Funnel management states
- `MailingStates` - Mailing states
- `OSINTStates` - OSINT operation states
- `TemplateStates` - Template management states
- `SupportStates` - Support ticket states

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token | Yes |
| `DATABASE_URL` | PostgreSQL connection URL | Yes |
| `ENCRYPTION_MASTER_KEY` | Master key for encryption | Yes |
| `ADMIN_IDS` | Comma-separated admin Telegram IDs | Yes |
| `API_ID` | Telegram API ID (for Telethon) | No |
| `API_HASH` | Telegram API Hash (for Telethon) | No |

## Callback Data Patterns

| Pattern | Description |
|---------|-------------|
| `{module}_main` | Main menu of module |
| `{module}_menu` | Secondary menu |
| `funnel_{action}:{id}` | Funnel actions |
| `funnel_{module}:{id}:{action}` | Module integration |
| `admin_{action}` | Admin panel actions |
| `back_to_menu` | Return to main menu |
