from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.exc import *
from migrate import *
from migrate.changeset import *
import datetime
now = datetime.datetime.utcnow
import sys, logging
# Need our custom types, but don't import anything else from model
from galaxy.model.custom_types import *

log = logging.getLogger( __name__ )
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler( sys.stdout )
format = "%(name)s %(levelname)s %(asctime)s %(message)s"
formatter = logging.Formatter( format )
handler.setFormatter( formatter )
log.addHandler( handler )

metadata = MetaData( migrate_engine )
db_session = scoped_session( sessionmaker( bind=migrate_engine, autoflush=False, autocommit=True ) )

def display_migration_details():
    print ""
    print "========================================"
    print """This script creates a job_to_output_library_dataset table for allowing library
uploads to run as regular jobs.  To support this, a library_folder_id column is
added to the job table, and library_folder/output_library_datasets relations
are added to the Job object.  An index is also added to the dataset.state
column."""
    print "========================================"

JobToOutputLibraryDatasetAssociation_table = Table( "job_to_output_library_dataset", metadata,
    Column( "id", Integer, primary_key=True ),
    Column( "job_id", Integer, ForeignKey( "job.id" ), index=True ),
    Column( "ldda_id", Integer, ForeignKey( "library_dataset_dataset_association.id" ), index=True ),
    Column( "name", String(255) ) )

def upgrade():
    display_migration_details()
    # Load existing tables
    metadata.reflect()
    # Create the job_to_output_library_dataset table
    try:
        JobToOutputLibraryDatasetAssociation_table.create()
    except Exception, e:
        print "Creating job_to_output_library_dataset table failed: %s" % str( e )
        log.debug( "Creating job_to_output_library_dataset table failed: %s" % str( e ) )
    # Create the library_folder_id column
    try:
        Job_table = Table( "job", metadata, autoload=True )
    except NoSuchTableError:
        Job_table = None
        log.debug( "Failed loading table job" )
    if Job_table:
        try:
            col = Column( "library_folder_id", Integer, index=True )
            col.create( Job_table )
            assert col is Job_table.c.library_folder_id
        except Exception, e:
            log.debug( "Adding column 'library_folder_id' to job table failed: %s" % ( str( e ) ) )
        try:
            LibraryFolder_table = Table( "library_folder", metadata, autoload=True )
        except NoSuchTableError:
            LibraryFolder_table = None
            log.debug( "Failed loading table library_folder" )
        # Add 1 foreign key constraint to the job table
        if Job_table and LibraryFolder_table:
            try:
                cons = ForeignKeyConstraint( [Job_table.c.library_folder_id],
                                             [LibraryFolder_table.c.id],
                                             name='job_library_folder_id_fk' )
                # Create the constraint
                cons.create()
            except Exception, e:
                log.debug( "Adding foreign key constraint 'job_library_folder_id_fk' to table 'library_folder' failed: %s" % ( str( e ) ) )
    # Create the ix_dataset_state index
    try:
        Dataset_table = Table( "dataset", metadata, autoload=True )
    except NoSuchTableError:
        Dataset_table = None
        log.debug( "Failed loading table dataset" )
    i = Index( "ix_dataset_state", Dataset_table.c.state )
    try:
        i.create()
    except Exception, e:
        print str(e)
        log.debug( "Adding index 'ix_dataset_state' to dataset table failed: %s" % str( e ) )

def downgrade():
    metadata.reflect()
    # Drop the library_folder_id column
    try:
        Job_table = Table( "job", metadata, autoload=True )
    except NoSuchTableError:
        Job_table = None
        log.debug( "Failed loading table job" )
    if Job_table:
        try:
            col = Job_table.c.library_folder_id
            col.drop()
        except Exception, e:
            log.debug( "Dropping column 'library_folder_id' from job table failed: %s" % ( str( e ) ) )
    # Drop the job_to_output_library_dataset table
    try:
        JobToOutputLibraryDatasetAssociation_table.drop()
    except Exception, e:
        print str(e)
        log.debug( "Dropping job_to_output_library_dataset table failed: %s" % str( e ) )
    # Drop the ix_dataset_state index
    try:
        Dataset_table = Table( "dataset", metadata, autoload=True )
    except NoSuchTableError:
        Dataset_table = None
        log.debug( "Failed loading table dataset" )
    i = Index( "ix_dataset_state", Dataset_table.c.state )
    try:
        i.drop()
    except Exception, e:
        print str(e)
        log.debug( "Dropping index 'ix_dataset_state' from dataset table failed: %s" % str( e ) )
