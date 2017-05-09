# Create 
db.define_table('company_description',
                    Field('description',type='string',notnull=True),
                    Field('company_id','reference company_info',notnull=True),
                    Field('data_source_id','reference data_source',notnull=True)
                   )

