"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html", session=session)


@app.route('/registration-form')
def show_registration_form():
    """Registration form"""

    return render_template("registration.html")


@app.route('/process-registration', methods=['POST'])
def register_user():
    """Add user information to database"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    if User.query.filter(User.email==user_email).all():
        flash('You are already registered! Please log in.')
        return redirect('/')
    else:
        user = User(email=user_email, password=user_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect('/')


@app.route('/login-form')
def show_login_form():
    """Add user information to database"""

    return render_template("login-form.html")


@app.route('/logout')
def logout_user():
    """Logs out user"""
    session.clear()

    return render_template('log-out.html')


@app.route('/log-user-in', methods=["POST"])
def log_user_in():
    """Check that user exists in db and log them in"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    q = User.query
    # figure out how to get user_id in session
    if q.filter(User.email==user_email, User.password==user_password).one():
        flash('You are logged in')
        session['email'] = user_email
        session['user_id'] = q.filter(User.email==user_email).first().user_id

        return redirect('/')

    else:
        flash('Email and/or password does not match. Please try again.')
        return redirect('/login-form')


@app.route("/movies")
def show_movie_list():
    """Shows list if movie titles"""

    movies = Movie.query.order_by('title').all()

    return render_template("movies.html", movies=movies)


@app.route("/movie-details")
def show_movie_details():
    """Show movie details"""

    movie_id = request.args.get("movie_id")
    movie = Movie.query.filter(Movie.movie_id==movie_id).one()

    return render_template("movie_details.html", movie=movie)


@app.route("/add-rating", methods=["POST"])
def rate_movie():
    """Add new rating or edit existing rating."""

    new_score = request.form.get("score")
    movie_id = request.form.get("movie_id")

    db_score = db.session.query(Rating, 
                                User).join(User).filter(Rating.movie_id==movie_id, 
                                                        User.user_id==session['user_id']).one()

    if db_score:
        db_score[0][0].score = new_score
    else:
        new_rating = Rating(movie_id=movie_id, user_id=session['user_id'], score=new_score)
        db.session.add(new_rating)
    
    db.session.commit()

    return redirect("/movie-details")


@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
