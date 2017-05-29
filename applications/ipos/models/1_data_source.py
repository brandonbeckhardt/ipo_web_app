import uuid
# Create 
db.define_table('data_source',
                    Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now),
                    Field('source',type='string',notnull=True),
                    Field('date_time',type='datetime',notnull=True),
                    Field('type',type='list:integer',notnull=True),
                    format='%(source)s %(uuid)s'
                   )

db.executesql('CREATE INDEX IF NOT EXISTS DATA_SOURCE_UUID_IDX ON data_source (uuid);')

db.data_source._after_insert.append(lambda f, id: db(db.data_source.id == id).update_naive(modified_on=request.now))
db.data_source._after_update.append(lambda s, f: updateModifiedOnIfModifiedOnNotUpdated(s,f)) 

def updateModifiedOnIfModifiedOnNotUpdated(s,f):
    for id in [r.id for r in s.select()]:
        db(db.data_source.id == id).update_naive(modified_on=request.now)
