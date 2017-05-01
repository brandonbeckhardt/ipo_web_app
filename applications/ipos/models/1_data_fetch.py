# Create 
db.define_table('data_fetch',
                    Field('source',type='string',notnull=True),
                    Field('date',type='date',notnull=True),
                    Field('type',type='integer',notnull=True)
                   )

