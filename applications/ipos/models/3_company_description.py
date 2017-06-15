import uuid
# Create 
db.define_table('company_description',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('created_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('description',type='string',notnull=True),
                    Field('company_id',length=64,notnull=True),
                    Field('data_migration_id',length=64),
                    format='%(description)s'
                   )

db.executesql('CREATE INDEX IF NOT EXISTS COMPANY_DESCRIPTION_UUID_IDX ON company_description (uuid);')
db.executesql('CREATE INDEX IF NOT EXISTS COMPANY_DESCRIPTION_data_migration_IDX ON company_description (data_migration_id);')

db.company_description._after_insert.append(lambda f, id: db(db.company_description.id == id).update_naive(modified_on=request.now))
db.company_description._after_update.append(lambda s, f: updateModifiedOnIfModifiedOnNotUpdated(s,f)) 

db.company_description.company_id.requires=IS_IN_DB(db,'company_info.uuid','%(name)')

def updateModifiedOnIfModifiedOnNotUpdated(s,f):
    for id in [r.id for r in s.select()]:
        db(db.company_description.id == id).update_naive(modified_on=request.now)