import datetime
import json
import random
import sys

import secrets
import requests
from pickledb import pickledb

import slackMenu

def postToSlack(message):
    print('Posting to slack: {}'.format(message))
    response = requests.post(
        secrets.getSlackWebhookUrl(),
        data=json.dumps(message),
        headers={'Content-Type': 'application/json'}
    )

def postAny():
    db = pickledb.load('menu.json', False)
    menus = db.getall()
    menu = db.get(random.choice(list(menus)))
    menu = [slackMenu.addEmojis(food) for food in menu]
    if menu:
        slack_data = {'text': '\n'.join(menu)}
        postToSlack(slack_data)

def main():
    db = pickledb.load('menu.json', False)
    menu = db.get(str(datetime.date.today()))
    if menu:
        menu = [slackMenu.addEmojis(food) for food in menu]
        slack_data = {'text': '\n'.join(menu)}
    else:
        slack_data = {'text': ':warning: Enginn matseðill fannst fyrir daginn í dag!'}
    postToSlack(slack_data)
    


if __name__ == "__main__":
    sys.exit(main())