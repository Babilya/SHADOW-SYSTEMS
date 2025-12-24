from aiogram.fsm.state import State, StatesGroup

class MainFSM(StatesGroup):
    guest_menu = State()
    tariff_select = State()
    application_fsm = State()
    auth_state = State()
