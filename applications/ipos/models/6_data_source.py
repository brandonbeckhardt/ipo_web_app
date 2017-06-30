import uuid
# Create 
db.define_table('data_sources',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('created_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('data_migration_id',length=64),
                    Field('company_id',length=64,notnull=True),
                    Field('sources',type='string')
                   )

db.executesql('CREATE INDEX IF NOT EXISTS DATA_SOURCES_UUID_IDX ON data_sources (uuid);')
db.executesql('CREATE INDEX IF NOT EXISTS DATA_SOURCES_DATA_MIGRATION_IDX ON data_sources (data_migration_id);')

db.url_info._after_insert.append(lambda f, id: db(db.url_info.id == id).update_naive(modified_on=request.now))
db.url_info._after_update.append(lambda s, f: updateModifiedOnIfModifiedOnNotUpdated(s,f)) 

def updateModifiedOnIfModifiedOnNotUpdated(s,f):
    for id in [r.id for r in s.select()]:
        db(db.data_sources.id == id).update_naive(modified_on=request.now)
