import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from settings import config
from db import db, Period

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

def get_confirmation_kb(confirm_msg: str = '?',  add_cancel: bool = True ) -> types.ReplyKeyboardMarkup:
    kb = [[types.KeyboardButton(text="Да"), 
           types.KeyboardButton(text="Нет")]]
    if add_cancel:
        kb[0].append(types.KeyboardButton(text="Отмена"))
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, 
                                        resize_keyboard=True, 
                                        input_field_placeholder=confirm_msg)

    return keyboard


def create_kb_builder(user_id: int) -> InlineKeyboardBuilder:
    cats = db.get_categories(user_id) 
    builder = InlineKeyboardBuilder()
    for cat in cats.items():
        builder.add(types.InlineKeyboardButton(
                                        text = cat[1],
                                        callback_data = cat[1] ))
    builder.adjust(3)
    return builder


@dp.message(Command("start"))
async def start(message: types.Message):
    # Create a simple menu using InlineKeyboardMarkup and InlineKeyboardButton
    await message.answer("Welcome to the Expense Tracker Bot")

# Adding category
class AddingCategory(StatesGroup):
    inputing_name = State()
    confirmation = State()
    
@dp.message(Command("new_cat"))
async def cmd_new_category(message: types.Message, state: FSMContext):
    await message.answer('Введи название')
    await state.set_state(AddingCategory.inputing_name)

@dp.message(AddingCategory.inputing_name)
async def handle_input_cat_name(message: types.Message, state: FSMContext):
    cats = db.get_categories(message.from_user.id)
    if message.text in cats.values():
        await message.reply('Такая уже есть')
        return
    
    keyboard = get_confirmation_kb('Подтверди или опровергни')
    await state.update_data(cat_name = message.text)
    await message.reply('Уверен?', reply_markup=keyboard)
    await state.set_state(AddingCategory.confirmation)
    
@dp.message(AddingCategory.confirmation, F.text == 'Да')
async def handle_confirm_input_cat_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_category(data['cat_name'], message.from_user.id)
    await message.answer('Добавлено', reply_markup=types.ReplyKeyboardRemove())
    await state.clear() 

@dp.message(AddingCategory.confirmation, F.text == 'Нет')
async def handle_decline_input_cat_name(message: types.Message, state: FSMContext):
    await message.answer('Тогда введи что-то нормальное', reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddingCategory.inputing_name)

@dp.message(AddingCategory.confirmation, F.text == 'Отмена')
async def handle_cancel_input_cat_name(message: types.Message, state: FSMContext):
    await message.answer('Забудем об этом', reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    
# Adding record
class AddingRecord(StatesGroup):
    inputing_amount = State()
    choosing_category = State()

@dp.message(Command("add"))
async def cmd_add(message: types.Message, state: FSMContext):
    cats = db.get_categories(message.from_user.id)
    if len(cats) == 0:
        await message.answer('Сначала добавь категорию')
    else:
        await message.answer('Введи сумму')
        await state.set_state(AddingRecord.inputing_amount)

@dp.message(AddingRecord.inputing_amount, F.text.isdigit())
async def handle_input_amnt(message: types.Message, state: FSMContext):
    await state.update_data(input = message.text)
    await message.answer(text='Куда столько?', reply_markup=create_kb_builder(message.from_user.id).as_markup(resize_keyboard=True))
    await state.set_state(AddingRecord.choosing_category)

@dp.message(AddingRecord.inputing_amount)
async def handle_input_amnt_wrong(message: types.Message):
    await message.reply("🤦🏻‍♂️ сумму введи")    

@dp.callback_query( AddingRecord.choosing_category )
async def category_chosen(callback: types.CallbackQuery, state: FSMContext):
    cats = db.get_categories(callback.from_user.id)
    if not callback.data in cats.values(): 
        await callback.answer('Кнопку нажми 🤦🏻‍♂️')    
        return

    user_data = await state.get_data()
    db.add_record( cat_name = callback.data, 
                  user_id = callback.from_user.id, 
                  amnt    = int(user_data['input']))

    await callback.message.edit_text('Записал')
    await state.clear()
    await callback.answer()

# Deleting category
class DeletingCategory(StatesGroup):
    choosing_category = State()
    confirmation = State()
    
@dp.message(Command('delete_cat'))
async def cmd_del_cat(message: types.Message, state: FSMContext):
    cats = db.get_categories(message.from_user.id)
    if len(cats) == 0:
        await message.answer(text='Нечего удалять')
        await state.clear()
    else:
        await message.answer(text='Что удаляем?', reply_markup=create_kb_builder(message.from_user.id).as_markup(resize_keyboard=True))
        await state.set_state(DeletingCategory.choosing_category)

@dp.callback_query( DeletingCategory.choosing_category )
async def handle_del_cat_chosen(callback: types.CallbackQuery, state: FSMContext):
    cat_name = callback.data
    cats = db.get_categories(callback.from_user.id)
    if cat_name not in cats.values(): 
        await callback.answer('Кнопку нажми 🤦🏻‍♂️')    
        return   
   
    keyboard = get_confirmation_kb(add_cancel=False)
    await state.update_data(cat_name = cat_name)
    await callback.message.answer(f'{cat_name}. Уверен?', reply_markup=keyboard)
    await state.set_state(DeletingCategory.confirmation)
    
@dp.message(DeletingCategory.confirmation, F.text == 'Да')
async def handle_confirm_del_cat_name(message: types.Message, state: FSMContext):
    cat_data = await state.get_data()
    deleted = db.delete_category(message.from_user.id, cat_data['cat_name'])
    msg = ''
    if deleted:
        msg = '👌'
    else:
        msg = 'Не удалось 🤷🏻‍♂️'

    await state.clear()
    await message.answer(msg, reply_markup=types.ReplyKeyboardRemove())


@dp.message(DeletingCategory.confirmation, F.text == 'Нет')
async def handle_decline_del_cat_name(message: types.Message, state: FSMContext):
    await message.answer('Ок, забыли', reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

# Getting stats
@dp.message(Command("quick_stat"))
async def get_quick_stat(message: types.Message):
    stats = db.get_stats(Period.MONTH, message.from_user.id)
    await message.answer(f'С начала месяца {str(stats[0]['totalValue'])}')
    
class GettingStats(StatesGroup):
    choosing_period = State()
    choosing_type = State()

async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())