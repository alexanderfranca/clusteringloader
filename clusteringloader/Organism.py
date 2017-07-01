from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship
from Basis import *

class Organism( Base ):
    """
    Organism and its related data: taxonomy, name etc.
    """
    
    __tablename__ = 'organisms'
    
    __table_args__ = {'extend_existing': True}
    
    id          = Column( Integer, primary_key = True )
    name        = Column( String )
    code        = Column( String )
    taxonomy_id = Column( Integer )
    internal_id = Column( String )
