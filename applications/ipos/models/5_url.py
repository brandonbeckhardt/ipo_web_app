import uuid
# Create 
db.define_table('url_info',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('created_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('data_migration_id',length=64),
                    Field('reference_id',length=64,notnull=True),
                    Field('type',type='integer',notnull=True),
                    Field('is_primary',type='boolean',default=False),
                    Field('url',type='string',notnull=True),
                    Field('label',type='string')
                   )

db.executesql('CREATE INDEX IF NOT EXISTS URL_INFO_UUID_IDX ON url_info (uuid);')
db.executesql('CREATE INDEX IF NOT EXISTS URL_INFO_DATA_MIGRATION_IDX ON url_info (data_migration_id);')

db.url_info._after_insert.append(lambda f, id: db(db.url_info.id == id).update_naive(modified_on=request.now))
db.url_info._after_update.append(lambda s, f: updateModifiedOnIfModifiedOnNotUpdated(s,f)) 

def updateModifiedOnIfModifiedOnNotUpdated(s,f):
    for id in [r.id for r in s.select()]:
        db(db.url_info.id == id).update_naive(modified_on=request.now)
