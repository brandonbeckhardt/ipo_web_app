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

import json
import os

no_input_text = "123__NO_INPUT_TEXT__123"

def index():
    redirect(URL('matcher'))

def matcher():
    text_input = None

    thisWeekRange = DateHandling.getThisWeekRange()
    thisWeekIpoInfo = db(db.ipo_info.date_week >= thisWeekRange[0] or db.ipo_info.date_week == 'future').select(db.ipo_info.ALL, db.company_info.ALL, db.company_description.ALL, join=[db.company_info.on(db.company_info.id == db.ipo_info.company_id), db.company_description.on(db.company_description.company_id == db.ipo_info.company_id)])

    print thisWeekIpoInfo
    for row in thisWeekIpoInfo:
        print DateHandling.getGroupFromDate(row.ipo_info.date_week)

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
    ipos = cache.disk('ipos', lambda: IpoFetcher().ipos, time_expire=time_to_expire)    
    companyData = cache.disk('companies', lambda: CompanyInformationFetcher(ipos).companies, time_expire=time_to_expire)    
    matches = DataMatcher(text_input,match_all,companyData).matches

    groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future")]
    return dict(message=T('IPO Matcher'),matches=matches,groups=groups,text_area_input=text_input)

def submit_keyword_input():

    variables={}
    if request.vars.post_form == "submit":
        variables['keyWords'] = request.vars.text_input
    elif request.vars.post_form =="match_all":
        variables['match_all'] = "true"
    redirect(URL('matcher',vars=variables))


def add_company():
    company_info = db.company_info
    company_info.data_source_id.writable = company_info.data_source_id.readable = False
    ipo_info = db.ipo_info
    ipo_info.data_source_id.writable = ipo_info.data_source_id.readable = False
    ipo_info.company_id.writable = ipo_info.company_id.readable = False
    description = db.company_description
    description.company_id.writable =  description.company_id.readable = False
    description.data_source_id.writable = description.data_source_id.readable = False
    record = db((db.company_info.id == request.args(0)) & (db.ipo_info.company_id == request.args(0)) & (db.company_description.company_id == request.args(0))).select().first()
    if record:
        message = 'Update company Information'
        dictRecord = {}
        # NOTE -- if any tables have attributes with the same name, need to manually choose which to update, otherwise there may be issues
        for key in record:
            for attribute in record[key]:
                if key == "company_info" or attribute != 'id':
                    dictRecord[attribute] = record[key][attribute]
        form=SQLFORM.factory(company_info,ipo_info, description, record=dictRecord, showid=False)
        if form.process().accepted:
            companyId = record.company_info.update_record(**db.company_info._filter_fields(form.vars))
            form.vars.company_id=companyId
            id = record.ipo_info.update_record(**db.ipo_info._filter_fields(form.vars))
            id = record.company_description.update_record(**db.company_description._filter_fields(form.vars))
            response.flash = 'form accepted'
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
    else: 
        message = 'Add new company'
        form=SQLFORM.factory(company_info,ipo_info, description)
        if form.process().accepted:
            companyId = db.company_info.insert(**db.company_info._filter_fields(form.vars))
            form.vars.company_id=companyId
            id = db.ipo_info.insert(**db.ipo_info._filter_fields(form.vars))
            id = db.company_description.insert(**db.company_description._filter_fields(form.vars))
            response.flash = 'form accepted'
        elif form.errors:
            response.flash = 'form has errors'
        else:
            response.flash = 'please fill the form'
    return dict(form=form, message=T(message))



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


