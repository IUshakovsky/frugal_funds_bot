from aiogram.enums import ParseMode
import locale
import calendar
from datetime import datetime

from db import Period

class Formatter():
    def __init__(self) -> None:
        locale.setlocale(locale.LC_ALL, 'ru_RU')
    
    def _format_total_str(self, stats:list, prefix: str = '') -> dict:
        return { 'text': f"{prefix}: {str(stats[0]['totalValue'])}", 'parse_mode':ParseMode.MARKDOWN_V2 } 

    def _format_cats_values(self, stats:list, prefix: str = '') -> dict:
        md2_reply = ''
        data = [ [row['_id']['cat_name'], row['totalValue']] for row in stats]
        data.sort(key=lambda x: int(x[1]),reverse=True)
        for line in data:
            md2_reply += f'*{line[0]}* {line[1]} \n'
        total = sum([r[1] for r in data])
        return {'text': f'{prefix}: {total}\n{md2_reply}', 'parse_mode':ParseMode.MARKDOWN_V2}
 
    def _format_months_values(sel, stats:list):
        data = [ [row['_id']['month'], row['totalValue']] for row in stats]        
        total = sum([r[1] for r in data])
        md2_reply = f"За *{stats[0]['_id']['year']}* год: {total} \n"
        for line in data:
            md2_reply += f'*{calendar.month_abbr[int(line[0])]}*:  {line[1]} \n'
    
        return {'text': md2_reply, 'parse_mode':ParseMode.MARKDOWN_V2}     
   
    
    def format_stats(self, stats: list, period: Period, detailed: bool) -> dict:
        if len(stats) == 0:
            return {'text': 'Нет записей'}
        
        match period:
            case Period.DAY:
                if detailed:
                    return self._format_cats_values(stats, f'*Сегодня*')
                else:
                    return self._format_total_str(stats, f'*Сегодня*')
            
            case Period.WEEK: 
                if detailed:
                    return self._format_cats_values(stats, f'*За неделю*')
                else:
                    return self._format_total_str(stats, f'*За неделю*')

            case Period.MONTH:
                if detailed:
                    return self._format_cats_values(stats, f'*За месяц*')
                else:
                    return self._format_total_str(stats, f'*За месяц*')

            case Period.YEAR:
                if detailed:
                    return self._format_cats_values(stats, f'За *{datetime.now().year}* год')    
                else:
                    return self._format_months_values(stats)     

            case Period.ALL:
                if detailed:
                    pass
                else:
                    pass 
        
        return {'text':str(stats)}

fmtr = Formatter()
