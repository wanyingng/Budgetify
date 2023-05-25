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
    return render_template('index.html', expenses=expenses)


@app.route('/addexpense', methods=['GET', 'POST'])
def addexpense():
    """Add a mew record with expense information"""
    if request.method == "POST":
        date = request.form['date']
        expensename = request.form['expensename']
        amount = request.form['amount']
        category = request.form['category']
        print(date + ' ' + expensename + ' ' + amount + ' ' + category)
        expense = Expenses(date=date, name=expensename, amount=amount, category=category)
        db.session.add(expense)
        db.session.commit()
        return redirect('/')
    else:
        return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)
