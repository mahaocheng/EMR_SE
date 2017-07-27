# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import web, datetime, os
import json
from bin import map
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer
from whoosh.analysis import Tokenizer, Token
from whoosh.qparser import QueryParser
from whoosh import qparser
import os, os.path
from whoosh import index
from jieba.analyse import ChineseAnalyzer
import pymssql
import jieba
import re
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# create index dir
indexdir = '/home/haohedata/github/EMR_SE/index'
if not os.path.exists(indexdir):
    os.mkdir(indexdir)

jieba.load_userdict(open("/home/haohedata/github/EMR_SE/dict/dict.txt"))
ix = open_dir(indexdir)
searcher = ix.searcher()
parser = QueryParser("FJBNAME", ix.schema ,group=qparser.OrGroup)
urls = (
    '/', 'Index',
    '/hello', 'SayHello',
    '/image', 'Upload',
    '/game', 'GameEngine',
    '/entry', 'Entry'
    )

app = web.application(urls, locals())

# little hack so that debug mode works with sessions
if web.config.get('_session') is None:
    store = web.session.DiskStore('sessions')
    session = web.session.Session(app, store,
                                  initializer={'room': None, 'name': 'Jedi'})
    web.config._session = session
else:
    session = web.config._session
    
render = web.template.render('templates/', base="layout")

class Index:
    def GET(self):
        return render.index()


class SayHello:
    def GET(self):
        return render.hello_form()
    def POST(self):
        form = web.input(name="Nobody", greet="hello")
        q = parser.parse("".join(jieba.lcut(form.greet, cut_all=True)))
        results = searcher.search(q)
        FPRN_list = []
	for hit in results:
	    FPRN_list.append(hit['FJBNAME'])
            FPRN_list.append(hit['Bingqu'])
            FPRN_list.append(hit['FPRN'])
        output = json.dumps(FPRN_list, ensure_ascii = False, encoding = 'utf-8')
        if form.name == '':
            form.name = "Nobody"
        if form.greet == '':
            form.greet = "Hello"
        greeting = "%s, %s" % (output, form.name)
        return render.hello(greeting = greeting)


class Upload:
    ''' using cgi to upload and show image '''
    def GET(self):
        return render.upload_form()
    def POST(self):
        form = web.input(myfile={})
        # web.debug(form['myfile'].file.read())
        # get the folder name
        upload_time = datetime.datetime.now().strftime("%Y-%m-%d")
        # create the folder
        folder = os.path.join('./static', upload_time)
        if not os.access(folder, 1):
            os.mkdir(folder)
        # get the file name
        filename = os.path.join(folder, form['myfile'].filename)
        print(type(form['myfile']))
        with open(filename, 'wb') as f:
            f.write(form['myfile'].file.read())
            f.close()
        return render.show(filename = filename)


class count:
    def GET(self):
        session.count += 1
        return str(session.count)


class reset:
    def GET(self):
        session.kill()
        return ""


class Entry(object):
    def GET(self):
        return render.entry()
    def POST(self):
        form = web.input(name="Jedi")
        if form.name != '':
            session.name = form.name
        session.room = map.START
        #session.description = session.room.description
        web.seeother("/game")
    

class GameEngine(object):
    def GET(self):
        if session.room:
            return render.show_room(room=session.room, name=session.name)
        else:
            # why is there here? do you need it?
            return render.you_died()

    def POST(self):
        form = web.input(action=None)
        # there is a bug here, can you fix it?
        web.debug(session.room.name)
        if session.room and session.room.name != "The End" and form.action:
            session.room = session.room.go(form.action)

        web.seeother("/game")

if __name__ == "__main__":
    app.run()
