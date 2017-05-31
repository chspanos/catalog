# Imports for running flask and rendering pages
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
# Imports for SQLalchemy
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
# Imports for creating anti-forgery state tokens
from flask import session as login_session
import random
import string
# Imports for handling Google callback method
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Database objects
from database_setup import Base, PlantCategory, PlantItem, User


# Create Flask application
app = Flask(__name__)

# Get client id from Google client_secrets json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Plant Catalog App'

# Connect to plant catalog database
engine = create_engine('sqlite:///plantcatalog.db')
Base.metadata.bind = engine
# Create a session to interface with the database
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Helper functions for creating and handling new Users
def createUser(login_session):
    """ createUser creates a new User database entry based on the
    given login session information and returns the user ID.
    """
    newUser = User(name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    """ Given a user_id return the corresponding User database object """
    user = db_session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    """ Look up User by email address and return corresponding User's ID.
    If no match return None.
    """
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Login handler
@app.route('/login')
def showLogin():
    """ This page handles logins """
    # Create and save state token to prevent request forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=login_session['state'])


# Google connection handler
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ This page handles the server-side callback from Google sign in """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state token.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain one-time authorization code
    code = request.data

    try:
        # Try to exchange one-time auth code for a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that returned credentials object contained a valid access token
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Abort if this didn't work
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # We have an access token, so check that it matches the Google user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token user ID doesn't match given user ID"), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the client IDs also match
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token client ID doesn't match the app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # We now have credentials, so check if  user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        # user is already logged in, so we don't need to reprocess user
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # New user, so store credentials in session data for later use
    # NOTE: I received an error message when I tried to store the
    # entire credentials object, so I opted to store only access token
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Use Google API to retrieve more information about the user
    userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # Record user information
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # If user is not alreaady in our database, create a new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Print Welcome message to user
    output = ''
    output = '<h1>Welcome, %s!</h1>' % login_session['username']
    flash("You are now logged in as %s" % login_session['username'])
    return output


# Google Disconnect and Logout Handler
@app.route('/disconnect')
def disconnect():
    """ Page to disconnect user from Google account and logout """
    # Grab credentials from login session
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute an http request to revoke the current token
    # NOTE: Recall that we only saved the access_token in credentials
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # If successful, reset the login session
    if result['status'] == '200':
        # Reset the user's login session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['picture']
        del login_session['email']
        del login_session['user_id']
        # Send success message
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        # Oops! The token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Main catalog page handler
@app.route('/')
@app.route('/catalog/')
def showCategories():
    """ This page shows all the plant categories along with the most
    recently added plant items
    """
    categories = db_session.query(PlantCategory).all()
    plants = db_session.query(PlantItem).order_by(PlantItem.id.desc()).limit(6)
    return render_template('categories.html', categories=categories, plants=plants)


# Show Category page handler
@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    """ This page shows all the plant items for the given category """
    category = db_session.query(PlantCategory).filter_by(name=category_name).one()
    plants = db_session.query(PlantItem).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, plants=plants)


# Show a single plant item page handler
@app.route('/catalog/<category_name>/<plant_name>/')
def showPlantItem(category_name, plant_name):
    """ This page shows all the details for the given plant item """
    try:
        category = db_session.query(PlantCategory).filter_by(name=category_name).one()
        plant = db_session.query(PlantItem).filter_by(name=plant_name, category_id=category.id).first()
        creator = db_session.query(User).filter_by(id=plant.user_id).one()
        return render_template('plant.html', plant=plant, creator=creator)
    except:
        flash("Category: %s, Plant: %s is not in catalog" % (category_name, plant_name))
        return redirect(url_for('showCategories'))


# Page handler for creating a new plant item
@app.route('/catalog/newplant/', methods=['GET', 'POST'])
def newPlant():
    """ This page is for creating a new plant item """
    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')
    # Process request
    if request.method == 'POST':
        # Get data from input form
        name = request.form['name']
        botanical_name = request.form['botanical_name']
        image = request.form['image']
        description = request.form['description']
        category_name = request.form['category']
        category = db_session.query(PlantCategory).filter_by(name=category_name).one()
        user_id = login_session['user_id']
        # create new Plant database entry
        newPlantItem = PlantItem(name=name, botanical_name=botanical_name,
            image=image, description=description, category_id=category.id,
            user_id = user_id)
        db_session.add(newPlantItem)
        db_session.commit()
        # redirect to Plant page
        flash("New Plant %s successfully created" % newPlantItem.name)
        return redirect(url_for('showPlantItem', category_name=category_name,
            plant_name=newPlantItem.name))
    else:
        # Display new plant page
        categories = db_session.query(PlantCategory).all()
        return render_template('newplant.html', categories=categories)


# Edit a plant item page handler
@app.route('/catalog/<plant_name>/edit/', methods=['GET', 'POST'])
def editPlant(plant_name):
    """ This page is for editing the given plant item """
    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')
    # Retrieve plant information
    categories = db_session.query(PlantCategory).all()
    editedPlant = db_session.query(PlantItem).filter_by(name=plant_name).first()
    # check for ownership
    if login_session['user_id'] != editedPlant.user_id:
        flash("Edit permission denied: User is not owner of %s" % plant_name)
        return redirect(url_for('showPlantItem',
            category_name=plant.category.name,
            plant_name=plant_name))
    # Process request
    if request.method == 'POST':
        # Get data from input form
        if request.form['name']:
            editedPlant.name = request.form['name']
        if request.form['botanical_name']:
            editedPlant.botanical_name = request.form['botanical_name']
        if request.form['image']:
            editedPlant.image = request.form['image']
        if request.form['description']:
            editedPlant.description = request.form['description']
        if request.form['category']:
            category_name = request.form['category']
            category = db_session.query(PlantCategory).filter_by(name=category_name).one()
            editedPlant.category_id = category.id
        # update Plant database entry
        db_session.add(editedPlant)
        db_session.commit()
        # redirect to Plant page
        flash("Plant %s successfully edited" % editedPlant.name)
        return redirect(url_for('showPlantItem', category_name=category_name,
            plant_name=editedPlant.name))
    else:
        return render_template('editplant.html', categories=categories,
            plant=editedPlant)


# Delete a plant item page handler
@app.route('/catalog/<plant_name>/delete/', methods=['GET', 'POST'])
def deletePlant(plant_name):
    """ This page is for deleting the given plant item """
    # Check for logged in user
    if 'username' not in login_session:
        return redirect('/login')
    # Retrieve plant information
    delPlant = db_session.query(PlantItem).filter_by(name=plant_name).first()
    # check for ownership
    if login_session['user_id'] != delPlant.user_id:
        flash("Delete permission denied: User is not owner of %s" % plant_name)
        return redirect(url_for('showPlantItem',
            category_name=plant.category.name,
            plant_name=plant_name))
    # Process request
    if request.method == 'POST':
        db_session.delete(delPlant)
        db_session.commit()
        flash("Plant %s successfully deleted" % plant_name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteplant.html', plant=delPlant)


if __name__ == '__main__':
    app.secret_key = "klahhoihjbgksjhaiuwth190333485"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
