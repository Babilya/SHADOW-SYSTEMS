from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class ApplicationFSM(StatesGroup):
    duration = State()
    name = State()
    purpose = State()
    contact = State()

@router.callback_query(F.data.startswith("apply_"))
async def start_application(query: CallbackQuery, state: FSMContext):
    tariff = query.data.split("_")[1]
    await state.update_data(tariff=tariff)
    await state.set_state(ApplicationFSM.duration)
    await query.message.edit_text("На який термін?\n[2 дні] [14 днів] [30 днів]")
    await query.answer()
