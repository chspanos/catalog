from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, PlantCategory, PlantItem, User

engine = create_engine('sqlite:///plantcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Clear any existing data
users = session.query(User).all()
for user in users:
    session.delete(user)
    session.commit()
categories = session.query(PlantCategory).all()
for category in categories:
     session.delete(category)
     session.commit()
items = session.query(PlantItem).all()
for item in items:
    session.delete(item)
    session.commit()


# Create dummy user
User1 = User(name="Flora Bunda", email="florasflowers@gmail.com",
             picture="/static/images/blank_user.gif")
session.add(User1)
session.commit()

# Category data
plantGroups = {
    "categories": [
        {
            "name": "Trees"
        },{
            "name": "Shrubs"
        },{
            "name": "Vines"
        },{
            "name": "Perennials"
        },{
            "name": "Annuals"
        },{
            "name": "Vegetables"
        },{
            "name": "Bulbs"
        }
    ]
}

# Load categories
for category in plantGroups['categories']:
    newCategory = PlantCategory(name=category['name'])
    session.add(newCategory)
    session.commit()


# Plant data
plants = {
  "plants": [
    {
      "name": "False Spirea",
      "botanical_name": "Astilbe",
      "description": "Perennial with plume-like flower clusters and attractive cut foliage",
      "picture": "/static/images/astilbe.JPG",
      "category": "Perennials"
    },{
      "name": "Beans 'Blue Lake'",
      "botanical_name": "Snap Bean",
      "description": "Widely planted garden bean producing tender fleshy pods",
      "picture": "/static/images/beans.JPG",
      "category": "Vegetables"
    },{
      "name": "Coreopsis",
      "botanical_name": "Coreopsis grandiflora",
      "description": "Perennial with narrow leaves and bright yellow flower heads",
      "picture": "/static/images/coreopsis.JPG",
      "category": "Perennials"
    },{
      "name": "Cosmos 'Sonata'",
      "botanical_name": "Cosmos bipinnatus",
      "description": "Annual with divided leaves and daisy-like flowers in white and shades of pink and crimson",
      "picture": "/static/images/cosmos.JPG",
      "category": "Annuals"
    },{
      "name": "Daffodil",
      "botanical_name": "Narcissus",
      "description": "Reliable spring bulb with strapped leaves and trumpet-shaped blossoms",
      "picture": "/static/images/daffodil.jpg",
      "category": "Bulbs"
    },{
      "name": "Daylily 'Stella d'Oro'",
      "botanical_name": "Hemerocallis",
      "description": "Perennial with sword-shaped leaves and bright yellow lily-like flowers",
      "picture": "/static/images/daylily.JPG",
      "category": "Perennials"
    },{
      "name": "Fuchsia",
      "botanical_name": "Fuchsia hybrida",
      "description": "Popular shrub with showy dangling clusters of bi-colored pink or purplish flowers",
      "picture": "/static/images/fuchsia.JPG",
      "category": "Shrubs"
    },{
      "name": "Honeysuckle",
      "botanical_name": "Lonicera",
      "description": "Vine or deciduous shrub valued for frangrant tubular flowers",
      "picture": "/static/images/honeysuckle.JPG",
      "category": "Vines"
    },{
      "name": "Hyacinth",
      "botanical_name": "Hyacinthus orientalis",
      "description": "Spring bulb producing spikes of fragrant bell-shaped flowers",
      "picture": "/static/images/hyacinth.jpg",
      "category": "Bulbs"
    },{
      "name": "Hydrangea",
      "botanical_name": "Hydrangea macrophylla",
      "description": "Shrub with big bold leaves and large clusters of white, pink, or blue flowers",
      "picture": "/static/images/hydrangea.JPG",
      "category": "Shrubs"
    },{
      "name": "Bearded Iris",
      "botanical_name": "Iris",
      "description": "Rhizomous plants with sword-shaped leaves and showy flowers with tufts of hairs on the falls",
      "picture": "/static/images/iris.jpg",
      "category": "Bulbs"
    },{
      "name": "English Lavender",
      "botanical_name": "Lavandula augustifolia",
      "description": "Shrub native to the Mediterranean prized for purple flowers used for perfume",
      "picture": "/static/images/lavender.JPG",
      "category": "Shrubs"
    },{
      "name": "Japanese Maple 'Bloodgood'",
      "botanical_name": "Acer Palmatum",
      "description": "Airy and delicate deciduous tree with deep red foliage",
      "picture": "/static/images/maple.JPG",
      "category": "Trees"
    },{
      "name": "French Marigold 'Bonanza'",
      "botanical_name": "Tagetes patula",
      "description": "Summer anuual with ferny leaves and flowers which range in color from yellow through orange to reddish-brown",
      "picture": "/static/images/marigold.JPG",
      "category": "Annuals"
    },{
      "name": "Heavenly Bamboo",
      "botanical_name": "Nandina Domestica",
      "description": "Evergreen shrub reminiscent of bamboo with canelike stems and fine-textured foliage",
      "picture": "/static/images/nandina.JPG",
      "category": "Shrubs"
    },{
      "name": "Zucchini",
      "botanical_name": "Summer Squash",
      "description": "Prolific producer of cylindrical summer squashes",
      "picture": "/static/images/squash.JPG",
      "category": "Vegetables"
    },{
      "name": "Star Jasmine",
      "botanical_name": "Trachelospermum jasminoides",
      "description": "Twining vine with glossy green leaves and scented white flowers",
      "picture": "/static/images/nandina.JPG",
      "category": "Vines"
    },{
      "name": "Tomato 'Brandywine'",
      "botanical_name": "Tomato",
      "description": "Rich-flavored pink hierloom tomato",
      "picture": "/static/images/tomato.JPG",
      "category": "Vegetables"
    },{
      "name": "Tulip 'Darwin Red Apeldoorn'",
      "botanical_name": "Tulipa",
      "description": "Large, egg-shaped, red flowers on stately stems",
      "picture": "/static/images/tulip.JPG",
      "category": "Bulbs"
    }
  ]
}

# Load first 15 plant items
for i in range(15):
    plant = plants['plants'][i]
    # look up category
    plantGroup = session.query(PlantCategory).filter_by(name=plant['category']).one()
    # Create Plant Item object
    newPlant = PlantItem(name=plant['name'],
        botanical_name=plant['botanical_name'],
        description=plant['description'],
        image=plant['picture'],
        category=plantGroup,
        user_id=1)
    session.add(newPlant)
    session.commit()

print "added menu items!"
