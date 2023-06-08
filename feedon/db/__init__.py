import peewee
import playhouse.sqlite_ext as sqlite_ext
import os

db = peewee.SqliteDatabase(os.environ.get('DB_PATH', 'feedon.db'))

class Instance(peewee.Model):
    instance_domain = peewee.CharField(primary_key=True)
    client_id = peewee.CharField()
    client_secret = peewee.CharField()
    full_response = sqlite_ext.JSONField()

    class Meta:
        table_name = 'instances'
        database = db

class User(peewee.Model):
    id = peewee.AutoField()
    handle = peewee.CharField()
    instance_domain = peewee.CharField()
    access_token = peewee.CharField()

    class Meta:
        table_name = 'users'
        database = db

db.create_tables([User, Instance])
