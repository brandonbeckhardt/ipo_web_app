# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------

from IpoFetcher import IpoFetcher
from CompanyInformationFetcher import CompanyInformationFetcher
from DataMatcher import DataMatcher
from DateHandling import DateHandling
from Enums import DataSourceTypes
from Enums import UrlTypes
from UrlHandler import UrlHandler
from UrlHandler import UrlResults
from collections import namedtuple
from data_model.Match import MatchObject
from operator import itemgetter

import json
import os
import StringIO
import uuid


import logging
logger = logging.getLogger("web2py.app.ipos")
logger.setLevel(logging.DEBUG)

no_input_text = "123__NO_INPUT_TEXT__123"

def index():
    redirect(URL('matcher'))

def matcher():
    textInput = None
    # open('test.csv', 'wb').write(str(db(db.company_info.id).select()))
    # db.export_to_csv_file(open('test2.csv', 'wb'))
    authenticated = False
    if request.cookies.has_key('authenticate'):
        if request.cookies['authenticate'].value == 'true':
            authenticated = True

    authenticated = False
    if request.cookies.has_key('authenticate'):
        if request.cookies['authenticate'].value == 'true':
            authenticated = True

    match_all=False
    if request.vars.has_key('match_all') and request.vars['match_all'] == "true":
        match_all = True

    edit = False
    if request.vars.has_key('edit') and request.vars['edit'] == "true" and authenticated:
        edit=True
        match_all = True

    showPast = False
    if request.vars.has_key('show_past') and request.vars['show_past'] == "true" and authenticated:
        showPast=True

    if request.vars.has_key('keyWords') and request.vars['keyWords']:
        textInput = request.vars['keyWords']
    else:
        filepath = os.path.join(request.folder, 'uploads', 'keyWords.txt')
        with open(filepath, 'r') as text_input_file:
            textInput = text_input_file.read()
            match_all = True

    time_to_expire = 60*60*24 #cache daily 

    companyData = db().select(db.ipo_info.ALL, db.company_info.ALL,
        left=[db.company_info.on(db.company_info.uuid == db.ipo_info.company_id)])
    logger.info('Number of companies pulled =' + str(len(companyData)))

    urlData = db((db.url_info.type == UrlTypes.PUBLIC_COMPANY_URL['enum'] 
        or db.url_info.type == UrlTypes.PRIVATE_COMPANY_URL['enum']
        or db.url_info.type == UrlTypes.BROKER_URL['enum']) and db.url_info.is_primary==True).select()

    urlResults = UrlHandler(urlData, logger).getResultsAsDict()
    matches = DataMatcher(textInput,match_all,companyData, logger).matches
    if len(matches["this_week"])==0 and len(matches["next_week"])==0 and len(matches["future"])==0 and len(matches["past"])>0 :
        groups=[("Previous IPOs","past"),("This Week", "this_week"),("Next Week","next_week"),("Future","future")]
    else:
        groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future"),("Previous IPOs","past")]
    return dict(message=T('IPO Matcher'),matches=matches,groups=groups,text_area_input=textInput,edit=edit,
        show_past=showPast, match_all=match_all, urlResults=urlResults,   jsFormat=jsFormat)

def dumpJson(itm):
    return json.dumps(itm)

def jsFormat(itm):
    return T(json.dumps(itm))

 # Will want to change how we send data in the future
def matcher_table():
    textInput = None
    # open('test.csv', 'wb').write(str(db(db.company_info.id).select()))
    # db.export_to_csv_file(open('test2.csv', 'wb'))
    authenticated = False
    if request.cookies.has_key('authenticate'):
        if request.cookies['authenticate'].value == 'true':
            authenticated = True

    authenticated = False
    if request.cookies.has_key('authenticate'):
        if request.cookies['authenticate'].value == 'true':
            authenticated = True

    edit = False
    if request.vars.has_key('edit') and request.vars['edit'] == "true" and authenticated:
        edit=True

    # urlData = db((db.url_info.type == UrlTypes.PUBLIC_COMPANY_URL['enum'] 
    #     or db.url_info.type == UrlTypes.PRIVATE_COMPANY_URL['enum']
    #     or db.url_info.type == UrlTypes.BROKER_URL['enum']) and db.url_info.is_primary==True).select()
    # urlHandler = UrlHandler(urlData, logger)
    
    matches = None
    if request.vars.has_key('matches') and request.vars['matches']:
        matches = json.loads(request.vars['matches'])
    group = None
    if request.vars.has_key('group') and request.vars['group']:
        group = json.loads(request.vars['group'])
    # sortBy = request.vars.sortBy
    # add asc

    if request.vars.has_key('sortBy') and request.vars['sortBy']:
        sortBy = request.vars['sortBy']
        reverse=False
        if request.vars.has_key('order') and request.vars['order']:
            if request.vars['order'] == 'desc':
                reverse = True

        logger.info('here')
        logger.info(matches)
        matches = sorted(matches, key=itemgetter(sortBy), reverse=reverse)

    return dict(matches=matches, group=group, edit=edit, urlResults=None, jsFormat=jsFormat)

def submit_keyword_input():
    variables={}
    if request.vars.post_form == "submit":
        variables['keyWords'] = request.vars.text_input
    elif request.vars.post_form =="match_all":
        variables['match_all'] = "true"
    redirect(URL('matcher',vars=variables))

def authenticate():
    variables={}
    myconf = AppConfig(reload=True)
    if request.vars.authentication_button == "login":
        if 'TEMP_LOGIN' in os.environ and 'TEMP_PW' in os.environ:
            if request.vars.username ==  os.environ['TEMP_LOGIN']:
                if request.vars.password == os.environ['TEMP_PW']:
                    response.cookies['authenticate'] = 'true'
                    response.cookies['authenticate']['expires'] = .5 * 3600 #1/2 hour
                    response.cookies['authenticate']['secure'] = True
                    response.cookies['authenticate']['path'] = '/'
                    variables['edit'] = "true"
    elif request.vars.authentication_button == "logout":
        response.cookies['authenticate'] = 'false'
        response.cookies['authenticate']['path'] = '/'
    redirect(URL('matcher',vars=variables))

def auth():
    if not request.is_https:
        redirect(URL(scheme='https', args=request.args, vars=request.vars))
    else:
        return dict(message=T('Login'))

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


