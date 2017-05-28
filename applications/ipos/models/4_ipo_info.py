import uuid
# Create 
db.define_table('ipo_info',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now),
                    Field('company_id',length=64,notnull=True),
                    Field('data_source_id','reference data_source'),
                    Field('date',type='date'),
                    Field('date_week',type='string'),
                    Field('broker',type='string')
                   )

db.ipo_info.company_id.requires=IS_IN_DB(db,'company_info.uuid','%(name)')
