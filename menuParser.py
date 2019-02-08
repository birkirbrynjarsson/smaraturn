import datetime
import calendar
import re
import sys

import argparse
import docx
from pickledb import pickledb # fork of pickledb that supports UTF-8

reverseCalendar = {v: k for k,v in enumerate(calendar.month_abbr)}
icelandicCalendar = {
    'jan': 'Jan', 'feb': 'Feb', 'mar': 'Mar', 'apr': 'Apr', 'mai': 'May', 'jún': 'Jun',
    'júl': 'Jul', 'ágú': 'Aug', 'sep': 'Sep', 'okt': 'Oct', 'nóv': 'Nov', 'des': 'Dec'
}


def parseArguments():
    parser = argparse.ArgumentParser(
        prog='Mulakaffi docx menu parser',
        description='Takes a docx file, weekly cafeteria menu from Múlakaffi as input, parses it and saves in database',
    )
    parser.add_argument('file', type=argparse.FileType('rb'), help='input docx weekly cafeteria-menu file')
    return parser.parse_args()


# Creates a date object from string like: 'þriðjudagur 13. Nóvember'
def getDateFromMenu(dateString):
    now = datetime.date.today()
    date = datetime.date(now.year, now.month, now.day)
    for substring in dateString.replace(".", " ").split():
        if substring[:3].lower() in icelandicCalendar:
            date = date.replace(month=reverseCalendar[icelandicCalendar[substring[:3].lower()]])
        elif substring[:3] in calendar.month_abbr:
            date = date.replace(month=reverseCalendar[substring[:3]])
    for substring in dateString.replace(".", " ").split():
        if substring.isnumeric():
            date = date.replace(day=int(substring))
    return date


# Parse food string, remove invalid and fix exceptions
def parseFood(food):
    food = " ".join(food.split()) # Remove any double spaces, tabs, non breaking spaces (\xA0) etc.
    
    # Check for closed
    closedString = 'Lokað í dag!'
    if 'lokað' in food.strip().lower():
        return closedString

    # Check for 'eða'
    if food.lower() == 'eða':
        return 'eða'
    
    # Check for 'V = Vegan' explanation
    if any(x in food.strip().lower() for x in ['v - vegan', 'vegan - v', 'v = vegan', 'vegan = v']):
        return None
    
    # Replace any 'V' for 'v', (vegan)
    if food[-2:] == " V":
        food = food[:-2] + ' v'  
    food = food.replace(" V ", " v ")
    
    # Fix any unwanted recognized typos
    food = food.replace(",,", "„")
    food = re.sub(r'(?<=[.,”])(?=[^\s])', r' ', food)

    return food


def storeData(data):
    db = pickledb.load('menu.json', False)
    for key in data:
        db.set(str(key), data[key])
    db.dump()


def parseDocx(docxFile):
    doc = docx.Document(docxFile)
    # Loop through paragraphs in menu (docx)
    date = None
    menu = {}
    for paragraph in doc.paragraphs:
        if "dagur" in paragraph.text:
            date = getDateFromMenu(paragraph.text)
            menu[date] = []
        elif date and paragraph.text:
            food = parseFood(paragraph.text)
            if food:
                if food != 'eða':
                    menu[date].append(food)
            else:
                date = None
                continue
        if not paragraph.text:
            date = None
            continue
    
    return menu

def main():
    # Parse input arguments
    args = parseArguments()

    menu = parseDocx(args.file)
    storeData(menu)


if __name__ == "__main__":
    sys.exit(main())