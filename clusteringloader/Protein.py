from sqlalchemy import Table, MetaData, Column, Integer, String, ForeignKey, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship
from Basis import *

from Organism import *

class Protein( Base ):
	"""
    Proteins: sequences and its related data.
	"""

	__tablename__ = 'proteins'

	__table_args__ = {'extend_existing': True}

	id                = Column( Integer, primary_key = True )
	organism_id       = Column( Integer, ForeignKey('organisms.id') )
	identification    = Column( String )
	description       = Column( String )
	full_fasta_header = Column( Integer )
	sequence          = Column( String )

	organism = relationship('Organism', backref='fk_organisms')
