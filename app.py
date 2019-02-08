#!/usr/bin/env python

import atexit
import datetime
from pytz import utc
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request
from flask_restplus import abort, Api, Resource, reqparse, inputs

from pickledb import pickledb

import getmail
import menuParser
import scheduledTasks
import slackMenu

parser = reqparse.RequestParser()
parser.add_argument('slack', type=inputs.boolean, default=False, help='If true, decorates each dish on the menu with slack emojis')

scheduler = BackgroundScheduler(timezone=utc)
scheduledTasks.setup(scheduler)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

application = Flask(__name__)
application.config['JSON_AS_ASCII'] = False
api = Api(
    application,
    prefix='/api/v1',
    doc='/api/v1/swagger',
    version='1.0',
    title='Smáraturn API',
    description='A small side project by <a href="https://github.com/birkirbrynjarsson">Birkir Brynjarsson</a>, serving todays menu at Smáratorg Tower!',
    contact='birkir@birkir.is'
)

menus = api.namespace('menus', description='Access to the cafeteria food menu')
jobs = api.namespace('jobs', description='List scheduled jobs or execute them manually')


# Helper function to get menu by date, 404 error if not found
def getMenu(date):
    db = pickledb.load('menu.json', False)
    menu = db.get(date)
    if not menu:
        abort(404)
    return {date: menu}

def getWeekMenus(week):
    db = pickledb.load('menu.json', False)
    menuKeys = db.getall()
    menuKeys = [w for w in menuKeys if int(datetime.datetime.strptime(w, "%Y-%m-%d").strftime('%W')) == week]
    if not menuKeys:
        abort(404)
    menus = {}
    for key in menuKeys:
        menus[key] = db.get(key)
    return menus

def getAllMenus():
    db = pickledb.load('menu.json', False)
    menuKeys = db.getall()
    menus = {}
    for key in menuKeys:
        menus[key] = db.get(key)
    return menus
    
def addSlackEmojisToMenus(menus):
    for date in menus:
        menus[date] = [slackMenu.addEmojis(food) for food in menus[date]]
    return menus

# List of all menus
@menus.route('/')
class Menus(Resource):
    @api.expect(parser)
    def get(self):
        '''Get all menus'''
        slack = parser.parse_args()['slack']
        menus = addSlackEmojisToMenus(getAllMenus()) if slack else getAllMenus()
        return jsonify(menus)

@menus.route('/week')
class MenusWeek(Resource):
    @api.expect(parser)
    def get(self):
        '''Get this weeks menus'''
        slack = parser.parse_args()['slack']
        menus = getWeekMenus(datetime.date.today().isocalendar()[1])
        menus = addSlackEmojisToMenus(menus) if slack else menus
        return jsonify(menus)

@menus.route('/week/<int:week>')
@api.param('week', 'Week number, integer from 1-52')
class MenusWeekNr(Resource):
    @api.expect(parser)
    def get(self, week):
        '''Get a specific weeks menu by week number 1-52 (current calendar year)'''
        if week < 1 or 52 < week:
            abort(400, message='{} is not a valid week from 1-52'.format(week))
        slack = parser.parse_args()['slack']
        menus = getWeekMenus(week)
        menus = addSlackEmojisToMenus(menus) if slack else menus
        return jsonify(menus)
    

# Todays menu item
@menus.route('/today')
class MenuToday(Resource):
    @api.expect(parser)
    def get(self):
        '''Get todays menu'''
        today = str(datetime.date.today())
        slack = parser.parse_args()['slack']
        menu = addSlackEmojisToMenus(getMenu(today)) if slack else getMenu(today)
        return jsonify(menu)


def validateDate(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        abort(400, 'Incorrect date format {}, should be YYYY-MM-DD'.format(date))

# Single menu item, date e.g. '2018-10-30'
@menus.route('/<date>')
@api.param('date', 'Date format: YYYY-MM-DD, e.g {}'.format(str(datetime.date.today())))
class MenuByDate(Resource):
    @api.expect(parser)
    def get(self, date):
        '''Get menu by date in ISO format YYYY-MM-DD'''
        # Add zero padding fixing e.g 2018-9-3 to 2018-09-03
        validateDate(date)
        date = '-'.join([x.zfill(2) for x in date.split('-')])
        slack = parser.parse_args()['slack']
        menu = addSlackEmojisToMenus(getMenu(date)) if slack else getMenu(date)
        return jsonify(menu)

def parseDirectory(dirpath):
    totalFiles = 0
    for filename in os.listdir(dirpath):
        totalFiles += 1
        doc = open(dirpath + filename, 'rb')
        menu = menuParser.parseDocx(doc)
        menuParser.storeData(menu)
    return totalFiles

@jobs.route('/')
class Jobs(Resource):
    def get(self):
        '''Get list of all scheduled jobs'''
        jobs = scheduler.get_jobs()
        jobs = [str(job) for job  in jobs]
        return jsonify(jobs)

@jobs.route('/checkmail')
class Mail(Resource):
    def get(self):
        '''Check mail and save (docx) attachments from recognized sources onto the server'''
        getmail.main()
        return jsonify('Checked mail!')

@jobs.route('/parsemenus')
class MenuParser(Resource):
    def post(self):
        '''Parse all (docx) menus on the server and rebuild the database'''
        scheduledTasks.stashMenus()
        totalFiles = parseDirectory('menus/')
        return jsonify('Parsed {} docx menu files!'.format(totalFiles))




if __name__ == '__main__':
    application.run(debug=True)