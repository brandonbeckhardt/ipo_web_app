import uuid
# Create 
db.define_table('company_info',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now),
                    Field('name',type='string',notnull=True),
                    Field('ticker',type='string'),
                    Field('exchange',type='string'),
                    Field('country',type='string'),
                    Field('data_source_id',length=64),
                    format='%(name)'
                )

db.company_info._after_insert.append(lambda f, id: db(db.company_info.id == id).update_naive(modified_on=request.now))
db.company_info._after_update.append(lambda s, f: updateModifiedOnIfModifiedOnNotUpdated(s,f)) 

def updateModifiedOnIfModifiedOnNotUpdated(s,f):
    for id in [r.id for r in s.select()]:
        db(db.company_info.id == id).update_naive(modified_on=request.now)