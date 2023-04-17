import re
import datetime

ftext = lambda txt: txt.lower().replace("ö", "oe").replace("ä", "ae").replace("ü","ue")

getnums = lambda text: set([int(it) for it in re.findall("\\b\\d{1,5}\\b", text) if int(it) > 0])

fdate= lambda datestring: "\'{yea}-{mon}-{day}\'".format(yea = datestring[6:], mon = datestring[3:5], day = datestring[0:2])

get_year = lambda datestring: int(datestring[:4])

now_year = lambda: datetime.date.today().year

def split_fee(amount, fee):
    if amount > fee:
        donation = amount - fee
        amount = fee
    else:
        donation = 0

    return amount, donation
