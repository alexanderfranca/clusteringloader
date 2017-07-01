from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship
from Basis import *
from Protein import *

class Ec( Base ):
    """
    EC numbers.
    """

    __tablename__ = 'ecs'
    
    __table_args__ = {'extend_existing': True}

    id = Column( Integer, primary_key = True )
    ec = Column( String )

    protein = relationship('Protein', secondary=protein_ecs, backref='ecs')
