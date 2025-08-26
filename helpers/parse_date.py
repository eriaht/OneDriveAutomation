import re

def parse_date(date):
    match = re.search(r"\d{2}/\d{2}/\d{2}", date)
    if match:
        first_date = match.group()
        return first_date
    return None