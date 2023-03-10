from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from secrets import token_hex
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
)


# create models from out ERD
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    # apitoken = db.Column(db.String)
    post = db.relationship("Post", backref='author', lazy=True)
    likes = db.relationship("Likes", lazy=True, cascade="all, delete")
    followed = db.relationship("User",
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        secondary = followers,
        backref=db.backref('followers', lazy='dynamic'),
        lazy = 'dynamic'
    )


    def __init__(self, username, email, password): ## REFER TO 1/25 OR 2/8 LECTURE (TOKEN AUTH)
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        # self.apitoken = token_hex(16) ## ASK SHOHA IF THIS WAS FOR LOGIN/AUTH OR WHAT?

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def follow(self, user):
        self.followed.append(user)
        db.session.commit()

    def unfollow(self, user):
        self.followed.remove(user)
        db.session.commit()
    def to_dict(self):
        return {
            'id': self.id,
            'username' : self.username,
            'email' : self.email,
            # 'apitoken' : self.apitoken
        }

class FloraFauna(db.Model):
    __tablename__ = "florafauna"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    post = db.relationship("Post", backref='florafauna', lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    img_url = db.Column(db.String, nullable=False)
    caption = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    florafauna_id = db.Column(db.Integer, db.ForeignKey('florafauna.id'), nullable=True)## change nullable to false once pets are integrated?
    likes = db.relationship("Likes", lazy=True, cascade="all, delete")

    def __init__(self, title, img_url, caption, user_id):
        self.title = title
        self.img_url = img_url
        self.caption = caption
        self.user_id = user_id
    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
    def saveChanges(self):
        db.session.commit()
    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()
    def getLikeCounter(self):
        return len(self.likes)


    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'img_url': self.img_url,
            'caption': self.caption,
            'date_created': self.date_created,
            'user_id': self.user_id,
            'author': self.author.username,
            'like_counter': len(self.likes)
        }


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id
    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()




