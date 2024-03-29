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
        dataMigrationUuid = str(uuid.uuid4())
        db.data_migration.insert(uuid=dataMigrationUuid, source='export',type=[DataSourceTypes.DATA_MIGRATION, DataSourceTypes.ALL])
        for table in db.tables:
            if 'uuid' in db[table].fields and 'data_migration_id' in db[table].fields:
                db(db[table].data_migration_id == None).update(data_migration_id=dataMigrationUuid)
        s = StringIO.StringIO()
        timeStr = str(DateHandling.dateTimeFormattedForFiles(DateHandling.today()))
        filename = 'data_migration_'+dataMigrationUuid +'_' + timeStr + '.csv'
        db.export_to_csv_file(open('applications/ipos/exports/'+filename,'wb'))
        db.export_to_csv_file(s)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-disposition']='attachment; filename='+filename
        return s.getvalue()
    else:
        redirect(URL('default','matcher'))                           
        return

# Note this is automatically wrapped in try, catch with proper committing and rollback as per 
# http://web2py.com/books/default/chapter/32/06/the-database-abstraction-layer#commit-and-rollback
def import_and_sync():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':
        form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
        if form.process().accepted:
            for table in db.tables:
                if 'uuid' in db[table].fields and ('data_migration_id' in db[table].fields or table =='data_migration'):
                    db(db[table].id != None).delete()
            db.import_from_csv_file(form.vars.data.file,unique=False)
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
        company_info.description.widget=lambda field, value: SQLFORM.widgets.text.widget(field, value, _class="description_textarea")

        ipo_info = db.ipo_info
        ipo_info.data_migration_id.writable = ipo_info.data_migration_id.readable = False
        ipo_info.company_id.writable = ipo_info.company_id.readable = False
        ipo_info.uuid.writable = ipo_info.uuid.readable = False
        ipo_info.date_week.widget=SQLFORM.widgets.date.widget

        data_sources = db.data_sources
        # data_sources.sources.widget=lambda field, value: SQLFORM.widgets.text.widget(field, value, _class="description_textarea")

        record = db(db.company_info.uuid == request.args(0)).select(db.ipo_info.ALL, db.company_info.ALL, db.data_sources.ALL,
        left=[db.company_info.on(db.company_info.uuid == db.ipo_info.company_id), db.data_sources.on(db.ipo_info.company_id == db.data_sources.company_id) ]).first()

        if record:
            message = 'Update company Information'
            dictRecord = {}
            # NOTE -- if any tables have attributes with the same name, need to manually choose which to update, otherwise there may be issues
            for key in record:
                for attribute in record[key]:
                    if key == "company_info" or attribute != 'id':
                        dictRecord[attribute] = record[key][attribute]
            form=SQLFORM.factory(company_info, ipo_info, data_sources, record=dictRecord, showid=False, _class='add_or_edit_company', formstyle='table2cols')
            url_info = db((db.url_info.reference_id == record.company_info.uuid or db.url_info.reference_id == record.ipo_info.uuid) and (db.url_info.is_primary == True)).select(orderby=db.url_info.created_on)
            add_custom_fields(form, url_info, record.company_info.uuid, record.ipo_info.uuid)
            if form.process().accepted:
                form.vars.company_id=form.vars.uuid
                record.company_info.update_record(**db.company_info._filter_fields(form.vars))
                form.vars.company_id = record.company_info.uuid #get the company's uuid5
                ipo_info_uuid = ""
                if record.ipo_info.uuid:
                    record.ipo_info.update_record(**db.ipo_info._filter_fields(form.vars))
                    ipo_info_uuid = record.ipo_info.uuid
                else:
                    ipo_id = db.ipo_info.insert(**db.ipo_info._filter_fields(form.vars))
                    ipo_info_uuid = db(db.ipo_info.id == ipo_id).select(db.ipo_info.uuid).first().uuid #get the ipo uuid
                if record.data_sources.uuid:
                    record.data_sources.update_record(**db.data_sources._filter_fields(form.vars))
                elif form.vars.sources != "":
                    db.data_sources.insert(**db.data_sources._filter_fields(form.vars))
                save_custom_field_values(form, url_info, record.company_info.uuid, ipo_info_uuid)

                response.flash = 'form accepted'
            elif form.errors:
                response.flash = 'form has errors'
            else:
                response.flash = 'please fill the form'
        else: 
            message = 'Add new company'
            form=SQLFORM.factory(company_info,ipo_info, data_sources, _class='add_or_edit_company', formstyle='table2cols')
            add_custom_fields(form, False, None, None)

            if form.process().accepted:
                company_id = db.company_info.insert(**db.company_info._filter_fields(form.vars))
                form.vars.company_id = db(db.company_info.id == company_id).select(db.company_info.uuid).first().uuid #get the company's uuid
                ipo_id = db.ipo_info.insert(**db.ipo_info._filter_fields(form.vars))
                ipo_info_uuid = ""
                if form.vars.broker_url and form.vars.broker_url != "":
                    ipo_info_uuid = db(db.ipo_info.id == ipo_id).select(db.ipo_info.uuid).first().uuid #get the ipo uuid
                db.data_sources.insert(**db.data_sources._filter_fields(form.vars))
                save_custom_field_values(form, None, form.vars.company_id, ipo_info_uuid)
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
                if url_item.type == UrlTypes.PRIVATE_COMPANY_URL['enum']:
                    if url_item.url != form.vars.private_url:
                        if form.vars.private_url != "":
                            url_item.update_record(url = form.vars.private_url)
                        else:
                            url_item.delete_record()
                    private_company_handled = True
            if url_item.reference_id == ipo_reference and url_item.is_primary:
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
        db.url_info.insert(url = form.vars.private_url, is_primary=True, reference_id = company_reference,
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
                if url_item.type == UrlTypes.PRIVATE_COMPANY_URL['enum']:
                    private_company_value = url_item.url
            if url_item.reference_id == ipo_reference and url_item.is_primary:
                if url_item.type == UrlTypes.BROKER_URL['enum']:
                    broker_value = url_item.url
    
    customVarsOffset = 2
    public_url_label = TR(LABEL('Public Company URL:'))
    public_url_input = TR(INPUT(_name='public_url',_type='text',_value=public_company_value))
    form[0].insert(len(form[0])-customVarsOffset, public_url_label)
    form[0].insert(len(form[0])-customVarsOffset, public_url_input)

    private_url_label = TR(LABEL('Private Company URL:'))
    private_url_input = TR(INPUT(_name='private_url',_type='text',_value=private_company_value))
    form[0].insert(len(form[0])-customVarsOffset, private_url_label)
    form[0].insert(len(form[0])-customVarsOffset, private_url_input)

    broker_url_label = TR(LABEL('Broker Company URL:'))
    broker_url_input = TR(INPUT(_name='broker_url',_type='text',_value=broker_value))
    form[0].insert(len(form[0])-customVarsOffset, broker_url_label)
    form[0].insert(len(form[0])-customVarsOffset, broker_url_input)


def delete_company():
    if request.cookies.has_key('authenticate') and request.cookies['authenticate'].value == 'true':
        variables = {}
        if request.vars.uuid:
            companyUuid = request.vars.uuid
            db(db.ipo_info.company_id == companyUuid).delete()
            db(db.company_info.uuid == companyUuid).delete()
        variables['edit'] = "true"
        redirect(URL('default','matcher',vars=variables))
    else:
        redirect(URL('default','matcher'))
