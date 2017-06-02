import uuid
# Create 
db.define_table('data_migration',
                    Field('uuid', length=64, default=lambda:str(uuid.uuid4())),
                    Field('modified_on', 'datetime', default=request.now),
                    #Datetime the data source was last exported (through csv)
                    Field('export_time', 'datetime'), 
                    #Datetime the data source was last imported (through csv)
                    Field('import_time', 'datetime'), 
                    #Date the migration was created
                    Field('created_time', 'datetime', notnull=True, default=request.now),
                    Field('source',type='string',notnull=True),
                    Field('type',type='list:string',notnull=True),
                    format='%(source)s %(uuid)s'
                   )

db.executesql('CREATE INDEX IF NOT EXISTS data_migration_UUID_IDX ON data_migration (uuid);')

db.data_migration._after_insert.append(lambda f, id: db(db.data_migration.id == id).update_naive(modified_on=request.now))
