from aiogram import Router
from core.states import AdminStates

admin_router = Router()
router = admin_router

from .main import *
from .bans import *
from .roles import *
from .keys import *
from .stats import *
from .emergency import *
from .system import *
