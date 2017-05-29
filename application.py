from flask import Flask, render_template, url_for, request, redirect
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
def showLogin():
    ''' This page handles logins '''
    return "Login page goes here"

@app.route('/disconnect')
def disconnect():
    return "Logout page goes here"

@app.route('/')
@app.route('/catalog/')
def showCategories():
    ''' This page shows all the plant categories along with the most
    recently added plant items
    '''
    #return "Shows all plant categories"
    categories = session.query(PlantCategory).all()
    plants = session.query(PlantItem).order_by(PlantItem.id.desc()).limit(6)
    return render_template('categories.html', categories=categories, plants=plants)

@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    ''' This page shows all the plant items for the given category '''
    # return "Show all plant items for category %s" % category_name
    category = session.query(PlantCategory).filter_by(name=category_name).one()
    plants = session.query(PlantItem).filter_by(category_id=category.id).all()
    return render_template('category.html', category=category, plants=plants)

@app.route('/catalog/<category_name>/<plant_name>/')
def showPlantItem(category_name, plant_name):
    ''' This page shows all the details for the given plant item '''
    #return "Show all details for plant %s" % plant_name
    category = session.query(PlantCategory).filter_by(name=category_name).one()
    plant = session.query(PlantItem).filter_by(name=plant_name, category_id=category.id).first()
    creator = session.query(User).filter_by(id=plant.user_id).one()
    if category and plant and creator:
        return render_template('plant.html', plant=plant, creator=creator)
    else:
        return "Plant %s is not in database" % plant_name

@app.route('/catalog/newplant/')
def newPlant():
    ''' This page is for creating a new plant item '''
    # return "Create a new plant"
    categories = session.query(PlantCategory).all()
    return render_template('newplant.html', categories=categories)

@app.route('/catalog/<plant_name>/edit/')
def editPlant(plant_name):
    ''' This page is for editing the given plant item '''
    # return "Edit plant %s" % plant_name
    categories = session.query(PlantCategory).all()
    plant = session.query(PlantItem).filter_by(name=plant_name).first()
    return render_template('editplant.html', categories=categories, plant=plant)

@app.route('/catalog/<plant_name>/delete/')
def deletePlant(plant_name):
    ''' This page is for deleting the given plant item '''
    # return "Delete plant %s" % plant_name
    plant = session.query(PlantItem).filter_by(name=plant_name).first()
    return render_template('deleteplant.html', plant=plant)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
