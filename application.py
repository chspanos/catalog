from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, PlantCategory, PlantItem, User

# Create Flask application
app = Flask(__name__)

# Connect to plant catalog database
engine = create_engine('sqlite:///plantcatalog.db')
Base.metadata.bind = engine
# Create a session to interface with the database
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def Login():
    ''' This page handles logins '''
    return "Login page goes here"

@app.route('/')
@app.route('/catalog/')
def showCategories():
    ''' This page shows all the plant categories along with the most
    recently added plant item in each category
    '''
    return "Shows all plant categories"

@app.route('/catalog/<string:category_name>/')
def showCategory(category_name):
    ''' This page shows all the plant items for the given category '''
    return "Show all plant items for category %s" % category_name

@app.route('/catalog/<string:category_name>/<string:plant_name>/')
def showPlantItem(category_name, plant_name):
    ''' This page shows all the details for the given plant item '''
    return "Show all details for plant %s" % plant_name

@app.route('/catalog/newplant/')
def newPlant():
    ''' This page is for creating a new plant item '''
    return "Create a new plant"

@app.route('/catalog/<string:plant_name>/edit/')
def editPlant(plant_name):
    ''' This page is for editing the given plant item '''
    return "Edit plant %s" % plant_name

@app.route('/catalog/<string:plant_name>/delete/')
def deletePlant(plant_name):
    ''' This page is for deleting the given plant item '''
    return "Delete plant %s" % plant_name


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
