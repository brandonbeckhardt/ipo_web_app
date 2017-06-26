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

import json
import os
import StringIO
import uuid


import logging
logger = logging.getLogger("web2py.app.ipos")
logger.setLevel(logging.DEBUG)

# Create new data source and have all data reference this data source.  From there, export db
def export():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':
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
    else:
        redirect(URL('default','matcher'))                           
        return

def import_and_sync():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':
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
    else:
        redirect(URL('default','matcher'))                           
        return
    

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
        ipo_info.date_week.widget=SQLFORM.widgets.date.widget

        description = db.company_description
        description.company_id.writable =  description.company_id.readable = False
        description.data_migration_id.writable = description.data_migration_id.readable = False
        description.uuid.writable = description.uuid.readable = False
        description.description.widget=lambda field, value: SQLFORM.widgets.text.widget(field, value, _class="company_description_textarea")

        record = db((db.company_info.uuid == request.args(0)) & (db.ipo_info.company_id == request.args(0)) & (db.company_description.company_id == request.args(0))).select().first()
        if record:
            message = 'Update company Information'
            dictRecord = {}
            # NOTE -- if any tables have attributes with the same name, need to manually choose which to update, otherwise there may be issues
            for key in record:
                for attribute in record[key]:
                    if key == "company_info" or attribute != 'id':
                        dictRecord[attribute] = record[key][attribute]
            form=SQLFORM.factory(company_info,ipo_info, description, record=dictRecord, showid=False, _class='add_or_edit_company', formstyle='table2cols')
            url_info = db((db.url_info.reference_id == record.company_info.uuid or db.url_info.reference_id == record.ipo_info.uuid) and (db.url_info.is_primary == True)).select(orderby=db.url_info.created_on)
            add_custom_fields(form, url_info, record.company_info.uuid, record.ipo_info.uuid)
            if form.process().accepted:
                form.vars.company_id=form.vars.uuid
                id = record.company_info.update_record(**db.company_info._filter_fields(form.vars))
                form.vars.company_id = record.company_info.uuid #get the company's uuid5
                id = record.ipo_info.update_record(**db.ipo_info._filter_fields(form.vars))
                id = record.company_description.update_record(**db.company_description._filter_fields(form.vars))

                save_custom_field_values(form, url_info, record.company_info.uuid, record.ipo_info.uuid)

                response.flash = 'form accepted'
            elif form.errors:
                response.flash = 'form has errors'
            else:
                response.flash = 'please fill the form'
        else: 
            message = 'Add new company'
            form=SQLFORM.factory(company_info,ipo_info, description, _class='add_or_edit_company', formstyle='table2cols')
            add_custom_fields(form, False, None, None)

            if form.process().accepted:
                id = db.company_info.insert(**db.company_info._filter_fields(form.vars))
                form.vars.company_id = db(db.company_info.id == id).select(db.company_info.uuid).first().uuid #get the company's uuid
                id = db.ipo_info.insert(**db.ipo_info._filter_fields(form.vars))
                id = db.company_description.insert(**db.company_description._filter_fields(form.vars))
                save_custom_field_values(form, None, record.company_info.uuid, record.ipo_info.uuid)
                response.flash = 'Form accepted'
            elif form.errors:
                response.flash = 'Form has errors and was not submitted - please see below for details'
    else:
        redirect(URL('default','matcher'))
    return dict(form=form, message=T(message))



def save_custom_field_values(form, url_info, company_reference, ipo_reference):
    public_company_handled = False
    private_company_handled = False
    broker_handled = False

    if url_info: #Coming from an update
        for url_item in url_info:
            if url_item.reference_id == company_reference and url_item.is_primary:
                if url_item.type == UrlTypes.PUBLIC_COMPANY_URL['enum']:
                    if url_item.url != form.vars.public_url:
                        if form.vars.public_url != "":
                            url_item.update_record(url=form.vars.public_url)
                        else:
                            url_item.delete_record()
                    public_company_handled = True
            if url_item.reference_id == ipo_reference and url_item.is_primary:
                if url_item.type == UrlTypes.PRIVATE_COMPANY_URL['enum']:
                    if url_item.url != form.vars.private_url:
                        if form.vars.private_url != "":
                            url_item.update_record(url = form.vars.private_url)
                        else:
                            url_item.delete_record()
                    private_company_handled = True
                if url_item.type == UrlTypes.BROKER_URL['enum']:
                    if url_item.url != form.vars.broker_url:
                        if form.vars.broker_url != "":
                            url_item.update_record(url = form.vars.broker_url)
                        else:
                            url_item.delete_record()
                    broker_handled = True

    if not public_company_handled and form.vars.public_url != "":
        db.url_info.insert(url = form.vars.public_url, is_primary=True, reference_id = company_reference,
            type=UrlTypes.PUBLIC_COMPANY_URL['enum'])
    if not private_company_handled and form.vars.private_url != "":
        db.url_info.insert(url = form.vars.private_url, is_primary=True, reference_id = ipo_reference,
                    type=UrlTypes.PRIVATE_COMPANY_URL['enum'])
    if not broker_handled and form.vars.broker_url != "":
        db.url_info.insert(url = form.vars.broker_url, is_primary=True, reference_id = ipo_reference,
            type=UrlTypes.BROKER_URL['enum']) 


def add_custom_fields(form, url_info, company_reference, ipo_reference):
    public_company_value = None
    private_company_value = None
    broker_value = None
    if url_info:
        for url_item in url_info:
            if url_item.reference_id == company_reference and url_item.is_primary:
                if url_item.type == UrlTypes.PUBLIC_COMPANY_URL['enum']:
                    public_company_value = url_item.url
            if url_item.reference_id == ipo_reference and url_item.is_primary:
                if url_item.type == UrlTypes.PRIVATE_COMPANY_URL['enum']:
                    private_company_value = url_item.url
                if url_item.type == UrlTypes.BROKER_URL['enum']:
                    broker_value = url_item.url
                
    public_url_label = TR(LABEL('Public Company URL:'))
    public_url_input = TR(INPUT(_name='public_url',_type='text',_value=public_company_value))
    form[0].insert(len(form[0])-4, public_url_label)
    form[0].insert(len(form[0])-4, public_url_input)

    private_url_label = TR(LABEL('Private Company URL:'))
    private_url_input = TR(INPUT(_name='private_url',_type='text',_value=private_company_value))
    form[0].insert(len(form[0])-4, private_url_label)
    form[0].insert(len(form[0])-4, private_url_input)

    broker_url_label = TR(LABEL('Broker Company URL:'))
    broker_url_input = TR(INPUT(_name='broker_url',_type='text',_value=broker_value))
    form[0].insert(len(form[0])-4, broker_url_label)
    form[0].insert(len(form[0])-4, broker_url_input)





def delete_company():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':
        variables = {}
        if request.vars.uuid:
            companyUuid = request.vars.uuid
            db(db.ipo_info.company_id == companyUuid).delete()
            db(db.company_description.company_id == companyUuid).delete()
            db(db.company_info.uuid == companyUuid).delete()
        variables['edit'] = "true"
        redirect(URL('default','matcher',vars=variables))
    else:
        redirect(URL('default','matcher'))
