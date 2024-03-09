from aiogram.fsm.state import State, StatesGroup

class AddingCategory(StatesGroup):
    inputing_name = State()
    confirmation = State()
    
class AddingRecord(StatesGroup):
    inputing_amount = State()
    choosing_category = State()
    
class DeletingCategory(StatesGroup):
    choosing_category = State()
    confirmation = State()
    
class GettingStats(StatesGroup):
    choosing_period = State()
    choosing_type = State()


    