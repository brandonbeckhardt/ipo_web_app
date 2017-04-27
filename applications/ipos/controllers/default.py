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

import json
import os

no_input_text = "123__NO_INPUT_TEXT__123"

def index():
    redirect(URL('matcher'))

def matcher():
    text_input = None

    search_future=False
    match_all=False
    if request.vars.has_key('search_future') and request.vars['search_future']:
        search_future = True
    if request.vars.has_key('match_all') and request.vars['match_all'] == "true":
        match_all = True
        search_future = True

    if request.vars.has_key('keyWords') and request.vars['keyWords']:
        text_input = request.vars['keyWords']
    else:
        filepath = os.path.join(request.folder, 'uploads', 'keyWords.txt')
        with open(filepath, 'r') as text_input_file:
            text_input = text_input_file.read()

    time_to_expire = 60*60*24 #cache daily
    ipos = cache.disk('ipos', lambda: IpoFetcher().ipos, time_expire=time_to_expire)    
    companyData = cache.disk('companies', lambda: CompanyInformationFetcher(ipos).companies, time_expire=time_to_expire)    
    matches = DataMatcher(text_input,search_future,match_all,companyData).matches

    groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future")]
    return dict(message=T('IPO Matcher'),matches=matches,groups=groups,text_area_input=text_input,search_future=search_future)

def submit_keyword_input():
    variables={}
    if request.vars.post_form == "submit":
        variables['keyWords'] = request.vars.text_input
        if request.vars.search_future:
            variables['search_future']='true'
    elif request.vars.post_form =="match_all":
        variables['match_all'] = "true"
        variables['search_future']='true'
    redirect(URL('matcher',vars=variables))


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


