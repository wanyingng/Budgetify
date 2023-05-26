from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "budget.db"))


# Create the app
app = Flask(__name__)
# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
# Create the extension
db = SQLAlchemy()
# Initialize the app with the extension
db.init_app(app)


# Create a database model for expenses using ORM
class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)

# Create a database file with the specified table(s)
# with app.app_context():
#     db.create_all()

@app.route('/')
def index():
    """Show records of expenses"""
    expenses = Expenses.query.all()
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


@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    """Add a mew record with expense information"""
    if request.method == "POST":
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form['category']
        expense = Expenses(date=date, name=expensename, amount=amount, category=category)
        db.session.add(expense)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('add.html')


@app.route('/delete/<int:id>')
def delete(id):
    """Delete an existing expense record"""
    # Retrieve the first entry that matches the specified id from the query
    expense = Expenses.query.filter_by(id=id).first()
    # Delete the expense record in database
    db.session.delete(expense)
    # Commit the changes to database
    db.session.commit()
    return redirect('/')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Update an existing expense record"""
    if request.method == "POST":
        id = request.form['id']
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form['category']
        # Assign the new properties retrieved from form to the properties of the expense object in database
        expense = Expenses.query.filter_by(id=id).first()
        expense.date = date
        expense.name = expensename
        expense.amount = amount
        expense.category = category
        # Commit the changes to database
        db.session.commit()
        return redirect('/')
    else:
        # Retrieve the first entry that matches the specified id from the query
        expense = Expenses.query.filter_by(id=id).first()
        return render_template('edit.html', expense=expense)


if __name__ == '__main__':
    app.run(debug=True)
