""" Python code to define the User, PlantCategory, and PlantItem tables
and setup the plant catalog database.
"""
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import backref

Base = declarative_base()


class User(Base):
    """ User database object

    Attributes:
        id (Integer, primary key): unique id assigned by database
        name (String, required): username
        email (String, required): user's email address
        picture (String, optional): link to user's profile picture
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class PlantCategory(Base):
    """ PlantCategory database object - stores plant categories

    Attributes:
        id (Integer, primary key): unique id assigned by database
        name (String, required): category name
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
       """ Return object data in easily serializeable format """
       return {
           'name' : self.name,
           'id' : self.id
       }


class PlantItem(Base):
    """ PlantItem database object - stores plant items in catalog

    Attributes:
        id (Integer, primary key): unique id assigned by database
        name (String, required): common plant name
        botanical_name (String, optional): botanical plant name
        description (String, optional): plant description
        image (String, optional): plant image URL
        category_id (Integer, reference to PlantCategory): plant category
        user_id (Integer, reference to User): entry owner
    """
    __tablename__ = 'plant_item'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    botanical_name = Column(String(80))
    description = Column(String(250))
    image = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(PlantCategory,
        backref=backref('plant-item', cascade='all, delete'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """ Return object data in easily serializeable format """
       return {
           'name' : self.name,
           'id' : self.id,
           'botanical_name' : self.botanical_name,
           'description' : self.description,
           'image': self.image,
           'category' : self.category.name
       }


engine = create_engine('sqlite:///plantcatalog.db')

Base.metadata.create_all(engine)
