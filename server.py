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
    return render_template("homepage.html")


@app.route('/registration')
def register_user():
    """Registration form"""

    return render_template("registration.html")


@app.route('/form-process', methods=['POST'])
def process_user():
    """Add user information to database"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    if User.query.filter(User.email==user_email).all():
        flash('You are already registered! Please sign in.')
        return redirect('/')
    else:
        user = User(email=user_email, password=user_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful')
        return redirect('/')


@app.route('/login')
def login():
    """Add user information to database"""

    return render_template("login-form.html")

@app.route('/log-user-in', methods=["POST"])
def log_user_in():
    """Check that user exists in db and log them in"""

    user_email = request.form.get("email")
    user_password = request.form.get("password")

    q = User.query

    if q.filter(User.email==user_email, User.password==user_password).all():
        flash('You are logged in')
        return redirect('/')
    else:
        flash('Email and/or password does not match. Please try again.')
        return redirect('/login')



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
