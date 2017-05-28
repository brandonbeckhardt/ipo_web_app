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