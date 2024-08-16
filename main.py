import logging
import asyncio

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import TELEGRAM_TOKEN, AUTHORIZED_CHAT_ID
from google_sheets import append_row



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),  
        logging.StreamHandler()          
    ]
)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class DataEntry(StatesGroup):
    waiting_for_currency = State()
    waiting_for_type = State()  
    waiting_for_spends_category = State()
    waiting_for_incomes_category = State()
    waiting_for_amount_description = State()



@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id == AUTHORIZED_CHAT_ID:
        await message.answer("use /add to add new position \nuse /clear to clear cache data")
    else:
        await message.answer("u re not authorized to use this bot")


@dp.message(Command("clear"))
async def cmd_clear(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("data cleared, u can start over by using /add")


@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    await state.update_data(new_row={})
    
    builder = InlineKeyboardBuilder()
    builder.button(text="$ / usd", callback_data="usd")
    builder.button(text="₽ / rub", callback_data="rub")
    builder.adjust(1)
    
    await message.answer("select currency", reply_markup=builder.as_markup())
    await state.set_state(DataEntry.waiting_for_currency)


@dp.callback_query(DataEntry.waiting_for_currency)
async def process_currency(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(currency=callback_query.data)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="spends", callback_data="spends")
    builder.button(text="incomes", callback_data="incomes")
    builder.adjust(2)
    
    await callback_query.message.edit_text(
        text="select type",
        reply_markup=builder.as_markup()
    )
    await state.set_state(DataEntry.waiting_for_type)


@dp.callback_query(DataEntry.waiting_for_type)
async def process_type(callback_query: types.CallbackQuery, state: FSMContext):
    selected_type = callback_query.data
    await state.update_data(entry_type=selected_type)
    
    if selected_type == "spends":
        await callback_query.message.edit_text(
            text="select a category",
            reply_markup=spends_category_keyboard()
        )
        await state.set_state(DataEntry.waiting_for_spends_category)
    
    elif selected_type == "incomes":
        await callback_query.message.edit_text(
            text="select a category",
            reply_markup=incomes_category_keyboard()
        )
        await state.set_state(DataEntry.waiting_for_incomes_category)

async def process_category_selection(callback_query: types.CallbackQuery, state: FSMContext, entry_type_state: State):
    data = await state.get_data()
    await state.update_data(category=callback_query.data)
    
    currency = data.get('currency', 'N/A')
    entry_type = data.get('entry_type', 'N/A')
    category = callback_query.data
    
    summary_message = (
        f"you selected:\n"
        f"currency: {currency}\n"
        f"type: {entry_type}\n"
        f"category: {category}\n\n"
        f"please enter the amount and optionally a description"
    )
    
    await callback_query.message.edit_text(
        text=summary_message
    )
    await state.set_state(entry_type_state)


@dp.callback_query(DataEntry.waiting_for_spends_category)
async def process_spends_category(callback_query: types.CallbackQuery, state: FSMContext):
    await process_category_selection(callback_query, state, DataEntry.waiting_for_amount_description)


@dp.callback_query(DataEntry.waiting_for_incomes_category)
async def process_incomes_category(callback_query: types.CallbackQuery, state: FSMContext):
    await process_category_selection(callback_query, state, DataEntry.waiting_for_amount_description)


@dp.message(DataEntry.waiting_for_amount_description)
async def process_amount_description(message: types.Message, state: FSMContext):
    data = await state.get_data()

    try:
        amount = float(message.text.split(' ')[0])
        data['amount'] = amount
        data['description'] = ' '.join(message.text.split(' ')[1:])
        
        append_row(data)
        
        await state.clear()
        await message.answer("done, use /add to add a new entry")
        
    except ValueError:
        await message.answer("invalid input, please enter a valid number for the amount \nexample: 12.34 description")


def spends_category_keyboard():
    builder = InlineKeyboardBuilder()
    categories = [
        "eating out", "food", "public transport", 
        "taxi", "shopping", "household", "chill", "no category", "new category"
    ]
    
    for category in categories:
        builder.button(text=category, callback_data=category)
    
    builder.adjust(2)
    return builder.as_markup()

def incomes_category_keyboard():
    builder = InlineKeyboardBuilder()
    categories = ["salary", "family", "gifts"]
    
    for category in categories:
        builder.button(text=category, callback_data=category)
    
    builder.adjust(2)
    return builder.as_markup()    



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())