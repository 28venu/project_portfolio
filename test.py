from datetime import date

month = str(date.today().month)
day = str(date.today().day)
year = str(date.today().year)

months = {
    '1': 'jan',
    '2': 'feb',
    '3': 'mar',
    '4': 'april',
    '5': 'may',
    '6': 'june',
    '7': 'july',
    '8': 'aug',
    '9': 'sep',
    '10': 'oct',
    '11': 'nov',
    '12': 'dec'
}


def today():
    return day+" "+months[month]+" "+year

# print(today())
