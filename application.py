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


# Login handler
@app.route('/login')
def showLogin():
    ''' This page handles logins '''
    # Create and save state token to prevent request forgery
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in range(32))
    login_session['state'] = state
    #return "The current state is %s" % login_session['state']
    return render_template('login.html', STATE=login_session['state'])


# Google connection handler
@app.route('/gconnect', methods=['POST'])
def gconnect():
    ''' This page handles the server-side callback from Google sign in '''
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
    #user_id = getUserID(login_session['email'])
    #if not user_id:
    #    user_id = createUser(login_session)
    #login_session['user_id'] = user_id

    # Print Welcome message to user
    output = ''
    output = '<h1>Welcome, %s!</h1>' % login_session['username']
    flash("You are now logged in as %s" % login_session['username'])
    return output


# Google Disconnect Handler
@app.route('/disconnect')
def disconnect():
    ''' Page to disconnect user from Google account and logout '''
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
        # del login_session['user_id']
        # Send success message
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        # Oops! The token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def showCategories():
    ''' This page shows all the plant categories along with the most
    recently added plant items
    '''
    #return "Shows all plant categories"
    categories = db_session.query(PlantCategory).all()
    plants = db_session.query(PlantItem).order_by(PlantItem.id.desc()).limit(6)
    return render_template('categories.html', categories=categories, plants=plants)

@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    ''' This page shows all the plant items for the given category '''
    # return "Show all plant items for category %s" % category_name
    category = db_session.query(PlantCategory).filter_by(name=category_name).one()
    plants = db_session.query(PlantItem).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, plants=plants)

@app.route('/catalog/<category_name>/<plant_name>/')
def showPlantItem(category_name, plant_name):
    ''' This page shows all the details for the given plant item '''
    #return "Show all details for plant %s" % plant_name
    category = db_session.query(PlantCategory).filter_by(name=category_name).one()
    plant = db_session.query(PlantItem).filter_by(name=plant_name, category_id=category.id).first()
    creator = db_session.query(User).filter_by(id=plant.user_id).one()
    if category and plant and creator:
        return render_template('plant.html', plant=plant, creator=creator)
    else:
        return "Plant %s is not in database" % plant_name

@app.route('/catalog/newplant/')
def newPlant():
    ''' This page is for creating a new plant item '''
    # return "Create a new plant"
    categories = db_session.query(PlantCategory).all()
    return render_template('newplant.html', categories=categories)

@app.route('/catalog/<plant_name>/edit/')
def editPlant(plant_name):
    ''' This page is for editing the given plant item '''
    # return "Edit plant %s" % plant_name
    categories = db_session.query(PlantCategory).all()
    plant = db_session.query(PlantItem).filter_by(name=plant_name).first()
    return render_template('editplant.html', categories=categories, plant=plant)

@app.route('/catalog/<plant_name>/delete/')
def deletePlant(plant_name):
    ''' This page is for deleting the given plant item '''
    # return "Delete plant %s" % plant_name
    plant = db_session.query(PlantItem).filter_by(name=plant_name).first()
    return render_template('deleteplant.html', plant=plant)


if __name__ == '__main__':
    app.secret_key = "klahhoihjbgksjhaiuwth190333485"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
