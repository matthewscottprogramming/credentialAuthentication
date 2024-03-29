import datetime

from werkzeug.security import generate_password_hash
from flask_login import UserMixin
# from xyz import * is evil (akin to using namespace std in c++)
from peewee import *

DATABASE = SqliteDatabase('social.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)
    
    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)
    
    def get_posts(self):
      return Post.select().where(Post.user==self)
    
    def get_stream(self):
      return Post.select().where(
        (Post.user==self)
      )
    
    def following(self):
      """Get the users that we are following"""
      return User.select().join(Relationship, on=Relationship.to_user).where(Relationship.from_user==self)
    
    def followers(self):
      """Get the users who are following you"""
      return User.select().join(Relationship, on=Relationship.from_user).where(Relationship.to_user==self)
    
    
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction(): #If the transaction fails it ensures that it retraces the steps... google 'ACID transaction processing'
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")

class Post(Model):
  timestamp = DateTimeField(default=datetime.datetime.now)
  user = ForeignKeyField(
    User,
    related_name = 'posts'
  )
  content=TextField()
  
  class Meta:
    database=DATABASE
    order_by=('-timestamp',)
    
    
class Relationship(Model):
  from_user = ForeignKeyField(User, related_name='relationships')
  to_user = ForeignKeyField(User, related_name='related_to')
  
  class Meta:
    database=DATABASE
    indexes = (
      (('from_user', 'to_user'), True),
    )

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
