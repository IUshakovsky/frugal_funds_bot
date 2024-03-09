import asyncio
from aiogram import Bot, Dispatcher, types, F, BaseMiddleware
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject

from settings import config
from state import AddingCategory, AddingRecord, DeletingCategory, GettingStats
from db import db, Period
from repl_formatter import fmtr

# Check user 
class CheckUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        from_user = data['event_from_user'].id
        if from_user in config.allowed_users:
            return await handler(event, data) 
        else:
            return None
        

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()
dp.update.outer_middleware(CheckUserMiddleware())

def get_confirmation_kb(confirm_msg: str = '?',  add_cancel: bool = True ) -> types.ReplyKeyboardMarkup:
    kb = [[types.KeyboardButton(text="Да"), 
           types.KeyboardButton(text="Нет")]]
    if add_cancel:
        kb[0].append(types.KeyboardButton(text="Отмена"))
    
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, 
                                        resize_keyboard=True, 
                                        input_field_placeholder=confirm_msg)

    return keyboard

def create_kb_builder_periods() ->InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for i, period_text in enumerate(['День','Неделя','Месяц','Год','Все'], start=1):
        builder.add(types.InlineKeyboardButton(
                                        text = period_text,
                                        callback_data = str(i) ))
    builder.adjust(5)
    return builder

def create_kb_builder_cats(user_id: int) -> InlineKeyboardBuilder:
    cats = db.get_categories(user_id) 
    builder = InlineKeyboardBuilder()
    for cat in cats.items():
        builder.add(types.InlineKeyboardButton(
                                        text = cat[1],
                                        callback_data = cat[1] ))
    builder.adjust(3)
    return builder

def create_kb_builder_detailed() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text = 'Кратко',callback_data = '0'))
    builder.add(types.InlineKeyboardButton(text = 'Подробно',callback_data = '1'))
    builder.adjust(2)
    return builder

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer('\_(oO)_/')

# Adding category
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
    await message.answer(text='Куда столько?', reply_markup=create_kb_builder_cats(message.from_user.id).as_markup(resize_keyboard=True))
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

# Simple way without command
@dp.message(F.text.regexp(r'^[\d]+$'))
async def msg_add(message: types.Message, state: FSMContext):
    await state.update_data(input = message.text)
    await message.answer(text='Куда столько?', reply_markup=create_kb_builder_cats(message.from_user.id).as_markup(resize_keyboard=True))
    await state.set_state(AddingRecord.choosing_category)


# Deleting category
@dp.message(Command('delete_cat'))
async def cmd_del_cat(message: types.Message, state: FSMContext):
    cats = db.get_categories(message.from_user.id)
    if len(cats) == 0:
        await message.answer(text='Нечего удалять')
        await state.clear()
    else:
        await message.answer(text='Что удаляем?', reply_markup=create_kb_builder_cats(message.from_user.id).as_markup(resize_keyboard=True))
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
    await state.clear()
    await message.answer('Ок, забыли', reply_markup=types.ReplyKeyboardRemove())

# Getting stats
@dp.message(Command("quick_stat"))
async def cmd_get_quick_stat(message: types.Message):
    stats = db.get_stats(Period.MONTH, message.from_user.id)
    msg = ''
    if len(stats) > 0:
        msg = f'С начала месяца {str(stats[0]["totalValue"])}'
    else:
        msg = 'Пока не было расходов'
    await message.answer(msg)
    
@dp.message(Command('get_stat'))
async def cmd_get_stat(message: types.Message, state: FSMContext):
    await message.answer(text='... ❓ ', reply_markup=create_kb_builder_periods().as_markup(resize_keyboard=True))
    await state.set_state(GettingStats.choosing_period)

@dp.callback_query( GettingStats.choosing_period )
async def handle_stats_period_chosen(callback: types.CallbackQuery, state: FSMContext):
    period = callback.data
    await state.update_data(period=period)
    await state.set_state(GettingStats.choosing_type)
    await callback.message.edit_reply_markup(reply_markup=create_kb_builder_detailed().as_markup(resize_keyboard=True))

@dp.callback_query( GettingStats.choosing_type )
async def handle_stats_type_chosen(callback: types.CallbackQuery, state: FSMContext):
    detailed = callback.data == '1'
    state_data = await state.get_data()
    period = Period(int(state_data['period']))
    stats = db.get_stats( period = period,
                          user_id = callback.from_user.id,
                          detailed = detailed )

    await state.clear()
    args = fmtr.format_stats(stats,period,detailed)
    await callback.message.edit_text(**args)


async def main():
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())