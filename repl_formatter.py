from db import Period

class Formatter():
    def __init__(self) -> None:
        pass
    
    def format_stats(self, stats: list, period: Period, detailed: bool) -> dict:
        if len(stats) == 0:
            return {'text': 'Нет записей'}
        
        return {'text':str(stats)}

fmtr = Formatter()

# from jinja2 import Template

# API_TOKEN = 'your_api_token'

# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot)
# dp.middleware.setup(LoggingMiddleware())


# async def format_table(data):
#     template = Template("""
#     <table border="1">
#         {% for row in data %}
#         <tr>
#             {% for cell in row %}
#             <td>{{ cell }}</td>
#             {% endfor %}
#         </tr>
#         {% endfor %}
#     </table>
#     """)

#     html_table = template.render(data=data)
#     return html_table


# @dp.message_handler(commands=['start'])
# async def start(message: types.Message):
#     table_data = [
#         ["Name", "Age", "Country"],
#         ["John", "25", "USA"],
#         ["Alice", "30", "UK"],
#         ["Bob", "22", "Canada"]
#     ]
    
#     html_table = await format_table(table_data)
    
#     # Send the HTML table
#     await message.reply(html_table, parse_mode=types.ParseMode.HTML)