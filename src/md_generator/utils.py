import re

def indent(text: str, amount: int = 4, char: str = " "):
    return ''.join([(char * amount) + l for l in text.splitlines(True)])

def escape(text: str, chars: str = '"\''):
    text = str(text)
    escape_chars = '\\' + chars
    result = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

    return result

def backtick_count(text: str, start = 1) -> int:
    found_ticks = {len(t) for t in re.findall(r"(`+)", str(text))}
    
    num_ticks = start
    while num_ticks in found_ticks:
        num_ticks += 1
    
    return num_ticks

def strbool(value: str):
    value = (value).lower()
    return value in ['true', 't', '1']

def strnum(num: str):
    try:
        return int(str(num))
    except ValueError:
        return float(str(num))
    except:
        return num
