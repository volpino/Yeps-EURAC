from galaxy.util.bunch import Bunch
from galaxy.tools.parameters import *
from galaxy.tools.parameters.grouping import *
from galaxy.util.template import fill_template
from galaxy.util.none_like import NoneDataset
from galaxy.web import url_for
from galaxy.jobs import JOB_OK
import galaxy.tools
from types import *

import logging
log = logging.getLogger( __name__ )

class ToolAction( object ):
    """
    The actions to be taken when a tool is run (after parameters have
    been converted and validated).
    """
    def execute( self, tool, trans, incoming={} ):
        raise TypeError("Abstract method")
    
class DefaultToolAction( object ):
    """Default tool action is to run an external command"""
    
    def collect_input_datasets( self, tool, param_values, trans ):
        """
        Collect any dataset inputs from incoming. Returns a mapping from 
        parameter name to Dataset instance for each tool parameter that is
        of the DataToolParameter type.
        """
        input_datasets = dict()
        def visitor( prefix, input, value, parent = None ):
            def process_dataset( data ):
                if data and not isinstance( data.datatype, input.formats ):
                    # Need to refresh in case this conversion just took place, i.e. input above in tool performed the same conversion
                    trans.sa_session.refresh( data )
                    target_ext, converted_dataset = data.find_conversion_destination( input.formats, converter_safe = input.converter_safe( param_values, trans ) )
                    if target_ext:
                        if converted_dataset:
                            data = converted_dataset
                        else:
                            #run converter here
                            assoc = trans.app.model.ImplicitlyConvertedDatasetAssociation( parent = data, file_type = target_ext, metadata_safe = False )
                            new_data = data.datatype.convert_dataset( trans, data, target_ext, return_output = True, visible = False ).values()[0]
                            new_data.hid = data.hid
                            new_data.name = data.name
                            trans.sa_session.add( new_data )
                            trans.sa_session.flush()
                            assoc.dataset = new_data
                            trans.sa_session.add( assoc )
                            trans.sa_session.flush()
                            data = new_data
                user, roles = trans.get_user_and_roles()
                if data and not trans.app.security_agent.can_access_dataset( roles, data.dataset ):
                    raise "User does not have permission to use a dataset (%s) provided for input." % data.id
                return data
            if isinstance( input, DataToolParameter ):
                if isinstance( value, list ):
                    # If there are multiple inputs with the same name, they
                    # are stored as name1, name2, ...
                    for i, v in enumerate( value ):
                        input_datasets[ prefix + input.name + str( i + 1 ) ] = process_dataset( v )
                        if parent:
                            parent[input.name] = input_datasets[ prefix + input.name + str( i + 1 ) ]
                        else:
                            param_values[input.name][i] = input_datasets[ prefix + input.name + str( i + 1 ) ]
                else:
                    input_datasets[ prefix + input.name ] = process_dataset( value )
                    if parent:
                        parent[input.name] = input_datasets[ prefix + input.name ]
                    else:
                        param_values[input.name] = input_datasets[ prefix + input.name ]
        tool.visit_inputs( param_values, visitor )
        return input_datasets

    def execute(self, tool, trans, incoming={}, set_output_hid=True ):
        def make_dict_copy( from_dict ):
            """
            Makes a copy of input dictionary from_dict such that all values that are dictionaries
            result in creation of a new dictionary ( a sort of deepcopy ).  We may need to handle 
            other complex types ( e.g., lists, etc ), but not sure... 
            """
            copy_from_dict = {}
            for key, value in from_dict.items():
                if type( value ).__name__ == 'dict':
                    copy_from_dict[ key ] = make_dict_copy( value )
                else:
                    copy_from_dict[ key ] = value
            return copy_from_dict
        def wrap_values( inputs, input_values ):
            # Wrap tool inputs as necessary
            for input in inputs.itervalues():
                if isinstance( input, Repeat ):
                    for d in input_values[ input.name ]:
                        wrap_values( input.inputs, d )
                elif isinstance( input, Conditional ):
                    values = input_values[ input.name ]
                    current = values[ "__current_case__" ]
                    wrap_values( input.cases[current].inputs, values )
                elif isinstance( input, DataToolParameter ):
                    input_values[ input.name ] = \
                        galaxy.tools.DatasetFilenameWrapper( input_values[ input.name ],
                                                             datatypes_registry = trans.app.datatypes_registry,
                                                             tool = tool,
                                                             name = input.name )
                elif isinstance( input, SelectToolParameter ):
                    input_values[ input.name ] = galaxy.tools.SelectToolParameterWrapper( input, input_values[ input.name ], tool.app, other_values = incoming )
                else:
                    input_values[ input.name ] = galaxy.tools.InputValueWrapper( input, input_values[ input.name ], incoming )
        out_data = {}
        # Collect any input datasets from the incoming parameters
        inp_data = self.collect_input_datasets( tool, incoming, trans )

        # Deal with input dataset names, 'dbkey' and types
        input_names = []
        input_ext = 'data'
        input_dbkey = incoming.get( "dbkey", "?" )
        for name, data in inp_data.items():
            if data:
                input_names.append( 'data %s' % data.hid )
                input_ext = data.ext
            else:
                data = NoneDataset( datatypes_registry = trans.app.datatypes_registry )
            if data.dbkey not in [None, '?']:
                input_dbkey = data.dbkey

        # Collect chromInfo dataset and add as parameters to incoming
        db_datasets = {}
        db_dataset = trans.db_dataset_for( input_dbkey )
        if db_dataset:
            db_datasets[ "chromInfo" ] = db_dataset
            incoming[ "chromInfo" ] = db_dataset.file_name
        else:
            incoming[ "chromInfo" ] = os.path.join( trans.app.config.tool_data_path, 'shared','ucsc','chrom', "%s.len" % input_dbkey )
        inp_data.update( db_datasets )
        
        # Determine output dataset permission/roles list
        existing_datasets = [ inp for inp in inp_data.values() if inp ]
        if existing_datasets:
            output_permissions = trans.app.security_agent.guess_derived_permissions_for_datasets( existing_datasets )
        else:
            # No valid inputs, we will use history defaults
            output_permissions = trans.app.security_agent.history_get_default_permissions( trans.history )
        # Build name for output datasets based on tool name and input names
        if len( input_names ) == 1:
            on_text = input_names[0]
        elif len( input_names ) == 2:
            on_text = '%s and %s' % tuple(input_names[0:2])
        elif len( input_names ) == 3:
            on_text = '%s, %s, and %s' % tuple(input_names[0:3])
        elif len( input_names ) > 3:
            on_text = '%s, %s, and others' % tuple(input_names[0:2])
        else:
            on_text = ""
        # Add the dbkey to the incoming parameters
        incoming[ "dbkey" ] = input_dbkey
        # Keep track of parent / child relationships, we'll create all the 
        # datasets first, then create the associations
        parent_to_child_pairs = []
        child_dataset_names = set()
        for name, output in tool.outputs.items():
            for filter in output.filters:
                try:
                    if not eval( filter.text, globals(), incoming ):
                        break #do not create this dataset
                except Exception, e:
                    log.debug( 'Dataset output filter failed: %s' % e )
            else: #all filters passed
                if output.parent:
                    parent_to_child_pairs.append( ( output.parent, name ) )
                    child_dataset_names.add( name )
                ## What is the following hack for? Need to document under what 
                ## conditions can the following occur? (james@bx.psu.edu)
                # HACK: the output data has already been created
                #      this happens i.e. as a result of the async controller
                if name in incoming:
                    dataid = incoming[name]
                    data = trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( dataid )
                    assert data != None
                    out_data[name] = data
                else:
                    # the type should match the input
                    ext = output.format
                    if ext == "input":
                        ext = input_ext
                    #process change_format tags
                    if output.change_format:
                        for change_elem in output.change_format:
                            for when_elem in change_elem.findall( 'when' ):
                                check = incoming.get( when_elem.get( 'input' ), None )
                                if check is not None:
                                    if check == when_elem.get( 'value', None ):
                                        ext = when_elem.get( 'format', ext )
                                else:
                                    check = when_elem.get( 'input_dataset', None )
                                    if check is not None:
                                        check = inp_data.get( check, None )
                                        if check is not None:
                                            if str( getattr( check, when_elem.get( 'attribute' ) ) ) == when_elem.get( 'value', None ):
                                                ext = when_elem.get( 'format', ext )
                    data = trans.app.model.HistoryDatasetAssociation( extension=ext, create_dataset=True, sa_session=trans.sa_session )
                    # Commit the dataset immediately so it gets database assigned unique id
                    trans.sa_session.add( data )
                    trans.sa_session.flush()
                    trans.app.security_agent.set_all_dataset_permissions( data.dataset, output_permissions )
                # Create an empty file immediately
                open( data.file_name, "w" ).close()
                # Fix permissions
                util.umask_fix_perms( data.file_name, trans.app.config.umask, 0666 )
                # This may not be neccesary with the new parent/child associations
                data.designation = name
                # Copy metadata from one of the inputs if requested. 
                if output.metadata_source:
                    data.init_meta( copy_from=inp_data[output.metadata_source] )
                else:
                    data.init_meta()
                # Take dbkey from LAST input
                data.dbkey = str(input_dbkey)
                # Set state 
                # FIXME: shouldn't this be NEW until the job runner changes it?
                data.state = data.states.QUEUED
                data.blurb = "queued"
                # Set output label
                if output.label:
                    params = make_dict_copy( incoming )
                    # wrapping the params allows the tool config to contain things like
                    # <outputs>
                    #     <data format="input" name="output" label="Blat on ${<input_param>.name}" />
                    # </outputs>
                    wrap_values( tool.inputs, params )
                    params['tool'] = tool
                    params['on_string'] = on_text
                    data.name = fill_template( output.label, context=params )
                else:
                    data.name = tool.name 
                    if on_text:
                        data.name += ( " on " + on_text )
                # Store output 
                out_data[ name ] = data
                # Store all changes to database
                trans.sa_session.flush()
        # Add all the top-level (non-child) datasets to the history
        for name in out_data.keys():
            if name not in child_dataset_names and name not in incoming: #don't add children; or already existing datasets, i.e. async created
                data = out_data[ name ]
                trans.history.add_dataset( data, set_hid = set_output_hid )
                trans.sa_session.add( data )
                trans.sa_session.flush()
        # Add all the children to their parents
        for parent_name, child_name in parent_to_child_pairs:
            parent_dataset = out_data[ parent_name ]
            child_dataset = out_data[ child_name ]
            parent_dataset.children.append( child_dataset )
        # Store data after custom code runs 
        trans.sa_session.flush()
        # Create the job object
        job = trans.app.model.Job()
        job.session_id = trans.get_galaxy_session().id
        job.history_id = trans.history.id
        job.tool_id = tool.id
        try:
            # For backward compatibility, some tools may not have versions yet.
            job.tool_version = tool.version
        except:
            job.tool_version = "1.0.0"
        # FIXME: Don't need all of incoming here, just the defined parameters
        #        from the tool. We need to deal with tools that pass all post
        #        parameters to the command as a special case.
        for name, value in tool.params_to_strings( incoming, trans.app ).iteritems():
            job.add_parameter( name, value )
        user, roles = trans.get_user_and_roles()
        for name, dataset in inp_data.iteritems():
            if dataset:
                if not trans.app.security_agent.can_access_dataset( roles, dataset.dataset ):
                    raise "User does not have permission to use a dataset (%s) provided for input." % data.id
                job.add_input_dataset( name, dataset )
            else:
                job.add_input_dataset( name, None )
        for name, dataset in out_data.iteritems():
            job.add_output_dataset( name, dataset )
        trans.sa_session.add( job )
        trans.sa_session.flush()
        # Some tools are not really executable, but jobs are still created for them ( for record keeping ).
        # Examples include tools that redirect to other applications ( epigraph ).  These special tools must
        # include something that can be retrieved from the params ( e.g., REDIRECT_URL ) to keep the job
        # from being queued.
        if 'REDIRECT_URL' in incoming:
            # Get the dataset - there should only be 1
            for name in inp_data.keys():
                dataset = inp_data[ name ]
            redirect_url = tool.parse_redirect_url( dataset, incoming )
            # GALAXY_URL should be include in the tool params to enable the external application 
            # to send back to the current Galaxy instance
            GALAXY_URL = incoming.get( 'GALAXY_URL', None )
            assert GALAXY_URL is not None, "GALAXY_URL parameter missing in tool config."
            redirect_url += "&GALAXY_URL=%s" % GALAXY_URL
            # Job should not be queued, so set state to ok
            job.state = JOB_OK
            job.info = "Redirected to: %s" % redirect_url
            trans.sa_session.add( job )
            trans.sa_session.flush()
            trans.response.send_redirect( url_for( controller='tool_runner', action='redirect', redirect_url=redirect_url ) )
        else:
            # Queue the job for execution
            trans.app.job_queue.put( job.id, tool )
            trans.log_event( "Added job to the job queue, id: %s" % str(job.id), tool_id=job.tool_id )
            return out_data
