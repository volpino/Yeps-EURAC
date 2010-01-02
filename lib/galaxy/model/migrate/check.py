import sys, os.path, logging

from galaxy import eggs

import pkg_resources
pkg_resources.require( "sqlalchemy-migrate" )

from migrate.versioning import repository, schema
from sqlalchemy import *
from sqlalchemy.exc import NoSuchTableError

log = logging.getLogger( __name__ )

# path relative to galaxy
migrate_repository_directory = os.path.dirname( __file__ ).replace( os.getcwd() + os.path.sep, '', 1 )
migrate_repository = repository.Repository( migrate_repository_directory )
dialect_to_egg = { 
    "sqlite" : "pysqlite>=2",
    "postgres" : "psycopg2",
    "mysql" : "MySQL_python"
}

def create_or_verify_database( url, engine_options={} ):
    """
    Check that the database is use-able, possibly creating it if empty (this is
    the only time we automatically create tables, otherwise we force the
    user to do it using the management script so they can create backups).
    
    1) Empty database --> initialize with latest version and return
    2) Database older than migration support --> fail and require manual update
    3) Database at state where migrate support introduced --> add version control information but make no changes (might still require manual update)
    4) Database versioned but out of date --> fail with informative message, user must run "sh manage_db.sh upgrade"
    
    """

    dialect = ( url.split( ':', 1 ) )[0]
    try:
        egg = dialect_to_egg[dialect]
        try:
            pkg_resources.require( egg )
            log.debug( "%s egg successfully loaded for %s dialect" % ( egg, dialect ) )
        except:
            # If the module is in the path elsewhere (i.e. non-egg), it'll still load.
            log.warning( "%s egg not found, but an attempt will be made to use %s anyway" % ( egg, dialect ) )
    except KeyError:
        # Let this go, it could possibly work with db's we don't support
        log.error( "database_connection contains an unknown SQLAlchemy database dialect: %s" % dialect )

    # Create engine and metadata
    engine = create_engine( url, **engine_options )
    meta = MetaData( bind=engine )
    # Try to load dataset table
    try:
        dataset_table = Table( "dataset", meta, autoload=True )
    except NoSuchTableError:
        # No 'dataset' table means a completely uninitialized database, which
        # is fine, init the database in a versioned state
        log.info( "No database, initializing" )
        # Database might or might not be versioned
        try:
            # Declare the database to be under a repository's version control
            db_schema = schema.ControlledSchema.create( engine, migrate_repository )
        except:
            # The database is already under version control
            db_schema = schema.ControlledSchema( engine, migrate_repository )
        # Apply all scripts to get to current version
        migrate_to_current_version( engine, db_schema )
        return
    try:
        hda_table = Table( "history_dataset_association", meta, autoload=True )
    except NoSuchTableError:
        raise Exception( "Your database is older than hg revision 1464:c7acaa1bb88f and will need to be updated manually" )
    # There is a 'history_dataset_association' table, so we (hopefully) have
    # version 1 of the database, but without the migrate_version table. This
    # happens if the user has a build from right before migration was added.
    # Verify that this is true, if it is any older they'll have to update
    # manually
    if 'copied_from_history_dataset_association_id' not in hda_table.c:
        # The 'copied_from_history_dataset_association_id' column was added in
        # rev 1464:c7acaa1bb88f.  This is the oldest revision we currently do
        # automated versioning for, so stop here
        raise Exception( "Your database is older than hg revision 1464:c7acaa1bb88f and will need to be updated manually" )
    # At revision 1464:c7acaa1bb88f or greater (database version 1), make sure
    # that the db has version information. This is the trickiest case -- we
    # have a database but no version control, and are assuming it is a certain
    # version. If the user has postion version 1 changes this could cause
    # problems
    try:
        version_table = Table( "migrate_version", meta, autoload=True )
    except NoSuchTableError:
        # The database exists but is not yet under migrate version control, so init with version 1
        log.info( "Adding version control to existing database" )
        try:
            metadata_file_table = Table( "metadata_file", meta, autoload=True )
            schema.ControlledSchema.create( engine, migrate_repository, version=2 )
        except NoSuchTableError:
            schema.ControlledSchema.create( engine, migrate_repository, version=1 )
    # Verify that the code and the DB are in sync
    db_schema = schema.ControlledSchema( engine, migrate_repository )
    if migrate_repository.versions.latest != db_schema.version:
        raise Exception( "Your database has version '%d' but this code expects version '%d'.  Please backup your database and then migrate the schema by running 'sh manage_db.sh upgrade'."
                            % ( db_schema.version, migrate_repository.versions.latest ) )
    else:
        log.info( "At database version %d" % db_schema.version )
        
def migrate_to_current_version( engine, schema ):
    # Changes to get to current version
    changeset = schema.changeset( None )
    for ver, change in changeset:
        nextver = ver + changeset.step
        log.info( 'Migrating %s -> %s... ' % ( ver, nextver ) )
        old_stdout = sys.stdout
        class FakeStdout( object ):
            def __init__( self ):
                self.buffer = []
            def write( self, s ):
                self.buffer.append( s )
            def flush( self ):
                pass
        sys.stdout = FakeStdout()
        try:
            schema.runchange( ver, change, changeset.step )
        finally:
            for message in "".join( sys.stdout.buffer ).split( "\n" ):
                log.info( message )
            sys.stdout = old_stdout