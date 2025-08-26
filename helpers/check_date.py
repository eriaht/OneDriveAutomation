from datetime import datetime
from dateutil.relativedelta import relativedelta

def check_date(date, years_older_than=2):
    date_obj = datetime.strptime(date, "%m/%d/%y")
    date_years_ago = datetime.today() - relativedelta(years=years_older_than)

    if date_obj < date_years_ago:
        return False
    
    return True