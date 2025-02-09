from flask_sqlalchemy import SQLAlchemy


#use models.py to map db and python variable

db = SQLAlchemy()

#fruits table
class Fruit(db.Model):
    __tablename__ = 'fruits'

    id = db.Column(db.Integer, primary_key=True)
    official_name = db.Column(db.String(50), nullable=False)
    other_name = db.Column(db.String(50), nullable=True)
    scientific_name = db.Column(db.String(80), nullable=True)
    cultivar = db.Column(db.String(255), nullable=True)
    other_links = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.Text, nullable=True)
    special_condition = db.Column(db.Text, nullable=True)
    tried_date = db.Column(db.Date, nullable=True)

    #FK
    place_id = db.Column(db.Integer, db.ForeignKey('places.id',ondelete="SET NULL")) #单引号表示普通字符串，双引号用于需要嵌套单引号的情况
    way_id = db.Column(db.Integer, db.ForeignKey('ways_to_get.id', ondelete="SET NULL"), nullable=True)

    #relations
    place = db.relationship("Place", backref="fruits")
    way = db.relationship("WayToGet", backref="fruits")
    reviews = db.relationship("FruitReview", backref="fruit", cascade="all, delete-orphan") #once delete the fruit, delete all follow info
    users = db.relationship("FruitUser", backref="fruit", cascade="all, delete-orphan")
    videos = db.relationship("FruitVideo", backref="fruit", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "official_name": self.official_name,
            "scientific_name": self.scientific_name,
            "image_url": self.image_url,
            "cultivar": self.cultivar,
            "other_links": self.other_links,
            "special_condition": self.special_condition,
            "tried_date": self.tried_date
        }

#places table
class Place(db.Model):
    __tablename__ = 'places'

    id = db.Column(db.Integer, primary_key=True)
    place_name = db.Column(db.String(80), nullable=False)
    country = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id":self.id,
            "place_name":self.place_name,
            "country":self.country
        }




#ways_to_get table
class WayToGet(db.Model):
    __tablename__ = 'ways_to_get'

    id = db.Column(db.Integer, primary_key=True)
    method = db.Column(db.String(100), unique=True, nullable=False) #to think once get the fuit must have the way to get
    
    def to_dict(self):
        return {
            "id": self.id,
            "method": self.method
        }

#fruits_revirews table
class FruitReview(db.Model):
    __tablename__ = 'fruit_reviews'

    id = db.Column(db.Integer, primary_key=True)
    fruit_id = db.Column(db.Integer, db.ForeignKey('fruits.id', ondelete="CASCADE"), nullable=False)
    taste_score = db.Column(db.Integer, nullable=False)
    experience_score = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=True)



    def to_dict(self):
        return {
            "id": self.id,
            "fruit_id": self.fruit_id,
            "taste_score": self.taste_score,
            "experience_score": self.experience_score,
            "review": self.review
        }

#users table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id" : self.id,
            "name" : self.name
        }

#fruits_users table
class FruitUser(db.Model):
    __tablename__ = 'fruits_users'

    id = db.Column(db.Integer, primary_key=True)
    fruit_id = db.Column(db.Integer, db.ForeignKey('fruits.id', ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

#video table
class FruitVideo(db.Model):
    __tablename__ = 'fruit_videos'

    id = db.Column(db.Integer, primary_key=True)
    fruit_id = db.Column(db.Integer, db.ForeignKey('fruits.id', ondelete="CASCADE"), nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_link = db.Column(db.Text, nullable=True)

