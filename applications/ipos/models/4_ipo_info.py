# Create 
db.define_table('ipo_info',
                    Field('company_id','reference company_info',notnull=True),
                    Field('data_source_id','reference data_source',notnull=True),
                    Field('date',type='date'),
                    Field('date_week',type='string'),
                    Field('intended_ticker',type='string'),
                    Field('intended_exchange',type='string'),
                    Field('broker',type='string')
                   )

