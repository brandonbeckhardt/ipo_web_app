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
    text_input = None
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

    if request.vars.has_key('keyWords') and request.vars['keyWords']:
        text_input = request.vars['keyWords']
    else:
        filepath = os.path.join(request.folder, 'uploads', 'keyWords.txt')
        with open(filepath, 'r') as text_input_file:
            text_input = text_input_file.read()

    time_to_expire = 60*60*24 #cache daily
    # ipos = cache.disk('ipos', lambda: IpoFetcher().ipos, time_expire=time_to_expire)    
    # companyData = cache.disk('companies', lambda: CompanyInformationFetcher(ipos).companies, time_expire=time_to_expire)    

    thisWeekRange = DateHandling.getThisWeekRange()
    # companyData = db(db.ipo_info.date_week >= thisWeekRange[0] or db.ipo_info.date_week == 'future').select(db.ipo_info.ALL, db.company_info.ALL, db.company_description.ALL, join=[db.company_info.on(db.company_info.id == db.ipo_info.company_id), db.company_description.on(db.company_description.company_id == db.ipo_info.company_id)])
    companyData = db().select(db.ipo_info.ALL, db.company_info.ALL, db.company_description.ALL, join=[db.company_info.on(db.company_info.uuid == db.ipo_info.company_id), db.company_description.on(db.company_description.company_id == db.ipo_info.company_id)])
    matches = DataMatcher(text_input,match_all,companyData).matches

    groups=[("This Week", "this_week"),("Next Week","next_week"),("Future","future")]
    return dict(message=T('IPO Matcher'),matches=matches,groups=groups,text_area_input=text_input,edit=edit)

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
        if request.vars.username == myconf.get('temp_auth.username'):
            if request.vars.password == myconf.get('temp_auth.pw'):
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
    return dict(message=T('Login'))

# Create new data source and have all data reference this data source.  From there, export db
def export():
    dataSourceUuid = str(uuid.uuid4())
    db.data_migration.insert(uuid=dataSourceUuid, source='export',type=[DataSourceTypes.DATA_MIGRATION, DataSourceTypes.ALL])
    for table in db.tables:
        if table == 'data_migration':
            db(db[table].id>0).update(export_time=request.now)
        elif 'data_migration_id' in db[table].fields:
            db(db[table].id > 0).update(data_migration_id=dataSourceUuid)
    s = StringIO.StringIO()
    db.export_to_csv_file(s)
    response.headers['Content-Type'] = 'text/csv'
    return s.getvalue()

def import_and_sync():
    form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
    if form.process().accepted:
        db.import_from_csv_file(form.vars.data.file,unique=False)

        #delete all old sets of data sources. old means was not uploaded just now
        exportTime = db(db.data_migration).select(db.data_migration.export_time, db.data_migration.uuid, orderby=~db.data_migration.modified_on).first().export_time
        if exportTime: #If there's no export time, it's not coming from a migration, want to avoid doing anything
            db(db.data_migration.export_time != exportTime).delete() # delete all migration rows that were not part of this export                 

            #Get the newest datasource
            newDataSourceUUID = db(db.data_migration).select(db.data_migration.uuid,orderby=~db.data_migration.created_time).first().uuid

            #Delete all data referencing old data_migration
            for table in db.tables:
                if 'uuid' in db[table].fields and ('data_migration_id' in db[table].fields or table =='data_migration'):
                    if table != 'data_migration':
                        #Delete all records that arent' referencing the most recent data_migration_id
                        db(db[table].data_migration_id != newDataSourceUUID).delete()

                    #For every uuid, delete all but the latest
                    #This is precautionary, in case we happen to be uploading the exact same state of the db.  Avoids duplicates
                    
                    #Note both forms of deletion are necessary because they handle the cases in which a record was deleted, 
                    #a record was added, a duplicate record has been imported
                    
                    items = db(db[table]).select(db[table].id, db[table].uuid, orderby=db[table].uuid | ~db[table].modified_on)
                    if items and len(items) > 0:
                        prevUuid = None
                        for item in items:
                            if item.uuid != prevUuid:
                                prevUuid = item.uuid
                                db((db[table].uuid==item.uuid) & (db[table].id!=item.id)).delete()

    return dict(form=form)

#Note at the moment, we can reference UUID for company_info in form.vars without any issues.
#If we change ordering of how things are represented/consumed in form, may cause issues
def add_company():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':

        company_info = db.company_info
        company_info.data_migration_id.writable = company_info.data_migration_id.readable = False
        company_info.uuid.writable = company_info.uuid.readable = False

        ipo_info = db.ipo_info
        ipo_info.data_migration_id.writable = ipo_info.data_migration_id.readable = False
        ipo_info.company_id.writable = ipo_info.company_id.readable = False
        ipo_info.uuid.writable = ipo_info.uuid.readable = False

        description = db.company_description
        description.company_id.writable =  description.company_id.readable = False
        description.data_migration_id.writable = description.data_migration_id.readable = False
        description.uuid.writable = description.uuid.readable = False
        
        record = db((db.company_info.uuid == request.args(0)) & (db.ipo_info.company_id == request.args(0)) & (db.company_description.company_id == request.args(0))).select().first()
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
                form.vars.company_id=form.vars.uuid
                id = record.company_info.update_record(**db.company_info._filter_fields(form.vars))
                form.vars.company_id = db(db.company_info.id == id).select(db.company_info.uuid).first().uuid #get the company's uuid
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
                id = db.company_info.insert(**db.company_info._filter_fields(form.vars))
                form.vars.company_id = db(db.company_info.id == id).select(db.company_info.uuid).first().uuid #get the company's uuid
                id = db.ipo_info.insert(**db.ipo_info._filter_fields(form.vars))
                id = db.company_description.insert(**db.company_description._filter_fields(form.vars))
                response.flash = 'form accepted'
            elif form.errors:
                response.flash = 'form has errors'
            else:
                response.flash = 'please fill the form'
    else:
        redirect(URL('matcher'))
    return dict(form=form, message=T(message))


def delete_company():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':
        variables = {}
        if request.vars.uuid:
            companyUuid = request.vars.uuid
            db(db.ipo_info.company_id == companyUuid).delete()
            db(db.company_description.company_id == companyUuid).delete()
            db(db.company_info.uuid == companyUuid).delete()
        variables['edit'] = "true"
        redirect(URL('matcher',vars=variables))
    else:
        redirect(URL('matcher'))

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


