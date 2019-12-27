"""Flask mail room app"""
import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Donation, Donor, User

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/')
def home():
    """home()"""
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    """all()"""
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/create/', methods=['GET', 'POST'])
def create_donation():
    """Create a new donation"""
    # If the visitor is not logged in as a user:
        # Then redirect them to the login page
    # If the method is POST:
        # Then use the name and amount that the user submitted to create a new donation and save it
        # Also, redirect the user to the list of all donations
    # Otherwise, just render the create.jinja2 template
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            donation = Donation(value=int(request.form['amount']), donor=Donor.get(Donor.name == request.form['name']))
            donation.save()
            return redirect(url_for('all'))
        except Donor.DoesNotExist:
            return render_template('create.jinja2', error="Incorrect donor name.")
    else:
        return render_template('create.jinja2')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    # If the user is attempting to submit the login form (method is POST)
    #    Find a user from the database that matches the username provided in the form submission
    #    If you find such a user and their password matches the provided password:
    #        Then log the user in by settings session['username'] to the users name
    #        And redirect the user to the creation of a new donation
    #    Else:
    #        Render the login.jinja2 template and include an error message 
    # Else the user is just trying to view the login form
    #    so render the login.jinja2 template
    if request.method == 'POST':
        try:
            user = User.get(User.name == request.form['name'])
            if pbkdf2_sha256.verify(request.form['password'], user.password):
                session['username'] = user.name
                return redirect(url_for('create_donation'))
        except User.DoesNotExist:
            return render_template('login.jinja2', error="Incorrect username.")
        return render_template('login.jinja2', error="Incorrect password.")
    else:
        return render_template('login.jinja2')

if __name__ == "__main__":
    """main()"""
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

