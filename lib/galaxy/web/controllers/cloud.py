from galaxy.web.base.controller import *

import pkg_resources
pkg_resources.require( "simplejson" )
import simplejson
import urllib2

from galaxy.tools.parameters import *
from galaxy.tools import DefaultToolState
from galaxy.tools.parameters.grouping import Repeat, Conditional
from galaxy.datatypes.data import Data
from galaxy.util.odict import odict
from galaxy.util.bunch import Bunch
from galaxy.util.topsort import topsort, topsort_levels, CycleError
from galaxy.model.mapping import desc
from galaxy.model.orm import *
from datetime import datetime, timedelta

pkg_resources.require( "WebHelpers" )
from webhelpers import *

# Required for Cloud tab
import galaxy.eggs
galaxy.eggs.require("boto")
from boto.ec2.connection import EC2Connection
from boto.ec2.regioninfo import RegionInfo
from galaxy.cloud import CloudManager
import boto.exception
import boto

import logging
log = logging.getLogger( __name__ )

uci_states = Bunch(
    NEW_UCI = "newUCI",
    NEW = "new",
    CREATING = "creating",
    DELETING_UCI = "deletingUCI",
    DELETING = "deleting",
    SUBMITTED_UCI = "submittedUCI",
    SUBMITTED = "submitted",
    SHUTTING_DOWN_UCI = "shutting-downUCI",
    SHUTTING_DOWN = "shutting-down",
    ADD_STORAGE_UCI = "add-storageUCI",
    ADD_STORAGE = "add-storage",
    AVAILABLE = "available",
    RUNNING = "running",
    PENDING = "pending",
    ERROR = "error",
    DELETED = "deleted",
    SNAPSHOT_UCI = "snapshotUCI",
    SNAPSHOT = "snapshot"
)

instance_states = Bunch(
    TERMINATED = "terminated",
    SUBMITTED = "submitted",
    RUNNING = "running",
    ADDING = "adding-storage",
    PENDING = "pending",
    SHUTTING_DOWN = "shutting-down",
    ERROR = "error"
)

store_status = Bunch(
    WAITING = "waiting",
    IN_USE = "in-use",
    ADDING = "adding",
    CREATING = "creating",
    DELETED = 'deleted',
    ERROR = "error"
)

snapshot_status = Bunch(
    SUBMITTED = 'submitted',
    PENDING = 'pending',
    COMPLETED = 'completed',
    DELETE = 'delete',
    DELETED= 'deleted',
    ERROR = "error"
)

class CloudController( BaseController ):
       
    @web.expose
    def index( self, trans ):
        return trans.fill_template( "cloud/index.mako" )
                                   
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def list( self, trans ):
        """
        Render cloud main page (management of cloud resources)
        """
        user = trans.get_user()
        
        cloudCredentials = trans.sa_session.query( model.CloudUserCredentials ) \
            .filter_by( user=user ) \
            .filter( model.CloudUserCredentials.table.c.deleted != True ) \
            .order_by( model.CloudUserCredentials.table.c.name ) \
            .all()
            
        cloudProviders = trans.sa_session.query( model.CloudProvider ) \
            .filter_by( user=user ) \
            .filter( model.CloudProvider.table.c.deleted != True ) \
            .order_by( model.CloudProvider.table.c.name ) \
            .all()
        
        liveInstances = trans.sa_session.query( model.UCI ) \
            .filter_by( user=user ) \
            .filter( or_( model.UCI.table.c.state==uci_states.RUNNING,  
                          model.UCI.table.c.state==uci_states.PENDING, 
                          model.UCI.table.c.state==uci_states.SUBMITTED, 
                          model.UCI.table.c.state==uci_states.SUBMITTED_UCI,
                          model.UCI.table.c.state==uci_states.SHUTTING_DOWN,
                          model.UCI.table.c.state==uci_states.SHUTTING_DOWN_UCI,
                          model.UCI.table.c.state==uci_states.ADD_STORAGE,
                          model.UCI.table.c.state==uci_states.ADD_STORAGE_UCI ) ) \
            .order_by( desc( model.UCI.table.c.update_time ) ) \
            .all()
            
        prevInstances = trans.sa_session.query( model.UCI ) \
            .filter_by( user=user, deleted=False ) \
            .filter( or_( model.UCI.table.c.state==uci_states.AVAILABLE,  
                          model.UCI.table.c.state==uci_states.NEW, 
                          model.UCI.table.c.state==uci_states.NEW_UCI, 
                          model.UCI.table.c.state==uci_states.CREATING, 
                          model.UCI.table.c.state==uci_states.ERROR,  
                          model.UCI.table.c.state==uci_states.DELETED,
                          model.UCI.table.c.state==uci_states.DELETING,
                          model.UCI.table.c.state==uci_states.DELETING_UCI,
                          model.UCI.table.c.state==uci_states.SNAPSHOT,
                          model.UCI.table.c.state==uci_states.SNAPSHOT_UCI ) ) \
            .order_by( desc( model.UCI.table.c.update_time ) ) \
            .all()
        
        # Check after update there are instances in pending state; if so, display message
        pendingInstances = trans.sa_session.query( model.UCI ) \
            .filter_by( user=user ) \
            .filter( or_( model.UCI.table.c.state==uci_states.PENDING, 
                          model.UCI.table.c.state==uci_states.SUBMITTED, 
                          model.UCI.table.c.state==uci_states.SUBMITTED_UCI ) ) \
            .all()
        if pendingInstances:
            trans.set_message( "Galaxy instance started. NOTE: Please wait about 5 minutes for the instance to " 
                               "start up. A button to connect to the instance will appear alongside "
                               "instance description once cloud instance of Galaxy is ready." )       
        
#        log.debug( "provider.is_secure: '%s'" % trans.sa_session.query( model.CloudProvider).filter_by(id=1).first().is_secure )
#        trans.sa_session.query( model.CloudProvider).filter_by(id=1).first().is_secure=False
#        trans.sa_session.flush()
#        log.debug( "provider.is_secure: '%s'" % trans.sa_session.query( model.CloudProvider).filter_by(id=1).first().is_secure )
        
#        log.debug( "image: '%s'" % model.CloudImage.is_secure )
        
        return trans.fill_template( "cloud/configure_cloud.mako",
                                    cloudCredentials = cloudCredentials,
                                    liveInstances = liveInstances,
                                    prevInstances = prevInstances,
                                    cloudProviders = cloudProviders )
    
    # ----- UCI methods -----
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def configure_new_uci( self, trans, instanceName='', credName='', volSize='', zone='' ):
        """
        Configure and add new cloud instance to user's instance pool
        """
        inst_error = vol_error = cred_error = None
        error = {}
        user = trans.get_user()
        
        if instanceName:
            # Check if volume size is entered as an integer
            try:
                volSize = int( volSize )
            except ValueError:
                error['vol_error'] = "Volume size must be integer value between 1 and 1000."
                
            # Create new user configured instance
            try:
                if trans.sa_session.query( model.UCI ) \
                    .filter_by (user=user, deleted=False, name=instanceName ) \
                    .first():
                    error['inst_error'] = "An instance with that name already exist."
                elif instanceName=='' or len( instanceName ) > 255:
                    error['inst_error'] = "Instance name must be between 1 and 255 characters long."
                elif credName=='':
                    error['cred_error'] = "You must select credentials."
                elif volSize == '':
                    error['vol_error'] = "You must specify volume size as an integer value between 1 and 1000."
                elif ( int( volSize ) < 1 ) or ( int( volSize ) > 1000 ):
                    error['vol_error'] = "Volume size must be integer value between 1 and 1000."
                elif zone=='':
                    error['zone_error'] = "You must select a zone where this UCI will be registered."
                else:
                    # Capture user configured instance information
                    uci = model.UCI()
                    uci.name = instanceName
                    creds = trans.sa_session.query( model.CloudUserCredentials ) \
                        .filter( model.CloudUserCredentials.table.c.name==credName ).first()
                    uci.credentials = creds
                    uci.user= user
                    uci.total_size = volSize # This is OK now because new instance is being created and only one storage volume can be created at UCI creation time 
                    uci.state = uci_states.NEW_UCI
                    
                    storage = model.CloudStore()
                    storage.user = user
                    storage.uci = uci
                    storage.size = volSize
                    # If '(any)' zone was selected, just choose the first one that's available
                    if zone == "(any)":
                        zones = None
                        conn = get_connection( trans, creds )
                        if conn != None:
                            try:
                                zones = conn.get_all_zones()
                                if len( zones ) > 0:
                                    zone = str( zones[0] ).split(':')[1]
                            except boto.exception.EC2ResponseError, e:
                                log.error( "Retrieving zones for credentials '%s' failed: %s" % ( storedCred.name, e ) )
                                providersToZones[storedCred.name] = [ "Retrieving zones failed: " + str( e ) ]
                    storage.availability_zone = zone
                    storage.status = store_status.ADDING
                    # Persist
                    session = trans.sa_session
                    session.add( uci )
                    session.add( storage )
                    session.flush()
                    # Log and display the management page
                    trans.log_event( "User configured new cloud instance: '%s'" % instanceName )
                    trans.set_message( "New Galaxy instance '%s' configured. Once instance status shows 'available' you will be able to start the instance." % instanceName )
                    return self.list( trans )
            except AttributeError, ae:
                inst_error = "No registered cloud images. You must contact administrator to add some before proceeding."
                log.debug("AttributeError when registering new UCI '%s': %s " % ( instanceName, str( ae ) ) )
        else:
            storedCreds = trans.sa_session.query( model.CloudUserCredentials ).filter_by( user=user, deleted=False ).all()
            if len( storedCreds ) == 0:
                return trans.show_error_message( "You must register credentials before configuring a Galaxy cloud instance." )
            # Create dict mapping of cloud-providers-to-zones available by those providers
            providersToZones = {}
            for storedCred in storedCreds:
                zones = None
                conn = get_connection( trans, storedCred )
                if conn != None:
                    avail_zones = []
                    try:
                        zones = conn.get_all_zones()
                        if len( zones ) > 0:
                            avail_zones.append( "(any)" )
                            for z in zones:
                                z = str( z ).split(':')[1]
                                avail_zones.append( z )
                            providersToZones[storedCred.name] = avail_zones
                    except boto.exception.EC2ResponseError, e:
                        log.error( "Retrieving zones for credentials '%s' failed: %s" % ( storedCred.name, e ) )
                        providersToZones[storedCred.name] = [ "Retrieving zones failed: " + str( e ) ]
                else:
                    providersToZones[storedCred.name] = ['Connection with cloud provider could not be established.']
            
                # Hard-coded solution
    #            if storedCred.provider.storedCred.provider.region_name == 'us-east-1':
    #                ec2_zones = ['us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-1d']
    #                providersToZones[storedCred.name] = ec2_zones 
    #            elif storedCred.provider.region_name == 'eu-west-1':
    #                ec2_zones = ['eu-west-1a', 'eu-west-1b']
    #                providersToZones[storedCred.name] = ec2_zones 
    #            elif storedCred.provider.type == 'eucalyptus':
    #                providersToZones[storedCred.name] = ['epc']
    #            else:
    #                providersToZones[storedCred.name] = ['Unknown provider zone']
            
            return trans.fill_template( "cloud/configure_uci.mako", 
                                        instanceName = instanceName, 
                                        credName = storedCreds, 
                                        volSize = volSize, 
                                        zone = zone, 
                                        error = error, 
                                        providersToZones = providersToZones )
    
    @web.expose
    @web.require_login( "start Galaxy cloud instance" )
    def start( self, trans, id, type='m1.small' ):
        """
        Start a new cloud resource instance
        """
        user = trans.get_user()
        uci = get_uci( trans, id )
        stores = get_stores( trans, uci ) 
        # Ensure instance is available and then store relevant data
        # into DB to initiate instance startup by cloud manager
        if ( len(stores) is not 0 ) and ( uci.state == uci_states.AVAILABLE ):
            instance = model.CloudInstance()
            instance.user = user
            instance.uci = uci
            instance.state = instance_states.SUBMITTED
            instance.availability_zone = stores[0].availability_zone # Bc. all EBS volumes need to be in the same avail. zone, just check 1st
            instance.type = type
            uci.state = uci_states.SUBMITTED_UCI
            # Persist
            session = trans.sa_session
            session.add( instance )
            session.add( uci )
            session.flush()
            # Log  
            trans.log_event ("User initiated starting of UCI '%s'." % uci.name )
            trans.set_message( "Galaxy instance started. NOTE: Please wait about 5 minutes for the instance to " 
                    "start up. A button to connect to the instance will appear alongside "
                    "instance description once cloud instance of Galaxy is ready." )
            return self.list( trans )
        
        if len(stores) == 0:
            error( "This instance does not have any storage volumes associated it and thus cannot be started." )
        else:
            error( "Cannot start instance that is in state '%s'." % uci.state )
        return self.list( trans )
    
    @web.expose
    @web.require_login( "stop Galaxy cloud instance" )
    def stop( self, trans, id ):
        """
        Stop a cloud UCI instance.
        """
        uci = get_uci( trans, id )
        if ( uci.state != uci_states.DELETING ) and \
           ( uci.state != uci_states.DELETING_UCI ) and \
           ( uci.state != uci_states.ERROR ) and \
           ( uci.state != uci_states.SHUTTING_DOWN_UCI ) and \
           ( uci.state != uci_states.SHUTTING_DOWN ) and \
           ( uci.state != uci_states.ADD_STORAGE_UCI ) and \
           ( uci.state != uci_states.ADD_STORAGE ) and \
           ( uci.state != uci_states.AVAILABLE ):
            uci.state = uci_states.SHUTTING_DOWN_UCI
            session = trans.sa_session
            session.add( uci )
            session.flush()
            trans.log_event( "User stopped cloud instance '%s' (id: %s)" % ( uci.name, uci.id ) )
            trans.set_message( "Stopping of Galaxy instance '%s' initiated." % uci.name )
            
            return self.list( trans )
        
        trans.show_error_message( "Cannot stop instance that is in state '%s'." % uci.state )
        return self.list( trans )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def set_uci_state( self, trans, id, state='available', clear_error=True ):
        """
        Sets state of UCI to given state, optionally resets error field, and resets UCI's launch time field to 'None'.
        """
        uci = get_uci( trans, id )
        uci.state = state
        if clear_error:
            uci.error = None
        uci.launch_time = None
        trans.sa_session.flush()
        trans.set_message( "Instance '%s' state reset." % uci.name )
        return self.list( trans )
   
    @web.expose
    @web.require_login( "view instance details" )
    def view_uci_details( self, trans, id=None ):
        """
        View details about running instance
        """
        uci = get_uci( trans, id )
        instances = get_instances( trans, uci ) # TODO: Handle list (will probably need to be done in mako template)
        
        return trans.fill_template( "cloud/view_instance.mako",
                                    liveInstance = instances )
        
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def rename_uci( self, trans, id, new_name=None ):
        instance = get_uci( trans, id )
        if new_name is not None:
            if len(new_name) > 255:
                error( "Instance name must be less than 255 characters long." )
            user = trans.get_user()
            name_exists = trans.sa_session.query( model.UCI ) \
                .filter_by( user=user, name=new_name ) \
                .first() 
            if name_exists:
                error( "Specified name ('%s') is already used by an existing instance. Please choose an alternative name." % new_name )
            
            # Update name in local DB
            instance.name = new_name
            trans.sa_session.flush()
            trans.set_message( "Instance renamed to '%s'." % new_name )
            return self.list( trans )
        else:
            return trans.show_form( 
                web.FormBuilder( url_for( id=trans.security.encode_id(instance.id) ), "Rename instance", submit_text="Rename" )
                .add_text( "new_name", "Instance name", value=instance.name ) )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def uci_usage_report( self, trans, id ):
        user = trans.get_user()
        id = trans.security.decode_id( id )
        
        prevInstances = trans.sa_session.query( model.CloudInstance ) \
            .filter_by( user=user, state=instance_states.TERMINATED, uci_id=id ) \
            .order_by( desc( model.CloudInstance.table.c.update_time ) ) \
            .all()
        
        return trans.fill_template( "cloud/view_usage.mako", prevInstances = prevInstances ) 
    
    @web.expose
    @web.require_login( "delete user configured Galaxy cloud instance" )
    def delete_uci( self, trans, id ):
        """
        Deletes User Configured Instance (UCI) from the cloud and local database. NOTE that this implies deletion of 
        any and all storage associated with this UCI!
        """
        uci = get_uci( trans, id )
        
        if ( uci.state != uci_states.DELETING_UCI ) and ( uci.state != uci_states.DELETING ) and ( uci.state != uci_states.ERROR ):
            name = uci.name
            uci.state = uci_states.DELETING_UCI
            session = trans.sa_session
            session.add( uci )
            session.flush()
            trans.log_event( "User marked cloud instance '%s' for deletion." % name )
            trans.set_message( "Galaxy instance '%s' marked for deletion." % name )
            return self.list( trans )
        
        if uci.state != uci_states.ERROR:
            trans.set_message( "Cannot delete instance in state ERROR." )
        else:
            trans.set_message( "Instance '%s' is already marked for deletion." % uci.name )
        return self.list( trans )
    
    # ----- Snapshot methods -----
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def create_snapshot( self, trans, id ):
        user = trans.get_user()
        id = trans.security.decode_id( id )
        uci = get_uci( trans, id )
        
        stores = trans.sa_session.query( model.CloudStore ) \
            .filter_by( user=user, deleted=False, uci_id=id ) \
            .all()
        
        if ( len( stores ) > 0 ) and ( uci.state == uci_states.AVAILABLE ):  
            for store in stores:
                snapshot = model.CloudSnapshot()
                snapshot.user = user
                snapshot.uci = uci
                snapshot.store = store
                snapshot.status = snapshot_status.SUBMITTED
                uci.state = uci_states.SNAPSHOT_UCI
                # Persist
                session = trans.sa_session
                session.add( snapshot )
                session.add( uci )
                session.flush()
        elif len( stores ) == 0:
            error( "No storage volumes found that are associated with this instance." )
        else:
            error( "Snapshot can be created only for an instance that is in 'available' state." )
        
        # Log and display the management page
        trans.log_event( "User initiated creation of new snapshot." )
        trans.set_message( "Creation of new snapshot initiated. " )
        return self.list( trans )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def view_snapshots( self, trans, id=None ):
        """
        View details about any snapshots associated with given UCI
        """
        user = trans.get_user()
        id = trans.security.decode_id( id )
        
        snaps = trans.sa_session.query( model.CloudSnapshot ) \
            .filter_by( user=user, uci_id=id, deleted=False ) \
            .order_by( desc( model.CloudSnapshot.table.c.update_time ) ) \
            .all()
        
        return trans.fill_template( "cloud/view_snapshots.mako", 
                                   snaps = snaps )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def delete_snapshot( self, trans, uci_id=None, snap_id=None ):
        """
        Initiates deletion of a snapshot
        """
        user = trans.get_user()
        snap_id = trans.security.decode_id( snap_id )
        # Set snapshot as 'ready for deletion' to be picked up by general updater
        snap = trans.sa_session.query( model.CloudSnapshot ).get( snap_id )
        
        if snap.status == snapshot_status.COMPLETED:
            snap.status = snapshot_status.DELETE
            trans.sa_session.add( snap )
            trans.sa_session.flush()
            trans.set_message( "Snapshot '%s' is marked for deletion. Once the deletion is complete, it will no longer be visible in this list. " 
                "Please note that this process may take up to a minute." % snap.snapshot_id ) 
        else:
            error( "Only snapshots in state 'completed' can be deleted. See the cloud provider directly "
                               "if you believe the snapshot is available and can be deleted." ) 
            
        # Display new list of snapshots
        uci_id = trans.security.decode_id( uci_id )
        snaps = trans.sa_session.query( model.CloudSnapshot ) \
            .filter_by( user=user, uci_id=uci_id, deleted=False ) \
            .order_by( desc( model.CloudSnapshot.table.c.update_time ) ) \
            .all()
        
        return trans.fill_template( "cloud/view_snapshots.mako", 
                                   snaps = snaps )
    
    # ----- Storage methods -----
        
    @web.expose
    @web.require_login( "add instance storage" )
    def add_storage( self, trans, id, vol_size=None ):
        error = None
        uci = get_uci( trans, id )
        stores = get_stores_in_status( trans, uci, store_status.IN_USE ) 
        
        # Start adding of storage making sure given UCI is running and that at least one
        # storage volume is attached to it (this is needed to by cloud controller to know
        # as which device to attach the new storage volume) 
        if uci.state == uci_states.RUNNING and len( stores ) > 0:
            if vol_size is not None: 
                try:
                    vol_size = int( vol_size )
                except ValueError:
                    error  = "Volume size must be integer value between 1 and 1000."
                
                if not error:
                    user = trans.get_user()
                    
                    storage = model.CloudStore()
                    storage.user = user
                    storage.uci = uci
                    storage.size = vol_size
                    storage.status = store_status.ADDING
                    
                    # Set state of instance - NOTE that this code will only work (with code in cloud controller) 
                    # for scenario where a UCI is associated with *1* compute instance!!!
                    instances = get_instances( trans, uci )
                    instances.state = instance_states.ADDING

                    uci.state = uci_states.ADD_STORAGE_UCI
                    # Persist
                    session = trans.sa_session
                    session.add( instances )
                    session.add( storage )
                    session.add( uci )
                    session.flush()
                    # Log and display the management page
                    trans.log_event( "User added storage volume to UCI: '%s'" % uci.name )
                    trans.set_message( "Adding of storage to instance '%s' initiated." % uci.name )
                    return self.list( trans )
        else:
            error( "Storage can only be added to instances that are in state 'RUNNING' with existing " \
                   "storage volume(s) already attached." )
        
        return trans.show_form( 
            web.FormBuilder( url_for( id=trans.security.encode_id(uci.id) ), "Add storage to an instance", submit_text="Add" )
            .add_text( "vol_size", "Storage size (1-1000 GB)", value='', error=error ) )
    
    # ----- Image methods -----
    @web.expose
    @web.require_admin
    def add_new_image( self, trans, provider_type='', image_id='', manifest='', architecture='', state=None ):
        #id_error = arch_error = provider_error = manifest_error = None
        error = {}
        if provider_type or image_id or manifest or architecture:
            if provider_type=='':
                error['provider_error'] = "You must select cloud provider type for this machine image."
            elif image_id=='' or len( image_id ) > 255:
                error['id_error'] = "Image ID must be between 1 and 255 characters long."
            elif trans.sa_session.query( model.CloudImage ) \
                    .filter_by( deleted=False ) \
                    .filter( model.CloudImage.table.c.image_id == image_id ) \
                    .first():
                error['id_error'] = "Image with ID '" + image_id + "' is already registered. \
                    Please choose another ID."
            elif architecture=='':
                error['arch_error'] = "You must select architecture type for this machine image."
            else:
                # Create new image
                image = model.CloudImage()
                image.provider_type = provider_type
                image.image_id = image_id
                image.manifest = manifest
                image.architecture = architecture
                # Persist
                session = trans.sa_session
                session.add( image )
                session.flush()
                # Log and display the management page
                trans.log_event( "New cloud image added: '%s'" % image.image_id )
                trans.set_message( "Cloud image '%s' added." % image.image_id )
                if state:
                    image.state = state
                images = trans.sa_session.query( model.CloudImage ).all()
                return trans.fill_template( '/cloud/list_images.mako', images=images )
        
        return trans.fill_template( "cloud/add_image.mako",
                                    provider_type = provider_type,
                                    image_id = image_id,
                                    manifest = manifest,
                                    architecture = architecture,
                                    error = error )
#        return trans.show_form(
#            web.FormBuilder( web.url_for(), "Add new cloud image", submit_text="Add" )
#                .add_text( "provider_type", "Provider type", value='ec2 or eucalyptus', error=provider_error )
#                .add_text( "image_id", "Machine Image ID (AMI or EMI)", value='', error=id_error )
#                .add_text( "manifest", "Manifest", value='', error=manifest_error )
#                .add_text( "architecture", "Architecture", value='i386 or x86_64', error=arch_error ) )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def list_machine_images( self, trans ):
        images = trans.sa_session.query( model.CloudImage ).filter_by( deleted=False ).all()
        return trans.fill_template( '/cloud/list_images.mako', images=images )
    
    @web.expose
    @web.require_admin
    def delete_image( self, trans, id=None ):
        if not isinstance( id, int ):
            id = trans.security.decode_id( id )

        image = trans.sa_session.query( model.CloudImage ).get( id )
        image.deleted = True
        trans.sa_session.add( image )
        trans.sa_session.flush()
        return self.list_machine_images( trans )
    
    @web.expose
    @web.require_admin
    def edit_image( self, trans, provider_type='', image_id='', manifest='', architecture='', id='', edited=False ):
        error = {}
        if not isinstance( id, int ):
            id = trans.security.decode_id( id )
                
        if not edited:
            image = trans.sa_session.query( model.CloudImage ).get( id )
            return trans.fill_template( "cloud/edit_image.mako", 
                                        image = image,
                                        error = error
                                        )
        else:
            image = trans.sa_session.query( model.CloudImage ).get( id )
            if image_id=='' or len( image_id ) > 255:
                error['id_error'] = "Image ID must be between 1 and 255 characters in length."
            elif trans.sa_session.query( model.CloudImage ) \
                .filter_by( deleted=False ) \
                .filter( and_( model.CloudImage.table.c.id != image.id, model.CloudImage.table.c.image_id==image_id ) ) \
                .first():
                error['id_error'] = "Image with ID '" + image_id + "' already exist. Please choose an alternative name."
            elif architecture=='' or len( architecture ) > 255:
                error['arch_error'] = "Architecture type must be between 1 and 255 characters long."
            if error:
                return trans.fill_template( "cloud/edit_image.mako", 
                                            image = image,
                                            error = error
                                            )
            else:
                image.image_id = image_id
                image.manifest = manifest
                image.architecture = architecture
                # Persist
                session = trans.sa_session
                session.add( image )
                session.flush()
                # Log and display the management page
                trans.set_message( "Machine image '%s' edited." % image.image_id )
                return self.list_machine_images( trans )
            
    # ----- Credentials methods -----
    
    @web.expose
    @web.require_login( "add credentials" )
    def add_credentials( self, trans, credName='', accessKey='', secretKey='', providerName='' ):
        """
        Add user's cloud credentials stored under name `credName`.
        """
        user = trans.get_user()
        error = {}
        
        if credName or providerName or accessKey or secretKey:
            if credName=='' or len( credName ) > 255:
                error['cred_error'] = "Credentials name must be between 1 and 255 characters in length."
            elif trans.sa_session.query( model.CloudUserCredentials ) \
                    .filter_by( user=user, deleted=False ) \
                    .filter( model.CloudUserCredentials.table.c.name == credName ) \
                    .first():
                error['cred_error'] = "Credentials with that name already exist."
            elif providerName=='':
                error['provider_error'] = "You must select cloud provider associated with these credentials."
            elif accessKey=='' or len( accessKey ) > 255:
                error['access_key_error'] = "Access key must be between 1 and 255 characters long."
            elif secretKey=='' or len( secretKey ) > 255:
                error['secret_key_error'] = "Secret key must be between 1 and 255 characters long."
            else:
                # Create new user stored credentials
                credentials = model.CloudUserCredentials()
                credentials.name = credName
                credentials.user = user
                credentials.access_key = accessKey
                credentials.secret_key = secretKey
                provider = get_provider( trans, providerName )
                credentials.provider = provider
                # Persist
                session = trans.sa_session
                session.add( credentials )
                session.flush()
                # Log and display the management page
                trans.log_event( "User added new credentials" )
                trans.set_message( "Credential '%s' created" % credentials.name )
                return self.list( trans )
        
        providers = trans.sa_session.query( model.CloudProvider ).filter_by( user=user ).all()
        return trans.fill_template( "cloud/add_credentials.mako", 
                                    credName = credName, 
                                    providerName = providerName, 
                                    accessKey = accessKey, 
                                    secretKey = secretKey, 
                                    error = error, 
                                    providers = providers
                                    )
        
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def edit_credentials( self, trans, id, credName=None, accessKey=None, secretKey=None, edited=False ):
        error = {}
        if not edited:
            credentials = get_stored_credentials( trans, id )
            return trans.fill_template( "cloud/edit_credentials.mako", 
                                        credential = credentials,
                                        error = error
                                        )
        else:
            user = trans.get_user()
            credentials = get_stored_credentials( trans, id )
            if credName=='' or len( credName ) > 255:
                error['cred_error'] = "Credentials name must be between 1 and 255 characters in length."
            elif trans.sa_session.query( model.CloudUserCredentials ) \
                .filter_by( user=user ) \
                .filter( and_( model.CloudUserCredentials.table.c.id != credentials.id, model.CloudUserCredentials.table.c.name==credName ) ) \
                .first():
                error['cred_error'] = "Credentials with name '" + credName + "' already exist. Please choose an alternative name."
            elif accessKey=='' or len( accessKey ) > 255:
                error['access_key_error'] = "Access key must be between 1 and 255 characters long."
            elif secretKey=='' or len( secretKey ) > 255:
                error['secret_key_error'] = "Secret key must be between 1 and 255 characters long."
            
            if error:
                return trans.fill_template( "cloud/edit_credentials.mako", 
                                        credential = credentials,
                                        error = error
                                        )
            else:
                # Edit user stored credentials
                credentials.name = credName
                credentials.access_key = accessKey
                credentials.secret_key = secretKey
                # Persist
                session = trans.sa_session
                session.add( credentials )
                session.flush()
                # Log and display the management page
                trans.set_message( "Credential '%s' edited." % credentials.name )
                return self.list( trans )   
        
    @web.expose
    @web.require_login( "view credentials" )
    def view_credentials( self, trans, id=None ):
        """
        View details for user credentials 
        """        
        # Load credentials from database
        stored = get_stored_credentials( trans, id )
        
        return trans.fill_template( "cloud/view_credentials.mako", 
                                   credDetails = stored )

    @web.expose
    @web.require_login( "test cloud credentials" )
    def test_cred( self, trans, id=None ):
        """
        Tests credentials provided by user with selected cloud provider 
        """

    @web.expose
    @web.require_login( "delete credentials" )
    def delete_credentials( self, trans, id=None ):
        """
        Delete user's cloud credentials checking that no registered instances are tied to given credentials.
        """
        # Load credentials from database
        user = trans.get_user()
        stored = get_stored_credentials( trans, id )
        # Check if there are any UCIs that depend on these credentials
        UCI = None
        UCI = trans.sa_session.query( model.UCI ) \
            .filter_by( user=user, credentials_id=stored.id, deleted=False ) \
            .first()
        
        if UCI == None:
            # Delete and save
            stored.deleted = True
            trans.sa_session.add( stored )
            trans.sa_session.flush()
            # Display the management page
            trans.set_message( "Credentials '%s' deleted." % stored.name )
            return self.list( trans )
        else:
            error( "Existing instance(s) depend on credentials '%s'. You must delete those instances before being able \
                to delete these credentials." % stored.name )
            return self.list( trans )
    
    # ----- Provider methods -----
    
    @web.expose
    @web.require_login( "add provider" )
    def add_provider( self, trans, name='', type='', region_name='', region_endpoint='', is_secure='', host='', port='', proxy='', proxy_port='',
                      proxy_user='', proxy_pass='', debug='', https_connection_factory='', path='' ):
        user = trans.get_user()
        error = {}
        
        if region_name or region_endpoint or name or is_secure or port or proxy or debug or path:
            try:
                is_secure = int(is_secure)
            except ValueError:
                error['is_secure_error'] = "Field 'is secure' can only take on an integer value '0' or '1'"
        
            if trans.sa_session.query( model.CloudProvider ) \
                .filter_by (user=user, name=name) \
                .filter( model.CloudProvider.table.c.deleted != True ) \
                .first():
                error['name_error'] = "A provider with that name already exist."
            elif name=='' or len( name ) > 255:
                error['name_error'] = "Provider name must be between 1 and 255 characters long."
            elif type=='':
                error['type_error'] = "Provider type must be selected."
            elif not (is_secure == 0 or is_secure == 1):
                error['is_secure_error'] = "Field 'is secure' can only take on an integer value '0' or '1'"
            else:
                provider = model.CloudProvider()
                provider.user = user
                provider.type = type
                provider.name = name
                if region_name:
                    provider.region_name = region_name
                else:
                    provider.region_name = None
                
                if region_endpoint:
                    provider.region_endpoint = region_endpoint
                else:
                    provider.region_endpoint = None
                
                if is_secure==0:
                    provider.is_secure = False
                else:
                    provider.is_secure = True
                
                if host:
                    provider.host = host
                else:
                    provider.host = None
                
                if port:
                    provider.port = port
                else:
                    provider.port = None
                
                if proxy:
                    provider.proxy = proxy
                else:
                    provider.proxy = None
                
                if proxy_port:
                    provider.proxy_port = proxy_port
                else:
                    provider.proxy_port = None
                
                if proxy_user:
                    provider.proxy_user = proxy_user
                else:
                    provider.proxy_user = None
                
                if proxy_pass:
                    provider.proxy_pass = proxy_pass
                else:
                    provider.proxy_pass = None
                
                if debug:
                    provider.debug = debug
                else:
                    provider.debug = None
                
                if https_connection_factory:
                    provider.https_connection_factory = https_connection_factory
                else:
                    provider.https_connection_factory = None
                
                provider.path = path
                # Persist
                session = trans.sa_session
                session.add( provider )
                session.flush()
                # Log and display the management page
                trans.log_event( "User configured new cloud provider: '%s'" % name )
                trans.set_message( "New cloud provider '%s' added." % name )
                return self.list( trans )
        
        return trans.fill_template( "cloud/add_provider.mako", 
                                    name = name,
                                    type = type,
                                    region_name = region_name,
                                    region_endpoint = region_endpoint,
                                    is_secure = is_secure,
                                    host = host, 
                                    port = port, 
                                    proxy = proxy,
                                    proxy_port = proxy_port,
                                    proxy_user = proxy_user,
                                    proxy_pass = proxy_pass, 
                                    debug = debug,
                                    https_connection_factory = https_connection_factory,
                                    path = path,
                                    error = error
                                    )
        
    @web.expose
    @web.require_login( "add Amazon EC2 provider" )
    def add_ec2( self, trans ):
        """ Default provider setup for Amazon's EC2. """
        self.add_provider( trans, name='Amazon EC2', type='ec2', region_name='us-east-1', region_endpoint='us-east-1.ec2.amazonaws.com', is_secure=1, path='/' )
        return self.add( trans )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def view_provider( self, trans, id=None ):
        """
        View details about given cloud provider
        """
        # Load credentials from database
        provider = get_provider_by_id( trans, id )
        
        return trans.fill_template( "cloud/view_provider.mako", 
                                   provider = provider )
    
    @web.expose
    @web.require_login( "use Galaxy cloud" )
    def edit_provider( self, trans, id, name='', type='', region_name='', region_endpoint='', is_secure='', host='', port='', proxy='', proxy_port='',
                      proxy_user='', proxy_pass='', debug='', https_connection_factory='', path='', edited=False ):
        error = {}
        if edited == False:
            provider = get_provider_by_id( trans, id )
            return trans.fill_template( "cloud/edit_provider.mako", 
                                        provider = provider,
                                        error = error
                                        )
        else:
            user = trans.get_user()
            provider = get_provider_by_id( trans, id )
            
            try:
                is_secure = int(is_secure)
            except ValueError:
                error['is_secure_error'] = "Field 'is secure' can only take on an integer value '0' or '1'"
        
            if name=='' or len( name ) > 255:
                error['name_error'] = "Cloud provider name must be between 1 and 255 characters in length."
            elif trans.sa_session.query( model.CloudProvider ) \
                .filter_by( user=user ) \
                .filter( and_( model.CloudProvider.table.c.id != provider.id, model.CloudProvider.table.c.name == name ) ) \
                .first():
                error['name_error'] = "Cloud provider with name '" + name + "' already exist. Please choose an alternative name."
            elif not ( is_secure == 0 or is_secure == 1):
                error['is_secure_error'] = "Field 'is secure' can only take on an integer value '0' or '1'"
            
            if error:
                return trans.fill_template( "cloud/edit_provider.mako", 
                                            provider = provider,
                                            error = error
                                            )
            else:
                provider.name = name
                if region_name and region_name != 'None':
                    provider.region_name = region_name
                else:
                    provider.region_name = None
                
                if region_endpoint and region_endpoint != 'None':
                    provider.region_endpoint = region_endpoint
                else:
                    provider.region_endpoint = None
                
                if is_secure==0:
                    provider.is_secure = False
                else:
                    provider.is_secure = True
                
                if host and host != 'None':
                    provider.host = host
                else:
                    provider.host = None
                
                if port and port != 'None':
                    provider.port = port
                else:
                    provider.port = None
                
                if proxy and proxy != 'None':
                    provider.proxy = proxy
                else:
                    provider.proxy = None
                
                if proxy_port and proxy_port != 'None':
                    provider.proxy_port = proxy_port
                else:
                    provider.proxy_port = None
                
                if proxy_user and proxy_user != 'None':
                    provider.proxy_user = proxy_user
                else:
                    provider.proxy_user = None
                
                if proxy_pass and proxy_pass != 'None':
                    provider.proxy_pass = proxy_pass
                else:
                    provider.proxy_pass = None
                
                if debug and debug != 'None':
                    provider.debug = debug
                else:
                    provider.debug = None
                
                if https_connection_factory and https_connection_factory != 'None':
                    provider.https_connection_factory = https_connection_factory
                else:
                    provider.https_connection_factory = None
                
                if path and path != 'None':
                    provider.path = path
                else:
                    provider.path = None
                # Persist
                session = trans.sa_session
                session.add( provider )
                session.flush()
                # Log and display the management page
                trans.log_event( "User edited cloud provider: '%s'" % name )
                trans.set_message( "Cloud provider '%s' edited." % name )
                return self.list( trans )
    
    @web.expose
    @web.require_login( "delete credentials" )
    def delete_provider( self, trans, id=None ):
        """
        Delete use-registered cloud provider checking that no registered credentials are tied to given provider.
        """
        # Load provider from database
        user = trans.get_user()
        provider = get_provider_by_id( trans, id )
        creds = trans.sa_session.query( model.CloudUserCredentials ) \
            .filter_by( user=user, provider_id=provider.id ) \
            .filter( model.CloudUserCredentials.table.c.deleted != True ) \
            .all()
            
        if len( creds ) == 0:
            # Delete and save
            #sess = trans.sa_session
            provider.deleted = True
            trans.sa_session.add( provider )
            trans.sa_session.flush()
            # Display the management page
            trans.set_message( "Cloud provider '%s' deleted." % provider.name )
            return self.list( trans )
        
        error( "Existing credentails depend on cloud provider '%s'. You must delete those credentials before being able \
            to delete this cloud provider." % provider.name )
        return self.list( trans )
    
    # ----- AJAX methods -----
    
    @web.json
    def json_update( self, trans ):
        user = trans.get_user()
        UCIs = trans.sa_session.query( model.UCI ).filter_by( user=user, deleted=False ).all()
        insd = {} # instance name-state dict
        for uci in UCIs:
            dict = {}
            dict['id'] = uci.id
            dict['state'] = uci.state
            dict['total_size'] = uci.total_size
            if uci.error != None:
                dict['error'] = str( uci.error )
            else:
                dict['error'] = None
            if uci.launch_time != None:
                dict['launch_time'] = str( uci.launch_time )
                dict['time_ago'] = str( date.distance_of_time_in_words( uci.launch_time, date.datetime.utcnow() ) )
            else:
                dict['launch_time'] = None
                dict['time_ago'] = None
            insd[uci.name] = dict
        return insd
    
    @web.json
    def link_update( self, trans, uci_id=0 ):
        ild = {} # instance-link-dict
        dict = {}
        dict['uci_id'] = uci_id
        try:
            user = trans.get_user()
            # TODO: This query can assumes only one instance under given UCI can be running (i.e., started).
            inst = trans.sa_session.query( model.CloudInstance ).filter_by( user=user, uci_id=uci_id, state=uci_states.RUNNING ).first()
            urllib2.urlopen( "http://" + inst.public_dns )
            dict['public_dns'] = inst.public_dns
            dict['inst_id'] = inst.id
            ild['data'] = dict
            return ild
        except urllib2.URLError:
            dict['public_dns'] = False
            ild['data'] = dict
            return ild
        
## ---- Utility methods -------------------------------------------------------

def get_provider( trans, name ):
    user = trans.get_user()
    return trans.sa_session.query( model.CloudProvider ) \
                .filter_by (user=user, name=name) \
                .first()
                
def get_provider_by_id( trans, id, check_ownership=True ):
    # Check if 'id' is in int (i.e., it was called from this program) or
    #    it was passed from the web (in which case decode it)
    if not isinstance( id, int ):
        id = trans.security.decode_id( id )

    stored = trans.sa_session.query( model.CloudProvider ).get( id )
    if not stored:
        error( "Cloud provider not found" )
    # Verify ownership
    user = trans.get_user()
    if not user:
        error( "Must be logged in to use the cloud." )
    if check_ownership and not( stored.user == user ):
        error( "Cloud provider '%s' is not registered by current user." % stored.name )
    # Looks good
    return stored
        
def get_stored_credentials( trans, id, check_ownership=True ):
    """
    Get StoredUserCredentials from the database by id, verifying ownership. 
    """
    # Check if 'id' is in int (i.e., it was called from this program) or
    #    it was passed from the web (in which case decode it)
    if not isinstance( id, int ):
        id = trans.security.decode_id( id )

    stored = trans.sa_session.query( model.CloudUserCredentials ).get( id )
    if not stored:
        error( "Credentials not found" )
    # Verify ownership
    user = trans.get_user()
    if not user:
        error( "Must be logged in to use the cloud." )
    if check_ownership and not( stored.user == user ):
        error( "Credentials are not owned by current user." )
    # Looks good
    return stored

def get_uci( trans, id, check_ownership=True ):
    """
    Get a UCI object from the database by id, verifying ownership. 
    """
    # Check if 'id' is in int (i.e., it was called from this program) or
    #    it was passed from the web (in which case decode it)
    if not isinstance( id, int ):
        id = trans.security.decode_id( id )

    live = trans.sa_session.query( model.UCI ).get( id )
    if not live:
        error( "Galaxy instance not found." )
    # Verify ownership
    user = trans.get_user()
    if not user:
        error( "Must be logged in to use the cloud." )
    if check_ownership and not( live.user == user ):
        error( "Instance is not owned by current user." )
    # Looks good
    return live

def get_stores( trans, uci ):
    """
    Get stores objects that are associated with given uci and are not in 'error' status 
    """
    user = trans.get_user()
    stores = trans.sa_session.query( model.CloudStore ) \
            .filter_by( user=user, uci_id=uci.id, deleted=False ) \
            .filter( model.CloudStore.table.c.status != store_status.ERROR ) \
            .all()
            
    return stores

def get_stores_in_status( trans, uci, status ):
    """
    Get stores objects that are associated with given uci and are not have given status
    """
    user = trans.get_user()
    stores = trans.sa_session.query( model.CloudStore ) \
            .filter_by( user=user, uci_id=uci.id, status=status ) \
            .all()
            
    return stores

def get_instances( trans, uci ):
    """
    Get objects of instances that are pending or running and are connected to the given uci object
    """
    user = trans.get_user()
    instances = trans.sa_session.query( model.CloudInstance ) \
            .filter_by( user=user, uci_id=uci.id ) \
            .filter( or_(model.CloudInstance.table.c.state==instance_states.RUNNING, model.CloudInstance.table.c.state==instance_states.PENDING ) ) \
            .first()
            #.all() #TODO: return all but need to edit calling method(s) to handle list
            
    return instances

def get_instances_in_state( trans, uci, state ):
    """
    Get objects of instances that are in specified state and are connected to the given uci object
    """
    user = trans.get_user()
    instances = trans.sa_session.query( model.CloudInstance ) \
            .filter_by( user=user, uci_id=uci.id, state=state ) \
            .all()
            
    return instances

def get_connection( trans, creds ):
    """
    Establishes cloud connection using user's credentials
    """
    log.debug( 'Establishing cloud connection.' )
#    user = trans.get_user()
#    creds = trans.sa_session.query( model.CloudUserCredentials ) \
#        .filter_by( user=user, name=credName ) \
#        .first()
        #.filter( model.CloudUserCredentials.table.c.deleted != True ) \ MOVE TO LINE ABOVE ONCE DELETE COLUMS ARE IMPLEMENTED
        
    if creds:
        a_key = creds.access_key
        s_key = creds.secret_key
        try:
            euca_region = RegionInfo( None, creds.provider.region_name, creds.provider.region_endpoint )
            conn = EC2Connection( aws_access_key_id=a_key, 
                                  aws_secret_access_key=s_key, 
                                  is_secure=creds.provider.is_secure, 
                                  port=creds.provider.port, 
                                  region=euca_region, 
                                  path=creds.provider.path )
        except boto.exception.EC2ResponseError, e:
            log.error( "Establishing connection with cloud failed: %s" % str(e) )
            return None

        return conn
