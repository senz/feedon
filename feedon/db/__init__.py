import peewee
import requests
import secrets
import os
import playhouse.sqlite_ext as sqlite_ext

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

    def get_client(self):
        s = requests.Session()
        s.headers['Authorization'] = f"Bearer {self.access_token}"

        return s

    def instance_url(self, url):
        return f"https://{self.instance_domain}{url}"
    
    def delete_account(self):
        return self.delete_instance(recursive=True)

    class Meta:
        table_name = 'users'
        database = db

class Timeline(peewee.Model):
    id = peewee.AutoField()
    title = peewee.CharField()
    remote_id = peewee.IntegerField()
    user_id = peewee.ForeignKeyField(User, backref='timelines')
    password = peewee.CharField()

    @classmethod
    def generate_password(cls):
        return secrets.token_urlsafe(16)

    def rss_url(self):
        return f"{os.environ.get('BASE_URL')}/feeds/{self.user_id}/{self.password}/atom.xml"

    class Meta:
        table_name = 'timelines'
        database = db

db.create_tables([User, Instance, Timeline])
