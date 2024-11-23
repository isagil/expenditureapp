from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenditures.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

# Expenditure Model
class Expenditure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Limit Model
class Limit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)

@app.route("/")
def index():
    # Fetch all expenditures
    expenditures = Expenditure.query.order_by(Expenditure.date.desc()).all()

    # Total spent so far
    total_spent = sum([exp.amount for exp in expenditures])

    # Fetch the limit if set
    limit_entry = Limit.query.first()
    limit = limit_entry.amount if limit_entry else 0

    # Check if we are over the limit
    over_limit = total_spent > limit if limit else False

    return render_template("index.html", expenditures=expenditures, total_spent=total_spent, limit=limit, over_limit=over_limit)

@app.route("/add", methods=["POST"])
def add_expenditure():
    description = request.form["description"]
    amount = float(request.form["amount"])

    # Add new expenditure to the database
    new_exp = Expenditure(description=description, amount=amount)
    db.session.add(new_exp)
    db.session.commit()
    flash("Expenditure added successfully!", "success")

    return redirect(url_for("index"))

@app.route("/delete/<int:id>")
def delete_expenditure(id):
    exp = Expenditure.query.get_or_404(id)
    db.session.delete(exp)
    db.session.commit()
    flash("Expenditure deleted successfully!", "success")
    return redirect(url_for("index"))

@app.route("/set_limit", methods=["POST"])
def set_limit():
    amount = float(request.form["limit"])

    # Set or update the spending limit
    limit_entry = Limit.query.first()
    if limit_entry:
        limit_entry.amount = amount
    else:
        new_limit = Limit(amount=amount)
        db.session.add(new_limit)
    db.session.commit()
    flash("Spending limit updated successfully!", "success")
    return redirect(url_for("index"))

@app.route("/report")
def report():
    # Fetch all expenditures
    expenditures = Expenditure.query.order_by(Expenditure.date.desc()).all()
    return render_template("report.html", expenditures=expenditures)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database is initialized within the app context
    app.run(debug=True)
