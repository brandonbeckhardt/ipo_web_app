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

    time_to_expire = 60*60*24 #cache daily 

    thisWeekRange = DateHandling.getThisWeekRange()
    companyData = db().select(db.ipo_info.ALL, db.company_info.ALL, db.company_description.ALL,
        left=[
        db.company_info.on(db.company_info.uuid == db.ipo_info.company_id), 
        db.company_description.on(db.company_description.company_id == db.ipo_info.company_id)])
    logger.info('Number of companies pulled =' + str(len(companyData)))

    urlData = db((db.url_info.type == UrlTypes.PUBLIC_COMPANY_URL['enum'] 
        or db.url_info.type == UrlTypes.PRIVATE_COMPANY_URL['enum']
        or db.url_info.type == UrlTypes.BROKER_URL['enum']) and db.url_info.is_primary==True).select()
    
    urlHandler = UrlHandler(urlData, logger)
    matches = DataMatcher(textInput,match_all,companyData, logger).matches
    groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future"),("Previous IPOs","past")]
    return dict(message=T('IPO Matcher'),matches=matches,groups=groups,text_area_input=textInput,edit=edit,
        show_past=showPast, urlHandler=urlHandler)


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


