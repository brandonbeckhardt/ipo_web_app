import uuid
# Create 
db.define_table('company_description',
                    Field('uuid',length=64,default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now),
                    Field('description',type='string',notnull=True),
                    Field('company_id',length=64,notnull=True),
                    Field('data_source_id',length=64),
                    format='%(description)s'
                   )

db.company_description.company_id.requires=IS_IN_DB(db,'company_info.uuid','%(name)')

