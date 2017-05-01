# Create 
db.define_table('company_info',
                    Field('name',type='string',notnull=True),
                    Field('ticker',type='string'),
                    Field('exchange',type='string'),
                    Field('country',type='string'),
                    Field('data_fetch_id','reference data_fetch',notnull=True)
                )