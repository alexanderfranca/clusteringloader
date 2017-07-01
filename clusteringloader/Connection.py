from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base


class Connection:
    """
    Stablish a new connection with a database and return an Session object.

    """

    def __init__( self ):

        self.db = None


    def connect( self, user=None, password=None, host=None, database=None ):
        """
        Actual connect to a database and return an Session object.

        Args:
            user(str): User name.
            password(str): User password.
            host(str): IP number or name for the host where's the database.
            database(str): Name of the databse.

        """

        self.db = create_engine( 'postgresql://' + user + ':' + password + '@' + host + ':5432/' + database )
        self.db.echo = False
        #db.echo = True 

        Session = sessionmaker(bind = self.db) 
        session = Session()

        return session



