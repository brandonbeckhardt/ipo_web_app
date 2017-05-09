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
from Enums import DataSourceTypes
from DateHandling import DateHandling

import json
import os

no_input_text = "123__NO_INPUT_TEXT__123"

def index():
    redirect(URL('matcher'))

def matcher():
    text_input = None

    match_all=False
    if request.vars.has_key('match_all') and request.vars['match_all'] == "true":
        match_all = True

    if request.vars.has_key('keyWords') and request.vars['keyWords']:
        text_input = request.vars['keyWords']
    else:
        filepath = os.path.join(request.folder, 'uploads', 'keyWords.txt')
        with open(filepath, 'r') as text_input_file:
            text_input = text_input_file.read()

    time_to_expire = 60*60*24 #cache daily 
    ipos = getIpos()
    # companyData = CompanyInformationFetcher(ipos).companies
    companyData = cache.disk('companies', lambda: CompanyInformationFetcher(ipos).companies, time_expire=time_to_expire)    
    matches = DataMatcher(text_input,match_all,companyData).matches

    groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future")]
    return dict(message=T('IPO Matcher'),matches=matches,groups=groups,text_area_input=text_input)

def getIpos():
    thisWeekRange = DateHandling.convertRangeToDateTimeExclusiveEndDate(DateHandling.getThisWeekRange())
    thisWeekIpoInfo = db(db.data_source.date_time >= thisWeekRange[0] and db.data_source.date_time < thisWeekRange[1]
        and DataSourceTypes.IPO.value in db.data_source.type and db.company_info.id == db.ipo_info.company_id).select()
    if thisWeekIpoInfo:
        return thisWeekIpoInfo
    else:
        ipos = cache.disk('ipos', lambda: IpoFetcher().ipos, time_expire=time_to_expire)  
        saveIpoAndCompanyData(ipo)
        return getIpos()


def createNewDataSource(source, type):
    return db.data_source.insert(source=source,type=type,date_time=datetime.today())

def saveIpoAndCompanyData(ipos):
    data_source_id = createNewDataSource("MarketWatch",[DataSourceTypes.IPO.value, DataSourceTypes.COMPANY.value])
    this_week_range = DateHandling.getThisWeekRange()
    next_week_range = DateHandling.getNextWeekRange()
    for group in ipos.keys():
        date_week = DateHandling.getDateWeekFromGroup(group)
        for company in ipos[group]:
            company_name = company[0]
            company_ticker = company[1]
            companyInDb = db(db.company_info.name==company_name).select().first()
            if not companyInDb: #if company doesn't exist, create it
                company_id = db.company_info.insert(name=company_name,data_source_id=data_source_id)
            else:
                company_id = companyInDb.id
            ipoInDb = db(db.ipo_info.company_id ==company_id).select().first()
            if not ipoInDb: #Save new IPO
                db.ipo_info.insert(company_id=company_id,data_source_id=data_source_id,
                    date_week=date_week,intended_ticker=company_ticker)
            else: #Update IPO info 
                ipoInDb.update_record(data_source_id=data_source_id,date_week=date_week,intended_ticker=company_ticker)



def submit_keyword_input():
    variables={}
    if request.vars.post_form == "submit":
        variables['keyWords'] = request.vars.text_input
    elif request.vars.post_form =="match_all":
        variables['match_all'] = "true"
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


