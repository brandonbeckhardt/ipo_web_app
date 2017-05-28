# Create 
db.define_table('data_source',
                    Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now),
                    Field('source',type='string',notnull=True),
                    Field('date_time',type='datetime',notnull=True),
                    Field('type',type='list:integer',notnull=True),
                    format='%(source)s %(uuid)s'
                   )

