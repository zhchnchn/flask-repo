# -*- coding: utf-8 -*-
import random
import datetime
from webapp.models import User, Tag, Post, db


# add User
user01 = User(username='user01')
db.session.add(user01)
db.session.commit()

User.query.filter_by(username='user01').update({'password': 'test01'})
db.session.commit()

user02 = User(username='user02')
db.session.add(user02)
db.session.commit()

# add Post ang Tag
user01 = User.query.filter_by(username='user01').first()
user02 = User.query.filter_by(username='user02').first()
tag_one = Tag('Python')
tag_two = Tag('Flask')
tag_three = Tag('SQLAlechemy')
tag_four = Tag('Jinja')
tag_list = [tag_one, tag_two, tag_three, tag_four]
s = "Example text"

for i in xrange(100):
    new_post = Post("Post {}".format(i+1))
    if i % 2:
        new_post.user = user01
    else:
        new_post.user = user02
    new_post.publish_date = datetime.datetime.now()
    new_post.text = s
    new_post.tags = random.sample(tag_list, random.randint(1, 3))
    db.session.add(new_post)

db.session.commit()
