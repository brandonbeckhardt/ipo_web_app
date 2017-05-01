# Create 
db.define_table('ipo_info',
                    Field('company_id','reference company_info',notnull=True),
                    Field('data_fetch_id','reference data_fetch',notnull=True),
                    Field('date',type='date'),
                    Field('date_week',type='date'),
                    Field('intended_ticker',type='string'),
                    Field('intended_exchange',type='string'),
                    Field('broker',type='string')
                   )

