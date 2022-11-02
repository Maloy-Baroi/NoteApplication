from peewee import *
import datetime


db = SqliteDatabase("peewee_database.db")

class User(Model):
    email = CharField(max_length=255, unique=True)
    password = CharField(max_length=100)

    class Meta:
        database = db


class AuthToken(Model):
    user = ForeignKeyField(User)
    token = CharField(max_length=105)

    class Meta:
        database = db


class Notes(Model):
    author = ForeignKeyField(User)
    title = CharField(max_length=255)
    content = TextField()

    class Meta:
        database = db


if __name__ == "__main__":
    db.connect()
    db.create_tables([User, Notes, AuthToken], safe=True)

