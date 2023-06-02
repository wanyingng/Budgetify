import os

from flask import Flask, render_template, request, redirect, session, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import error, usd, login_required, validate

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "budget.db"))

# Create the app
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
# Create the extension
db = SQLAlchemy()
# Initialize the app with the extension
db.init_app(app)


# Create a database model for users using ORM
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    hash = db.Column(db.String(200), nullable=False)


# Create a database model for expenses using ORM
class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)


# Create a database file with the specified table(s)
with app.app_context():
    db.create_all()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return error("Must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("Must provide password", 403)
        # Query database for username
        rows = Users.query.filter_by(
            username=request.form.get("username")).all()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0].hash, request.form.get("password")):
            return error("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0].id
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was not blank
        if not request.form.get("username"):
            return error("Missing username", 400)
        else:
            # Query database for username
            rows = Users.query.filter_by(
                username=request.form.get("username")).all()
            # Ensure username does not already exists in database
            if len(rows) != 0:
                return error("Username is not available", 400)
        # Ensure passwords were not blank
        if not request.form.get("password") or not request.form.get("confirmation"):
            return error("Missing password", 400)
        # Ensure the passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return error("Passwords don't match", 400)
        # Require users’ passwords to have some number of letters, numbers, and/or symbols
        message, code = validate(request.form.get("confirmation"))
        if code != 200:
            return error(message, code)

        # Insert the new user into users, storing a hash of the user's password; and
        # Remember which user has logged in by storing the returned user id in session
        user = Users(username=request.form.get(
            "username"), hash=generate_password_hash(request.form.get("confirmation")))
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        # Flash message upon successful registration
        flash("Welcome, {}!".format(user.username))
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Redirect user to register page
        return render_template("register.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change password"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure passwords were not blank
        if not request.form.get("oldpassword") or not request.form.get("newpassword") or not request.form.get("confirmation"):
            return error("Missing password", 400)
        # Query database for user old password
        rows = Users.query.filter_by(id=session["user_id"]).all()
        # Ensure old password is correct
        if len(rows) != 1 or not check_password_hash(rows[0].hash, request.form.get("oldpassword")):
            return error("Invalid password", 403)
        # Ensure the new passwords match
        elif request.form.get("newpassword") != request.form.get("confirmation"):
            return error("Passwords don't match", 400)
        # Require users’ passwords to have some number of letters, numbers, and/or symbols
        message, code = validate(request.form.get("confirmation"))
        if code != 200:
            return error(message, code)

        # Update user password in database to the new password's hash
        user = Users.query.filter_by(id=session["user_id"]).first()
        user.hash = generate_password_hash(request.form.get("confirmation"))
        db.session.commit()
        # # Flash message upon successful password change
        flash("Changed!")
        # Redirect user to change password page
        return redirect("/password")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Redirect user to change password page
        return render_template("password.html")


@app.route('/')
@login_required
def index():
    """Show records of expenses"""
    expenses = Expenses.query.filter_by(user_id=session["user_id"]).all()
    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_other = 0
    # Calculate the overall total and total for each category
    for expense in expenses:
        total += expense.amount
        if expense.category == 'Food':
            t_food += expense.amount
        elif expense.category == 'Entertainment':
            t_entertainment += expense.amount
        elif expense.category == 'Business':
            t_business += expense.amount
        elif expense.category == 'Other':
            t_other += expense.amount
    return render_template('index.html', expenses=expenses, total=total, t_food=t_food, t_entertainment=t_entertainment, t_business=t_business, t_other=t_other)


@app.route('/about')
def about():
    """Display information about the app"""
    return render_template('about.html')


@app.route('/addexpense', methods=['GET', 'POST'])
@login_required
def addexpense():
    """Add a mew record with expense information"""
    if request.method == "POST":
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form.get('category')
        # Form fields validation
        if not request.form.get("date"):
            return error("Missing date", 400)
        if not request.form.get("expensename"):
            return error("Missing name", 400)
        if not request.form.get("amount"):
            return error("Missing amount", 400)
        if not isinstance(request.form.get("amount", type=float), float):
            return error("Invalid amount", 400)
        if request.form.get("amount", type=float) < 0:
            return error("Amount must be positive number", 400)
        if not request.form.get("category"):
            return error("Missing category", 400)
        expense = Expenses(date=date, name=expensename, amount=amount,
                           category=category, user_id=session["user_id"])
        db.session.add(expense)
        db.session.commit()
        # Flash message upon successful add
        flash("Added!")
        return redirect('/')
    else:
        return render_template('add.html')


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    """Delete an existing expense record"""
    # Retrieve the first entry that matches the current session user id and the pecified id from the query
    expense = Expenses.query.filter_by(
        user_id=session["user_id"], id=id).first()
    # Delete the expense record in database
    db.session.delete(expense)
    # Commit the changes to database
    db.session.commit()
    # Flash message upon successful delete
    flash("Deleted!")
    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Update an existing expense record"""
    if request.method == "POST":
        id = request.form['id']
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form.get('category')
        # Form fields validation
        if not request.form.get("date"):
            return error("Missing date", 400)
        if not request.form.get("expensename"):
            return error("Missing name", 400)
        if not request.form.get("amount"):
            return error("Missing amount", 400)
        if not isinstance(request.form.get("amount", type=float), float):
            return error("Invalid amount", 400)
        if request.form.get("amount", type=float) < 0:
            return error("Amount must be positive number", 400)
        if not request.form.get("category"):
            return error("Missing category", 400)
        # Assign the new properties retrieved from form to the properties of the expense object in database
        expense = Expenses.query.filter_by(
            user_id=session["user_id"], id=id).first()
        expense.date = date
        expense.name = expensename
        expense.amount = amount
        expense.category = category
        # Commit the changes to database
        db.session.commit()
        # Flash message upon successful update
        flash("Updated!")
        return redirect('/')
    else:
        # Retrieve the first entry that matches the specified id from the query
        expense = Expenses.query.filter_by(
            user_id=session["user_id"], id=id).first()
        return render_template('edit.html', expense=expense)


if __name__ == '__main__':
    app.run(debug=True)
