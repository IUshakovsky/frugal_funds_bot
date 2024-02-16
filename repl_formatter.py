from aiogram.enums import ParseMode
import locale
import calendar

from db import Period

class Formatter():
    def __init__(self) -> None:
        locale.setlocale(locale.LC_ALL, 'ru_RU')
    
    def _format_total_str(self, stats:list) -> dict:
        return {'text':str(stats[0]['totalValue'])} 

    def _format_cats_values(self, prefix: str, stats:list) -> dict:
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
   
    def _format_months_cats_values(self, stats: list) -> dict:
        data = [[row['id']['month'], row['id']['cat_name'], row['totalValue']] for row in stats]
        total = sum([r[2] for r in data])
        md2_reply = f"За *{stats[0]['_id']['year']}* год: {total} \n"
        data.sort(key=lambda x: (x[0], -x[2])) 
        for line in data:
            pass
            
        return {'text': md2_reply, 'parse_mode':ParseMode.MARKDOWN_V2}     
            
    
    def format_stats(self, stats: list, period: Period, detailed: bool) -> dict:
        if len(stats) == 0:
            return {'text': 'Нет записей'}
        
        match period:
            case Period.DAY:
                if detailed:
                    return self._format_cats_values(f'*Сегодня*', stats)
                else:
                    return self._format_total_str(stats)
            
            case Period.WEEK: 
                if detailed:
                    return self._format_cats_values(f'*За неделю*', stats)
                else:
                    return self._format_total_str(stats)

            case Period.MONTH:
                if detailed:
                    return self._format_cats_values(f'*За месяц*', stats)
                else:
                    return self._format_total_str(stats)

            case Period.YEAR:
                if detailed:
                    return self._format_months_cats_values(stats)    
                else:
                    return self._format_months_values(stats)     

            case Period.ALL:
                pass
        
        return {'text':str(stats)}

fmtr = Formatter()
