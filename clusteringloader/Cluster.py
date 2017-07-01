from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship
from Basis import *

class Cluster( Base ):
    """
    Cluster: protein, ec and identification. 
    """

    __tablename__ = 'clusters'

    __table_args__ = {'extend_existing': True}

    id             = Column( Integer, primary_key = True )
    protein_id     = Column( String )
    ec_id          = Column( String )
    identification = Column( Integer )

