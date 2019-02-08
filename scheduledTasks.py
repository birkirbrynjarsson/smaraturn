#!/usr/bin/env python

import os
from pytz import utc
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

import getmail
import menuParser
import slackbot

def setup(scheduler):    
    scheduler.add_job(postToSlack, 'cron', day_of_week='mon-fri', hour=11, minute=0)
    scheduler.add_job(getMailandParseMenus, 'cron', day_of_week='mon-fri', hour=9, minute=30)
    scheduler.add_job(getMailandParseMenus, 'cron', day_of_week='mon', hour=10, minute=55)
    scheduler.add_job(stashMenus, 'cron', day=1, hour=1, minute=0)

def parseMenus():
    dirpath = 'attachments/'
    for filename in os.listdir(dirpath):
        doc = open(dirpath + filename, 'rb')
        menu = menuParser.parseDocx(doc)
        menuParser.storeData(menu)

def getMailandParseMenus():
    print('Getting mail...')
    getmail.main()
    print('Parsing menus...')
    parseMenus()

def stashMenus():
    print('Stashing menus, moving from attachments/ to menus/')
    wd = os.getcwd()
    os.system('mv {}/attachments/* {}/menus/'.format(wd, wd))

def postToSlack():
    slackbot.main()

# def main():
#     scheduler = BlockingScheduler(timezone=utc)
#     setup(scheduler)
#     scheduler.start()

# if __name__ == '__main__':
#     sys.exit(main())