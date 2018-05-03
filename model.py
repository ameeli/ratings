"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy

from correlation import pearson

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} email={}>".format(self.user_id, 
                                                   self.email)


# Put your Movie and Rating model classes here.

class Movie(db.Model):
    """Movie of the ratings website"""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String(164), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imdb_url = db.Column(db.String(264), nullable=False)

class Rating(db.Model):
    """Ratings for movies"""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer, nullable=False)

    # Define relationship to user
    user = db.relationship("User", backref=db.backref("ratings",
                                                      order_by=rating_id))

    # Define relationship to movie
    movie = db.relationship("Movie", backref=db.backref("ratings",
                                                       order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed"""

        return "<Rating rating_id={} movie_id={} user_id={} score={}>".format (self.rating_id,
                                                                               self.movie_id,
                                                                               self.user_id,
                                                                               self.score)


def compare_users(movie_id, user_id):
    """Create dictionary of user's ratings and find other others who have rated movie."""

    # Get User instance
    u = User.query.get(user_id)

    # Find other ratings for the movie
    other_ratings = Rating.query.filter_by(movie_id=movie_id).all()
    # Find users connected to those ratings
    other_users = [r.user for r in other_ratings]

    o_prime_user_id = 0
    o_prime_similarity = 0.0

    for o in other_users:
        similarity = calc_similarity(u, o)

        if similarity > o_prime_similarity:
            o_prime_similarity = similarity
            o_prime_user_id = o.user_id


def calc_similarity(user1, user2):
    """Calclate similarity between users"""
    
    # create dictionary of user's ratings using the key/value pair of {movie_id: ratings}
    user1_ratings_dict = {}
    
    # add to dictionary with user info
    for r in user1.ratings:
        user1_ratings_dict[r.movie_id] = r

    # create list to hold pairs
    pairs = []

    for user2_rating in user2.ratings:
        user1_rating = user1_ratings_dict.get(user2_rating.movie_id)

        if user1_rating:
            pairs.append((user1_rating.score, user2_rating.score))

    similarity = pearson(pairs)
    
    return similarity


# def compare_users(user_ratings, other)

#     # Get list of other users who have rated movie
#     other_ratings = Rating.query.filter_by(movie_id=movie_id).all()
#     other_users = [r.user for r in other_ratings]








##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ratings'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
