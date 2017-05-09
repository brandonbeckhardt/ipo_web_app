# Create 
db.define_table('data_source',
                    Field('source',type='string',notnull=True),
                    Field('date_time',type='datetime',notnull=True),
                    Field('type',type='list:integer',notnull=True)
                   )

