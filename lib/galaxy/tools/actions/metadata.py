from __init__ import ToolAction
from galaxy.datatypes.metadata import JobExternalOutputMetadataWrapper

import logging
log = logging.getLogger( __name__ )

class SetMetadataToolAction( ToolAction ):
    """Tool action used for setting external metadata on an existing dataset"""
    
    def execute( self, tool, trans, incoming = {}, set_output_hid = False ):
        for name, value in incoming.iteritems():
            if isinstance( value, trans.app.model.HistoryDatasetAssociation ):
                dataset = value
                dataset_name = name
                break
            else:
                raise Exception( 'The dataset to set metadata on could not be determined.' )
                                
        # Create the job object
        job = trans.app.model.Job()
        job.session_id = trans.get_galaxy_session().id
        job.history_id = trans.history.id
        job.tool_id = tool.id
        start_job_state = job.state #should be job.states.NEW
        try:
            # For backward compatibility, some tools may not have versions yet.
            job.tool_version = tool.version
        except:
            job.tool_version = "1.0.0"
        job.state = job.states.WAITING #we need to set job state to something other than NEW, or else when tracking jobs in db it will be picked up before we have added input / output parameters
        trans.sa_session.add( job )
        trans.sa_session.flush() #ensure job.id is available
        
        #add parameters to job_parameter table
        # Store original dataset state, so we can restore it. A separate table might be better (no chance of 'losing' the original state)? 
        incoming[ '__ORIGINAL_DATASET_STATE__' ] = dataset.state
        external_metadata_wrapper = JobExternalOutputMetadataWrapper( job )
        cmd_line = external_metadata_wrapper.setup_external_metadata( dataset,
                                                                      trans.sa_session,
                                                                      exec_dir = None,
                                                                      tmp_dir = trans.app.config.new_file_path,
                                                                      dataset_files_path = trans.app.model.Dataset.file_path,
                                                                      output_fnames = None,
                                                                      config_root = None,
                                                                      datatypes_config = None,
                                                                      job_metadata = None,
                                                                      kwds = { 'overwrite' : True } )
        incoming[ '__SET_EXTERNAL_METADATA_COMMAND_LINE__' ] = cmd_line
        for name, value in tool.params_to_strings( incoming, trans.app ).iteritems():
            job.add_parameter( name, value )
        #add the dataset to job_to_input_dataset table
        job.add_input_dataset( dataset_name, dataset )
        #Need a special state here to show that metadata is being set and also allow the job to run
        #   i.e. if state was set to 'running' the set metadata job would never run, as it would wait for input (the dataset to set metadata on) to be in a ready state
        dataset.state = dataset.states.SETTING_METADATA
        job.state = start_job_state #job inputs have been configured, restore initial job state
        trans.sa_session.flush()
        
        # Queue the job for execution
        trans.app.job_queue.put( job.id, tool )
        trans.log_event( "Added set external metadata job to the job queue, id: %s" % str(job.id), tool_id=job.tool_id )
        return []
