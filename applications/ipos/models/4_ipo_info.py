import uuid
# Create 
db.define_table('ipo_info',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now, readable=False, writable=False),
                    Field('company_id',length=64,notnull=True),
                    Field('data_migration_id',length=64),
                    Field('date',type='date'),
                    Field('date_week',type='string'),
                    Field('broker',type='string')
                   )

db.executesql('CREATE INDEX IF NOT EXISTS IPO_INFO_UUID_IDX ON ipo_info (uuid);')
db.executesql('CREATE INDEX IF NOT EXISTS IPO_INFO_data_migration_IDX ON ipo_info (data_migration_id);')

db.ipo_info.company_id.requires=IS_IN_DB(db,'company_info.uuid','%(name)')

db.ipo_info._after_insert.append(lambda f, id: db(db.ipo_info.id == id).update_naive(modified_on=request.now))
db.ipo_info._after_update.append(lambda s, f: updateModifiedOnIfModifiedOnNotUpdated(s,f)) 

def updateModifiedOnIfModifiedOnNotUpdated(s,f):
    for id in [r.id for r in s.select()]:
        db(db.ipo_info.id == id).update_naive(modified_on=request.now)
