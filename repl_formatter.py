from aiogram.enums import ParseMode
from db import Period

class Formatter():
    def __init__(self) -> None:
        pass
    
    def _get_total_str(self, stats:list) -> str:
        return str(stats[0]['totalValue'])
        
    def format_stats(self, stats: list, period: Period, detailed: bool) -> dict:
        if len(stats) == 0:
            return {'text': 'Нет записей'}
        
        md2_reply = ''
        match period:
            case Period.DAY | Period.WEEK | Period.MONTH:
                if detailed:
                    data = [ [row['_id']['cat_name'], row['totalValue']] for row in stats]
                    data.sort(key=lambda x: x[0])
                    for line in data:
                        md2_reply += f'*{line[0]}* {line[1]} \n'
                    return {'text': md2_reply, 'parse_mode':ParseMode.MARKDOWN_V2}
                else:
                    return {'text':self._get_total_str(stats)}

            case Period.YEAR:
                if detailed:
                    pass    
                else:
                    data = [ [row['_id']['month'], row['totalValue']] for row in stats]        
                    md2_reply = f'*{stats[0]['_id']['year']}*\n'
                    for line in data:
                        md2_reply += f'*{line[0]}*:  {line[1]} \n'

                
                return {'text': md2_reply, 'parse_mode':ParseMode.MARKDOWN_V2}

            case Period.ALL:
                pass
        
        return {'text':str(stats)}

fmtr = Formatter()
