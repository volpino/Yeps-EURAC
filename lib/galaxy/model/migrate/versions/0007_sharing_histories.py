"""
This migration script creates the new history_user_share_association table, and adds
a new boolean type column to the history table.  This provides support for sharing
histories in the same way that workflows are shared.
"""
from sqlalchemy import *
from sqlalchemy.orm import *
from migrate import *
from migrate.changeset import *
import sys, logging

log = logging.getLogger( __name__ )
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler( sys.stdout )
format = "%(name)s %(levelname)s %(asctime)s %(message)s"
formatter = logging.Formatter( format )
handler.setFormatter( formatter )
log.addHandler( handler )

metadata = MetaData( migrate_engine )

def display_migration_details():
    print "========================================"
    print "This migration script creates the new history_user_share_association table, and adds"
    print "a new boolean type column to the history table.  This provides support for sharing"
    print "histories in the same way that workflows are shared."
    print "========================================"

HistoryUserShareAssociation_table = Table( "history_user_share_association", metadata,
    Column( "id", Integer, primary_key=True ),
    Column( "history_id", Integer, ForeignKey( "history.id" ), index=True ),
    Column( "user_id", Integer, ForeignKey( "galaxy_user.id" ), index=True )
    )

def upgrade():
    display_migration_details()
    # Load existing tables
    metadata.reflect()
    # Create the history_user_share_association table
    try:
        HistoryUserShareAssociation_table.create()
    except Exception, e:
        log.debug( "Creating history_user_share_association table failed: %s" % str( e ) )
    # Add 1 column to the history table
    try:
        History_table = Table( "history", metadata, autoload=True )
    except NoSuchTableError:
        History_table = None
        log.debug( "Failed loading table history" )
    if History_table:
        try:
            col = Column( 'importable', Boolean, index=True, default=False )
            col.create( History_table )
            assert col is History_table.c.importable
        except Exception, e:
            log.debug( "Adding column 'importable' to history table failed: %s" % ( str( e ) ) )

def downgrade():
    # Load existing tables
    metadata.reflect()
    # Drop 1 column from the history table
    try:
        History_table = Table( "history", metadata, autoload=True )
    except NoSuchTableError:
        History_table = None
        log.debug( "Failed loading table history" )
    if History_table:
        try:
            col = History_table.c.importable
            col.drop()
        except Exception, e:
            log.debug( "Dropping column 'importable' from history table failed: %s" % ( str( e ) ) )
    # Drop the history_user_share_association table
    try:
        HistoryUserShareAssociation_table.drop()
    except Exception, e:
        log.debug( "Dropping history_user_share_association table failed: %s" % str( e ) )
