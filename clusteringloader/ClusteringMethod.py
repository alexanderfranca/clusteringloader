from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship
from Basis import *

class ClusteringMethod( Base ):
    """
    ClusteringMethod: used software, author, cutoff etc 
    """

    __tablename__ = 'clustering_methods'

    __table_args__ = {'extend_existing': True}

    id       = Column( Integer, primary_key = True )
    author   = Column( String )
    date     = Column( String )
    software = Column( String )
    cutoff   = Column( Integer )
    name     = Column( String )

