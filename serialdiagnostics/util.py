from datetime import datetime


def get_datestr(suffix, date=None):
    if date is None:
        date = datetime.now()
    return date.strftime('%y%m%d_%H%M%S_'+suffix)

