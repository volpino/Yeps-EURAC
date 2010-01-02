"""
Classes encapsulating galaxy tools and tool configuration.
"""
import pkg_resources; 

pkg_resources.require( "simplejson" )

import logging, os, string, sys, tempfile, glob, shutil, types
import simplejson
import binascii
from UserDict import DictMixin
from galaxy.util.odict import odict
from galaxy.util.bunch import Bunch
from galaxy.util.template import fill_template
from galaxy import util, jobs, model
from elementtree import ElementTree
from parameters import *
from parameters.grouping import *
from parameters.validation import LateValidationError
from parameters.input_translation import ToolInputTranslator
from galaxy.util.expressions import ExpressionContext
from galaxy.tools.test import ToolTestBuilder
from galaxy.tools.actions import DefaultToolAction
from galaxy.model import directory_hash_id
from galaxy.util.none_like import NoneDataset
from galaxy.datatypes import sniff
from cgi import FieldStorage
from galaxy.util.hash_util import *

log = logging.getLogger( __name__ )

class ToolNotFoundException( Exception ):
    pass

class ToolBox( object ):
    """
    Container for a collection of tools
    """

    def __init__( self, config_filename, tool_root_dir, app ):
        """
        Create a toolbox from the config file names by `config_filename`,
        using `tool_root_directory` as the base directory for finding 
        individual tool config files.
        """
        self.tools_by_id = {}
        self.workflows_by_id = {}
        self.tool_panel = odict()
        self.tool_root_dir = tool_root_dir
        self.app = app
        try:
            self.init_tools( config_filename )
        except:
            log.exception( "ToolBox error reading %s", config_filename )

    def init_tools( self, config_filename ):
        """
        Read the configuration file and load each tool.
        The following tags are currently supported:
        <toolbox>
            <tool file="data_source/upload.xml"/>            # tools outside sections
            <label text="Basic Tools" id="basic_tools" />    # labels outside sections
            <workflow id="529fd61ab1c6cc36" />               # workflows outside sections
            <section name="Get Data" id="getext">            # sections
                <tool file="data_source/biomart.xml" />      # tools inside sections
                <label text="In Section" id="in_section" />  # labels inside sections
                <workflow id="adb5f5c93f827949" />           # workflows inside sections
            </section>
        </toolbox>
        """
        def load_tool( elem, panel_dict ):
            try:
                path = elem.get( "file" )
                tool = self.load_tool( os.path.join( self.tool_root_dir, path ) )
                self.tools_by_id[ tool.id ] = tool
                key = 'tool_' + tool.id
                panel_dict[ key ] = tool
                log.debug( "Loaded tool: %s %s" % ( tool.id, tool.version ) )
            except:
                log.exception( "error reading tool from path: %s" % path )
        def load_workflow( elem, panel_dict ):
            try:
                # TODO: should id be encoded?
                workflow_id = elem.get( 'id' )
                workflow = self.load_workflow( workflow_id )
                self.workflows_by_id[ workflow_id ] = workflow
                key = 'workflow_' + workflow_id
                panel_dict[ key ] = workflow
                log.debug( "Loaded workflow: %s %s" % ( workflow_id, workflow.name ) )
            except:
                log.exception( "error loading workflow: %s" % workflow_id )
        def load_label( elem, panel_dict ):
            label = ToolSectionLabel( elem )
            key = 'label_' + label.id
            panel_dict[ key ] = label
        def load_section( elem, panel_dict ):
            section = ToolSection( elem )
            log.debug( "Loading section: %s" % section.name )
            for section_elem in elem:
                if section_elem.tag == 'tool':
                    load_tool( section_elem, section.elems )
                elif section_elem.tag == 'workflow':
                    load_workflow( section_elem, section.elems )
                elif section_elem.tag == 'label':
                    load_label( section_elem, section.elems )
            key = 'section_' + section.id
            panel_dict[ key ] = section
                
        log.info("parsing the tool configuration")
        tree = util.parse_xml( config_filename )
        root = tree.getroot()
        for elem in root:
            if elem.tag == 'tool':
                load_tool( elem, self.tool_panel )
            elif elem.tag == 'workflow':
                load_workflow( elem, self.tool_panel )
            elif elem.tag == 'section' :
                load_section( elem, self.tool_panel )
            elif elem.tag == 'label':
                load_label( elem, self.tool_panel )
        
    def load_tool( self, config_file ):
        """
        Load a single tool from the file named by `config_file` and return 
        an instance of `Tool`.
        """
        # Parse XML configuration file and get the root element
        tree = util.parse_xml( config_file )
        root = tree.getroot()
        # Allow specifying a different tool subclass to instantiate
        if root.find( "type" ) is not None:
            type_elem = root.find( "type" )
            module = type_elem.get( 'module', 'galaxy.tools' )
            cls = type_elem.get( 'class' )
            mod = __import__( module, globals(), locals(), [cls])
            ToolClass = getattr( mod, cls )
        elif root.get( 'tool_type', None ) is not None:
            ToolClass = tool_types.get( root.get( 'tool_type' ) )
        else:
            ToolClass = Tool
        return ToolClass( config_file, root, self.app )
        
    def reload( self, tool_id ):
        """
        Attempt to reload the tool identified by 'tool_id', if successful
        replace the old tool.
        """
        if tool_id not in self.tools_by_id:
            raise ToolNotFoundException( "No tool with id %s" % tool_id )
        old_tool = self.tools_by_id[ tool_id ]
        new_tool = self.load_tool( old_tool.config_file )
        # Replace old_tool with new_tool in self.tool_panel
        tool_key = 'tool_' + tool_id
        for key, val in self.tool_panel.items():
            if key == tool_key:
                self.tool_panel[ key ] = new_tool
                break
            elif key.startswith( 'section' ):
                section = val
                for section_key, section_val in section.elems.items():
                    if section_key == tool_key:
                        self.tool_panel[ key ].elems[ section_key ] = new_tool
                        break
        self.tools_by_id[ tool_id ] = new_tool
        log.debug( "Reloaded tool %s %s" %( old_tool.id, old_tool.version ) )

    def load_workflow( self, workflow_id ):
        """
        Return an instance of 'Workflow' identified by `id`, 
        which is encoded in the tool panel.
        """
        id = self.app.security.decode_id( workflow_id )
        stored = self.app.model.context.query( self.app.model.StoredWorkflow ).get( id )
        return stored.latest_workflow

class ToolSection( object ):
    """
    A group of tools with similar type/purpose that will be displayed as a
    group in the user interface.
    """
    def __init__( self, elem ):
        self.name = elem.get( "name" )
        self.id = elem.get( "id" )
        self.version = elem.get( "version" )
        self.elems = odict()

class ToolSectionLabel( object ):
    """
    A label for a set of tools that can be displayed above groups of tools
    and sections in the user interface
    """
    def __init__( self, elem ):
        self.text = elem.get( "text" )
        self.id = elem.get( "id" )
        self.version = elem.get( "version" )

class DefaultToolState( object ):
    """
    Keeps track of the state of a users interaction with a tool between 
    requests. The default tool state keeps track of the current page (for 
    multipage "wizard" tools) and the values of all parameters.
    """
    def __init__( self ):
        self.page = 0
        self.inputs = None
    def encode( self, tool, app ):
        """
        Convert the data to a string
        """
        # Convert parameters to a dictionary of strings, and save curent
        # page in that dict
        value = params_to_strings( tool.inputs, self.inputs, app )
        value["__page__"] = self.page
        value = simplejson.dumps( value )
        # Make it secure
        a = hmac_new( app.config.tool_secret, value )
        b = binascii.hexlify( value )
        return "%s:%s" % ( a, b )      
    def decode( self, value, tool, app ):
        """
        Restore the state from a string
        """
        # Extract and verify hash
        a, b = value.split( ":" )
        value = binascii.unhexlify( b )
        test = hmac_new( app.config.tool_secret, value )
        assert a == test
        # Restore from string
        values = json_fix( simplejson.loads( value ) )
        self.page = values.pop( "__page__" )
        self.inputs = params_from_strings( tool.inputs, values, app, ignore_errors=True )

class ToolOutput( object ):
    """
    Represents an output datasets produced by a tool. For backward
    compatibility this behaves as if it were the tuple:
      (format, metadata_source, parent)  
    """
    def __init__( self, name, format=None, metadata_source=None, 
                  parent=None, label=None, filters = None ):
        self.name = name
        self.format = format
        self.metadata_source = metadata_source
        self.parent = parent
        self.label = label
        self.filters = filters or []

    # Tuple emulation

    def __len__( self ): 
        return 3
    def __getitem__( self, index ):
        if index == 0: 
            return self.format
        elif index == 1:
            return self.metadata_source
        elif index == 2:
            return self.parent
        else:
            raise IndexError( index )
    def __iter__( self ):
        return iter( ( self.format, self.metadata_source, self.parent ) )

class Tool:
    """
    Represents a computational tool that can be executed through Galaxy. 
    """
    tool_type = 'default'
    def __init__( self, config_file, root, app ):
        """
        Load a tool from the config named by `config_file`
        """
        # Determine the full path of the directory where the tool config is
        self.config_file = config_file
        self.tool_dir = os.path.dirname( config_file )
        self.app = app
        # Parse XML element containing configuration
        self.parse( root )
    @property
    def sa_session( self ):
        """Returns a SQLAlchemy session"""
        return self.app.model.context
    def parse( self, root ):
        """
        Read tool configuration from the element `root` and fill in `self`.
        """
        # Get the (user visible) name of the tool
        self.name = root.get( "name" )
        if not self.name: 
            raise Exception, "Missing tool 'name'"
        # Get the UNIQUE id for the tool 
        # TODO: can this be generated automatically?
        self.id = root.get( "id" )
        if not self.id: 
            raise Exception, "Missing tool 'id'" 
        self.version = root.get( "version" )
        if not self.version: 
            # For backward compatibility, some tools may not have versions yet.
            self.version = "1.0.0"
        # Support multi-byte tools
        self.is_multi_byte = util.string_as_bool( root.get( "is_multi_byte", False ) )
        #Force history to fully refresh after job execution for this tool. Useful i.e. when an indeterminate number of outputs are created by a tool.
        self.force_history_refresh = util.string_as_bool( root.get( 'force_history_refresh', 'False' ) )
        #load input translator, used by datasource tools to change names/values of incoming parameters
        self.input_translator = root.find( "request_param_translation" )
        if self.input_translator:
            self.input_translator = ToolInputTranslator.from_element( self.input_translator )
        # Command line (template). Optional for tools that do not invoke a local program  
        command = root.find("command")
        if command is not None and command.text is not None:
            self.command = command.text.lstrip() # get rid of leading whitespace
            interpreter  = command.get("interpreter")
            if interpreter:
                # TODO: path munging for cluster/dataset server relocatability
                executable = self.command.split()[0]
                abs_executable = os.path.abspath(os.path.join(self.tool_dir, executable))
                self.command = self.command.replace(executable, abs_executable, 1)
                self.command = interpreter + " " + self.command
        else:
            self.command = ''
        # Parameters used to build URL for redirection to external app
        redirect_url_params = root.find( "redirect_url_params" )
        if redirect_url_params is not None and redirect_url_params.text is not None:
            # get rid of leading / trailing white space
            redirect_url_params = redirect_url_params.text.strip()
            # Replace remaining white space with something we can safely split on later
            # when we are building the params
            self.redirect_url_params = redirect_url_params.replace( ' ', '**^**' )
        else:
            self.redirect_url_params = ''
        # Short description of the tool
        self.description = util.xml_text(root, "description")
        # Job runner
        if self.app.config.start_job_runners is None:
            # Jobs are always local regardless of tool config if no additional
            # runners are started
            self.job_runner = "local:///"
        else:
            # Set job runner to the cluster default
            self.job_runner = self.app.config.default_cluster_job_runner
            for tup in self.app.config.tool_runners:
                if tup[0] == self.id.lower():
                    self.job_runner = tup[1]
                    break
        # Is this a 'hidden' tool (hidden in tool menu)
        self.hidden = util.xml_text(root, "hidden")
        if self.hidden: self.hidden = util.string_as_bool(self.hidden)
        # Load any tool specific code (optional) Edit: INS 5/29/2007,
        # allow code files to have access to the individual tool's
        # "module" if it has one.  Allows us to reuse code files, etc.
        self.code_namespace = dict()
        self.hook_map = {}
        for code_elem in root.findall("code"):
            for hook_elem in code_elem.findall("hook"):
                for key, value in hook_elem.items():
                    # map hook to function
                    self.hook_map[key]=value
            file_name = code_elem.get("file")
            code_path = os.path.join( self.tool_dir, file_name )
            execfile( code_path, self.code_namespace )
        # Load any tool specific options (optional)
        self.options = dict( sanitize=True, refresh=False )
        for option_elem in root.findall("options"):
            for option, value in self.options.copy().items():
                if isinstance(value, type(False)):
                    self.options[option] = util.string_as_bool(option_elem.get(option, str(value)))
                else:
                    self.options[option] = option_elem.get(option, str(value))
        self.options = Bunch(** self.options)
        # Parse tool inputs (if there are any required)
        self.parse_inputs( root )
        # Parse tool help
        self.parse_help( root )
        # Description of outputs produced by an invocation of the tool
        self.outputs = {}
        out_elem = root.find("outputs")
        if out_elem:
            for data_elem in out_elem.findall("data"):
                output = ToolOutput( data_elem.get("name") )
                output.format = data_elem.get("format", "data")
                output.change_format = data_elem.findall("change_format")
                output.metadata_source = data_elem.get("metadata_source", "")
                output.parent = data_elem.get("parent", None)
                output.label = util.xml_text( data_elem, "label" )
                output.count = int( data_elem.get("count", 1) )
                output.filters = data_elem.findall( 'filter' )
                self.outputs[ output.name ] = output
        # Any extra generated config files for the tool
        self.config_files = []
        conf_parent_elem = root.find("configfiles")
        if conf_parent_elem:
            for conf_elem in conf_parent_elem.findall( "configfile" ):
                name = conf_elem.get( "name" )
                filename = conf_elem.get( "filename", None )
                text = conf_elem.text
                self.config_files.append( ( name, filename, text ) )
        # Action
        action_elem = root.find( "action" )
        if action_elem is None:
            self.tool_action = DefaultToolAction()
        else:
            module = action_elem.get( 'module' )
            cls = action_elem.get( 'class' )
            mod = __import__( module, globals(), locals(), [cls])
            self.tool_action = getattr( mod, cls )()
        # User interface hints
        self.uihints = {}
        uihints_elem = root.find( "uihints" )
        if uihints_elem is not None:
            for key, value in uihints_elem.attrib.iteritems():
                self.uihints[ key ] = value
        # Tests
        tests_elem = root.find( "tests" )
        if tests_elem:
            try:
                self.parse_tests( tests_elem )
            except:
                log.exception( "Failed to parse tool tests" )
        else:
            self.tests = None
        # Determine if this tool can be used in workflows
        self.is_workflow_compatible = self.check_workflow_compatible()
            
    def parse_inputs( self, root ):
        """
        Parse the "<inputs>" element and create appropriate `ToolParameter`s.
        This implementation supports multiple pages and grouping constructs.
        """
        # Load parameters (optional)
        input_elem = root.find("inputs")
        if input_elem:
            # Handle properties of the input form
            self.check_values = util.string_as_bool( input_elem.get("check_values", "true") )
            self.nginx_upload = util.string_as_bool( input_elem.get( "nginx_upload", "false" ) )
            if self.nginx_upload and self.app.config.nginx_upload_path:
                self.action = input_elem.get( "action", self.app.config.nginx_upload_path + "?nginx_redir=/tool_runner/index" )
            else:
                self.action = input_elem.get( "action", "/tool_runner/index")
            self.target = input_elem.get( "target", "galaxy_main" )
            self.method = input_elem.get( "method", "post" )
            # Parse the actual parameters
            self.inputs = odict()
            self.inputs_by_page = list()
            self.display_by_page = list()
            enctypes = set()
            # Handle multiple page case
            pages = input_elem.findall( "page" )
            for page in ( pages or [ input_elem ] ):
                display, inputs = self.parse_input_page( page, enctypes )
                self.inputs_by_page.append( inputs )
                self.inputs.update( inputs )
                self.display_by_page.append( display )
            self.display = self.display_by_page[0]
            self.npages = len( self.inputs_by_page )
            self.last_page = len( self.inputs_by_page ) - 1
            self.has_multiple_pages = bool( self.last_page )
            # Determine the needed enctype for the form
            if len( enctypes ) == 0:
                self.enctype = "application/x-www-form-urlencoded"
            elif len( enctypes ) == 1:
                self.enctype = enctypes.pop()
            else:
                raise Exception, "Conflicting required enctypes: %s" % str( enctypes )
        # Check if the tool either has no parameters or only hidden (and
        # thus hardcoded) parameters. FIXME: hidden parameters aren't
        # parameters at all really, and should be passed in a different
        # way, making this check easier.
        self.input_required = False
        for param in self.inputs.values():
            if not isinstance( param, ( HiddenToolParameter, BaseURLToolParameter ) ):
                self.input_required = True
                break
                
    def parse_help( self, root ):
        """
        Parse the help text for the tool. Formatted in reStructuredText.
        This implementation supports multiple pages.
        """
        # TODO: Allow raw HTML or an external link.
        self.help = root.find("help")
        self.help_by_page = list()
        help_header = ""
        help_footer = ""
        if self.help is not None:
            help_pages = self.help.findall( "page" )
            help_header = self.help.text
            try:
                self.help = util.rst_to_html(self.help.text)
            except:
                log.exception( "error in help for tool %s" % self.name )
            # Multiple help page case
            if help_pages:
                for help_page in help_pages:
                    self.help_by_page.append( help_page.text )
                    help_footer = help_footer + help_page.tail
        # Each page has to rendered all-together because of backreferences allowed by rst
        try:
            self.help_by_page = [ util.rst_to_html( help_header + x + help_footer )
                                  for x in self.help_by_page ]
        except:
            log.exception( "error in multi-page help for tool %s" % self.name )
        # Pad out help pages to match npages ... could this be done better?
        while len( self.help_by_page ) < self.npages: 
            self.help_by_page.append( self.help )
            
    def parse_tests( self, tests_elem ):
        """
        Parse any "<test>" elements, create a `ToolTestBuilder` for each and
        store in `self.tests`.
        """
        self.tests = []
        for i, test_elem in enumerate( tests_elem.findall( 'test' ) ):
            name = test_elem.get( 'name', 'Test-%d' % (i+1) )
            maxseconds = int( test_elem.get( 'maxseconds', '120' ) )
            test = ToolTestBuilder( self, name, maxseconds )
            try:
                for param_elem in test_elem.findall( "param" ):
                    attrib = dict( param_elem.attrib )
                    if 'values' in attrib:
                        value = attrib[ 'values' ].split( ',' )
                    elif 'value' in attrib:
                        value = attrib['value']
                    else:
                        value = None
                    test.add_param( attrib.pop( 'name' ), value, attrib )
                for output_elem in test_elem.findall( "output" ):
                    attrib = dict( output_elem.attrib )
                    name = attrib.pop( 'name', None )
                    if name is None:
                        raise Exception( "Test output does not have a 'name'" )
                    file = attrib.pop( 'file', None )
                    if file is None:
                        raise Exception( "Test output does not have a 'file'")
                    test.add_output( name, file )
            except Exception, e:
                test.error = True
                test.exception = e
            self.tests.append( test )
            
    def parse_input_page( self, input_elem, enctypes ):
        """
        Parse a page of inputs. This basically just calls 'parse_input_elem',
        but it also deals with possible 'display' elements which are supported
        only at the top/page level (not in groups).
        """
        inputs = self.parse_input_elem( input_elem, enctypes )
        # Display
        display_elem = input_elem.find("display")
        if display_elem is not None:
            display = util.xml_to_string(display_elem)
        else:
            display = None
        return display, inputs
        
    def parse_input_elem( self, parent_elem, enctypes, context=None ):
        """
        Parse a parent element whose children are inputs -- these could be 
        groups (repeat, conditional) or param elements. Groups will be parsed
        recursively.
        """
        rval = odict()
        context = ExpressionContext( rval, context )
        for elem in parent_elem:
            # Repeat group
            if elem.tag == "repeat":
                group = Repeat()
                group.name = elem.get( "name" )
                group.title = elem.get( "title" ) 
                group.inputs = self.parse_input_elem( elem, enctypes, context )
                rval[group.name] = group
            elif elem.tag == "conditional":
                group = Conditional()
                group.name = elem.get( "name" )
                
                group.name = elem.get( "name" )
                
                group.value_ref = elem.get( 'value_ref', None )
                group.value_ref_in_group = util.string_as_bool( elem.get( 'value_ref_in_group', 'True' ) )
                value_from = elem.get( "value_from" )
                if value_from:
                    value_from = value_from.split( ':' )
                    group.value_from = locals().get( value_from[0] )
                    group.test_param = rval[ group.value_ref ]
                    group.test_param.refresh_on_change = True
                    for attr in value_from[1].split( '.' ):
                        group.value_from = getattr( group.value_from, attr )
                    for case_value, case_inputs in group.value_from( context, group, self ).iteritems():
                        case = ConditionalWhen()
                        case.value = case_value
                        if case_inputs:
                            case.inputs = self.parse_input_elem( ElementTree.XML( "<when>%s</when>" % case_inputs ), enctypes, context )
                        else:
                            case.inputs = {}
                        group.cases.append( case )
                else:
                    # Should have one child "input" which determines the case
                    input_elem = elem.find( "param" )
                    assert input_elem is not None, "<conditional> must have a child <param>"
                    group.test_param = self.parse_param_elem( input_elem, enctypes, context )
                    # Must refresh when test_param changes
                    group.test_param.refresh_on_change = True
                    # And a set of possible cases
                    for case_elem in elem.findall( "when" ):
                        case = ConditionalWhen()
                        case.value = case_elem.get( "value" )
                        case.inputs = self.parse_input_elem( case_elem, enctypes, context )
                        group.cases.append( case )
                rval[group.name] = group
            elif elem.tag == "upload_dataset":
                group = UploadDataset()
                group.name = elem.get( "name" )
                group.title = elem.get( "title" ) 
                group.file_type_name = elem.get( 'file_type_name', group.file_type_name )
                group.default_file_type = elem.get( 'default_file_type', group.default_file_type )
                group.metadata_ref = elem.get( 'metadata_ref', group.metadata_ref )
                rval[ group.file_type_name ].refresh_on_change = True
                rval[ group.file_type_name ].refresh_on_change_values = self.app.datatypes_registry.get_composite_extensions()
                group.inputs = self.parse_input_elem( elem, enctypes, context )
                rval[ group.name ] = group
            elif elem.tag == "param":
                param = self.parse_param_elem( elem, enctypes, context )
                rval[param.name] = param
        return rval

    def parse_param_elem( self, input_elem, enctypes, context ):
        """
        Parse a single "<param>" element and return a ToolParameter instance. 
        Also, if the parameter has a 'required_enctype' add it to the set
        enctypes.
        """
        param = ToolParameter.build( self, input_elem )
        param_enctype = param.get_required_enctype()
        if param_enctype:
            enctypes.add( param_enctype )
        # If parameter depends on any other paramters, we must refresh the
        # form when it changes
        for name in param.get_dependencies():
            context[ name ].refresh_on_change = True
        return param
    
    def check_workflow_compatible( self ):
        """
        Determine if a tool can be used in workflows. External tools and the
        upload tool are currently not supported by workflows.
        """
        # Multiple page tools are not supported -- we're eliminating most
        # of these anyway
        if self.has_multiple_pages:
            return False
        # This is probably the best bet for detecting external web tools
        # right now
        if self.action != "/tool_runner/index":
            return False
        # HACK: upload is (as always) a special case becuase file parameters
        #       can't be persisted.
        if self.id == "upload1":
            return False
        # TODO: Anyway to capture tools that dynamically change their own
        #       outputs?
        return True

    def new_state( self, trans, all_pages=False ):
        """
        Create a new `DefaultToolState` for this tool. It will be initialized
        with default values for inputs. 
        
        Only inputs on the first page will be initialized unless `all_pages` is
        True, in which case all inputs regardless of page are initialized.
        """
        state = DefaultToolState()
        state.inputs = {}
        if all_pages:
            inputs = self.inputs
        else:
            inputs = self.inputs_by_page[ 0 ]
        self.fill_in_new_state( trans, inputs, state.inputs )
        return state

    def fill_in_new_state( self, trans, inputs, state, context=None ):
        """
        Fill in a tool state dictionary with default values for all parameters
        in the dictionary `inputs`. Grouping elements are filled in recursively. 
        """
        context = ExpressionContext( state, context )
        for input in inputs.itervalues():
            state[ input.name ] = input.get_initial_value( trans, context )

    def get_param_html_map( self, trans, page=0, other_values={} ):
        """
        Return a dictionary containing the HTML representation of each 
        parameter. This is used for rendering display elements. It is 
        currently not compatible with grouping constructs.
        
        NOTE: This should be considered deprecated, it is only used for tools
              with `display` elements. These should be eliminated.
        """
        rval = dict()
        for key, param in self.inputs_by_page[page].iteritems():
            if not isinstance( param, ToolParameter ):
                raise Exception( "'get_param_html_map' only supported for simple paramters" )
            rval[key] = param.get_html( trans, other_values=other_values )
        return rval

    def get_param( self, key ):
        """
        Returns the parameter named `key` or None if there is no such 
        parameter.
        """
        return self.inputs.get( key, None )

    def get_hook(self, name):
        """
        Returns an object from the code file referenced by `code_namespace`
        (this will normally be a callable object)
        """
        if self.code_namespace:
            # Try to look up hook in self.hook_map, otherwise resort to default
            if name in self.hook_map and self.hook_map[name] in self.code_namespace:
                return self.code_namespace[self.hook_map[name]]
            elif name in self.code_namespace:
                return self.code_namespace[name]
        return None
        
    def visit_inputs( self, value, callback ):
        """
        Call the function `callback` on each parameter of this tool. Visits
        grouping parameters recursively and constructs unique prefixes for
        each nested set of parameters. The callback method is then called as:
        
        `callback( level_prefix, parameter, parameter_value )`
        """
        # HACK: Yet another hack around check_values -- WHY HERE?
        if not self.check_values:
            return
        for input in self.inputs.itervalues():
            if isinstance( input, ToolParameter ):
                callback( "", input, value[input.name] )
            else:
                input.visit_inputs( "", value[input.name], callback )

    def handle_input( self, trans, incoming ):
        """
        Process incoming parameters for this tool from the dict `incoming`,
        update the tool state (or create if none existed), and either return
        to the form or execute the tool (only if 'execute' was clicked and
        there were no errors).
        """
        # Get the state or create if not found
        if "tool_state" in incoming:
            encoded_state = util.string_to_object( incoming["tool_state"] )
            state = DefaultToolState()
            state.decode( encoded_state, self, trans.app )
        else:
            state = self.new_state( trans )
            # This feels a bit like a hack. It allows forcing full processing
            # of inputs even when there is no state in the incoming dictionary
            # by providing either 'runtool_btn' (the name of the submit button
            # on the standard run form) or "URL" (a parameter provided by
            # external data source tools). 
            if "runtool_btn" not in incoming and "URL" not in incoming:
                return "tool_form.mako", dict( errors={}, tool_state=state, param_values={}, incoming={} )
        # Process incoming data
        if not( self.check_values ):
            # If `self.check_values` is false we don't do any checking or
            # processing on input parameters. This is used to pass raw values
            # through to/from external sites. FIXME: This should be handled
            # more cleanly, there is no reason why external sites need to
            # post back to the same URL that the tool interface uses.
            errors = {}
            params = incoming
        else:
            # Update state for all inputs on the current page taking new
            # values from `incoming`.
            errors = self.update_state( trans, self.inputs_by_page[state.page], state.inputs, incoming )
            # If the tool provides a `validate_input` hook, call it. 
            validate_input = self.get_hook( 'validate_input' )
            if validate_input:
                validate_input( trans, errors, state.inputs, self.inputs_by_page[state.page] )
            params = state.inputs
        # Did the user actually click next / execute or is this just
        # a refresh?
        if 'runtool_btn' in incoming or 'URL' in incoming or 'ajax_upload' in incoming:
            # If there were errors, we stay on the same page and display 
            # error messages
            if errors:
                error_message = "One or more errors were found in the input you provided. The specific errors are marked below."    
                return "tool_form.mako", dict( errors=errors, tool_state=state, incoming=incoming, error_message=error_message )
            # If we've completed the last page we can execute the tool
            elif state.page == self.last_page:
                out_data = self.execute( trans, incoming=params )
                try:
                    assert type( out_data ) is types.DictType
                    return 'tool_executed.mako', dict( out_data=out_data )
                except:
                    return 'message.mako', dict( message_type='error', message=out_data, refresh_frames=[] )
            # Otherwise move on to the next page
            else:
                state.page += 1
                # Fill in the default values for the next page
                self.fill_in_new_state( trans, self.inputs_by_page[ state.page ], state.inputs )
                return 'tool_form.mako', dict( errors=errors, tool_state=state )
        else:
            try:
                self.find_fieldstorage( state.inputs )
            except InterruptedUpload:
                # If inputs contain a file it won't persist.  Most likely this
                # is an interrupted upload.  We should probably find a more
                # standard method of determining an incomplete POST.
                return self.handle_interrupted( trans, state.inputs )
            except:
                pass
            # Just a refresh, render the form with updated state and errors.
            return 'tool_form.mako', dict( errors=errors, tool_state=state )
      
    def find_fieldstorage( self, x ):
        if isinstance( x, FieldStorage ):
            raise InterruptedUpload( None )
        elif type( x ) is types.DictType:
            [ self.find_fieldstorage( y ) for y in x.values() ]
        elif type( x ) is types.ListType:
            [ self.find_fieldstorage( y ) for y in x ]

    def handle_interrupted( self, trans, inputs ):
        """
        Upon handling inputs, if it appears that we have received an incomplete
        form, do some cleanup or anything else deemed necessary.  Currently
        this is only likely during file uploads, but this method could be
        generalized and a method standardized for handling other tools.
        """
        # If the async upload tool has uploading datasets, we need to error them.
        if 'async_datasets' in inputs and inputs['async_datasets'] not in [ 'None', '', None ]:
            for id in inputs['async_datasets'].split(','):
                try:
                    data = self.sa_session.query( trans.model.HistoryDatasetAssociation ).get( int( id ) )
                except:
                    log.exception( 'Unable to load precreated dataset (%s) sent in upload form' % id )
                    continue
                if trans.user is None and trans.galaxy_session.current_history != data.history:
                    log.error( 'Got a precreated dataset (%s) but it does not belong to anonymous user\'s current session (%s)' % ( data.id, trans.galaxy_session.id ) ) 
                elif data.history.user != trans.user:
                    log.error( 'Got a precreated dataset (%s) but it does not belong to current user (%s)' % ( data.id, trans.user.id ) )
                else:
                    data.state = data.states.ERROR
                    data.info = 'Upload of this dataset was interrupted.  Please try uploading again or'
                    self.sa_session.add( data )
                    self.sa_session.flush()
        # It's unlikely the user will ever see this.
        return 'message.mako', dict( message_type='error', message='Your upload was interrupted.  If this was uninentional, please retry it.', refresh_frames=[], cont=None )

    def update_state( self, trans, inputs, state, incoming, prefix="", context=None,
                      update_only=False, old_errors={}, item_callback=None ):
        """
        Update the tool state in `state` using the user input in `incoming`. 
        This is designed to be called recursively: `inputs` contains the
        set of inputs being processed, and `prefix` specifies a prefix to
        add to the name of each input to extract it's value from `incoming`.
        
        If `update_only` is True, values that are not in `incoming` will
        not be modified. In this case `old_errors` can be provided, and any
        errors for parameters which were *not* updated will be preserved.
        """
        errors = dict()     
        # Push this level onto the context stack
        context = ExpressionContext( state, context )
        # Iterate inputs and update (recursively)
        for input in inputs.itervalues():
            key = prefix + input.name
            if isinstance( input, Repeat ):
                group_state = state[input.name]
                group_errors = []
                group_old_errors = old_errors.get( input.name, None )
                any_group_errors = False
                # Check any removals before updating state -- only one
                # removal can be performed, others will be ignored
                for i, rep_state in enumerate( group_state ):
                    rep_index = rep_state['__index__']
                    if key + "_" + str(rep_index) + "_remove" in incoming:
                        del group_state[i]
                        if group_old_errors:
                            del group_old_errors[i]
                        break
                # Update state
                max_index = -1
                for i, rep_state in enumerate( group_state ):
                    rep_index = rep_state['__index__']
                    max_index = max( max_index, rep_index )
                    rep_prefix = "%s_%d|" % ( key, rep_index )
                    if group_old_errors:
                        rep_old_errors = group_old_errors[i]
                    else:
                        rep_old_errors = {}
                    rep_errors = self.update_state( trans,
                                                    input.inputs, 
                                                    rep_state, 
                                                    incoming, 
                                                    prefix=rep_prefix,
                                                    context=context,
                                                    update_only=update_only,
                                                    old_errors=rep_old_errors,
                                                    item_callback=item_callback )
                    if rep_errors:
                        any_group_errors = True
                        group_errors.append( rep_errors )
                    else:
                        group_errors.append( {} )
                # Check for addition
                if key + "_add" in incoming:
                    new_state = {}
                    new_state['__index__'] = max_index + 1
                    self.fill_in_new_state( trans, input.inputs, new_state, context )
                    group_state.append( new_state )
                    if any_group_errors:
                        group_errors.append( {} )
                # Were there *any* errors for any repetition?
                if any_group_errors:
                    errors[input.name] = group_errors
            elif isinstance( input, Conditional ):
                group_state = state[input.name]
                group_old_errors = old_errors.get( input.name, {} )
                old_current_case = group_state['__current_case__']
                group_prefix = "%s|" % ( key )
                # Deal with the 'test' element and see if it's value changed
                if input.value_ref and not input.value_ref_in_group: #we are referencing an existant parameter, which is not part of this group
                    test_param_key = prefix + input.test_param.name
                else:
                    test_param_key = group_prefix + input.test_param.name
                test_param_error = None
                test_incoming = get_incoming_value( incoming, test_param_key, None )
                if test_param_key not in incoming \
                   and "__force_update__" + test_param_key not in incoming \
                   and update_only:
                    # Update only, keep previous value and state, but still
                    # recurse in case there are nested changes
                    value = group_state[ input.test_param.name ]
                    current_case = old_current_case
                    if input.test_param.name in old_errors:
                        errors[ input.test_param.name ] = old_errors[ input.test_param.name ]
                else:
                    # Get value of test param and determine current case
                    value, test_param_error = \
                        check_param( trans, input.test_param, test_incoming, context )
                    current_case = input.get_current_case( value, trans )
                if current_case != old_current_case:
                    # Current case has changed, throw away old state
                    group_state = state[input.name] = {}
                    # TODO: we should try to preserve values if we can
                    self.fill_in_new_state( trans, input.cases[current_case].inputs, group_state, context )
                    group_errors = dict()
                    group_old_errors = dict()
                else:
                    # Current case has not changed, update children
                    group_errors = self.update_state( trans, 
                                                      input.cases[current_case].inputs, 
                                                      group_state,
                                                      incoming, 
                                                      prefix=group_prefix,
                                                      context=context,
                                                      update_only=update_only,
                                                      old_errors=group_old_errors,
                                                      item_callback=item_callback )
                if test_param_error:
                    group_errors[ input.test_param.name ] = test_param_error
                if group_errors:
                    errors[ input.name ] = group_errors
                # Store the current case in a special value
                group_state['__current_case__'] = current_case
                # Store the value of the test element
                group_state[ input.test_param.name ] = value
            elif isinstance( input, UploadDataset ):
                group_state = state[input.name]
                group_errors = []
                group_old_errors = old_errors.get( input.name, None )
                any_group_errors = False
                d_type = input.get_datatype( trans, context )
                writable_files = d_type.writable_files
                #remove extra files
                while len( group_state ) > len( writable_files ):
                    del group_state[-1]
                    if group_old_errors:
                        del group_old_errors[-1]
                # Update state
                max_index = -1
                for i, rep_state in enumerate( group_state ):
                    rep_index = rep_state['__index__']
                    max_index = max( max_index, rep_index )
                    rep_prefix = "%s_%d|" % ( key, rep_index )
                    if group_old_errors:
                        rep_old_errors = group_old_errors[i]
                    else:
                        rep_old_errors = {}
                    rep_errors = self.update_state( trans,
                                                    input.inputs, 
                                                    rep_state, 
                                                    incoming, 
                                                    prefix=rep_prefix,
                                                    context=context,
                                                    update_only=update_only,
                                                    old_errors=rep_old_errors,
                                                    item_callback=item_callback )
                    if rep_errors:
                        any_group_errors = True
                        group_errors.append( rep_errors )
                    else:
                        group_errors.append( {} )
                #add new fileupload as needed
                offset = 1
                while len( writable_files ) > len( group_state ):
                    new_state = {}
                    new_state['__index__'] = max_index + offset
                    offset += 1
                    self.fill_in_new_state( trans, input.inputs, new_state, context )
                    group_state.append( new_state )
                    if any_group_errors:
                        group_errors.append( {} )
                # Were there *any* errors for any repetition?
                if any_group_errors:
                    errors[input.name] = group_errors
            else:
                if key not in incoming \
                   and "__force_update__" + key not in incoming \
                   and update_only:
                    # No new value provided, and we are only updating, so keep
                    # the old value (which should already be in the state) and
                    # preserve the old error message.
                    if input.name in old_errors:
                        errors[ input.name ] = old_errors[ input.name ]
                else:
                    incoming_value = get_incoming_value( incoming, key, None )
                    value, error = check_param( trans, input, incoming_value, context )
                    # If a callback was provided, allow it to process the value
                    if item_callback:
                        old_value = state.get( input.name, None )
                        value, error = item_callback( trans, key, input, value, error, old_value, context )                                          
                    if error:
                        errors[ input.name ] = error
                    state[ input.name ] = value
        return errors
            
    def get_static_param_values( self, trans ):
        """
        Returns a map of parameter names and values if the tool does not 
        require any user input. Will raise an exception if any parameter
        does require input.
        """
        args = dict()
        for key, param in self.inputs.iteritems():
            if isinstance( param, HiddenToolParameter ):
                args[key] = param.value
            elif isinstance( param, BaseURLToolParameter ):
                args[key] = param.get_value( trans )
            else:
                raise Exception( "Unexpected parameter type" )
        return args
            
    def execute( self, trans, incoming={}, set_output_hid=True ):
        """
        Execute the tool using parameter values in `incoming`. This just
        dispatches to the `ToolAction` instance specified by 
        `self.tool_action`. In general this will create a `Job` that 
        when run will build the tool's outputs, e.g. `DefaultToolAction`.
        """
        return self.tool_action.execute( self, trans, incoming=incoming, set_output_hid=set_output_hid )
        
    def params_to_strings( self, params, app ):
        return params_to_strings( self.inputs, params, app )
        
    def params_from_strings( self, params, app, ignore_errors=False ):
        return params_from_strings( self.inputs, params, app, ignore_errors )
        
            
    def check_and_update_param_values( self, values, trans ):
        """
        Check that all parameters have values, and fill in with default
        values where neccesary. This could be called after loading values
        from a database in case new parameters have been added. 
        """
        messages = []
        self.check_and_update_param_values_helper( self.inputs, values, trans, messages )
        return messages
        
    def check_and_update_param_values_helper( self, inputs, values, trans, messages, context=None, prefix="" ):
        """
        Recursive helper for `check_and_update_param_values_helper`
        """
        context = ExpressionContext( values, context )
        for input in inputs.itervalues():
            # No value, insert the default
            if input.name not in values:
                messages.append( prefix + input.label )
                values[input.name] = input.get_initial_value( trans, context )
            # Value, visit recursively as usual
            else:
                if isinstance( input, Repeat ):
                    for i, d in enumerate( values[ input.name ] ):
                        rep_prefix = prefix + "%s %d > " % ( input.title, i + 1 )
                        self.check_and_update_param_values_helper( input.inputs, d, trans, messages, context, rep_prefix )
                elif isinstance( input, Conditional ):
                    group_values = values[ input.name ]
                    current = group_values["__current_case__"]
                    self.check_and_update_param_values_helper( input.cases[current].inputs, group_values, trans, messages, context, prefix )
                else:
                    # Regular tool parameter, no recursion needed
                    pass        
    
    def handle_unvalidated_param_values( self, input_values, app ):
        """
        Find any instances of `UnvalidatedValue` within input_values and
        validate them (by calling `ToolParameter.from_html` and 
        `ToolParameter.validate`).
        """
        # No validation is done when check_values is False
        if not self.check_values:
            return
        self.handle_unvalidated_param_values_helper( self.inputs, input_values, app )

    def handle_unvalidated_param_values_helper( self, inputs, input_values, app, context=None, prefix="" ):
        """
        Recursive helper for `handle_unvalidated_param_values`
        """
        context = ExpressionContext( input_values, context )
        for input in inputs.itervalues():
            if isinstance( input, Repeat ):  
                for i, d in enumerate( input_values[ input.name ] ):
                    rep_prefix = prefix + "%s %d > " % ( input.title, i + 1 )
                    self.handle_unvalidated_param_values_helper( input.inputs, d, app, context, rep_prefix )
            elif isinstance( input, Conditional ):
                values = input_values[ input.name ]
                current = values["__current_case__"]
                # NOTE: The test param doesn't need to be checked since
                #       there would be no way to tell what case to use at
                #       workflow build time. However I'm not sure if we are
                #       actually preventing such a case explicately.
                self.handle_unvalidated_param_values_helper( input.cases[current].inputs, values, app, context, prefix )
            else:
                # Regular tool parameter
                value = input_values[ input.name ]
                if isinstance( value, UnvalidatedValue ):
                    try:
                        # Convert from html representation
                        if value.value is None:
                            # If value.value is None, it could not have been
                            # submited via html form and therefore .from_html
                            # can't be guaranteed to work
                            value = None
                        else:
                            value = input.from_html( value.value, None, context )
                        # Do any further validation on the value
                        input.validate( value, None )
                    except Exception, e:
                        # Wrap an re-raise any generated error so we can
                        # generate a more informative message
                        v = input.value_to_display_text( value, self.app )
                        message = "Failed runtime validation of %s%s (%s)" \
                            % ( prefix, input.label, e )
                        raise LateValidationError( message )
                    input_values[ input.name ] = value
    
    def handle_job_failure_exception( self, e ):
        """
        Called by job.fail when an exception is generated to allow generation
        of a better error message (returning None yields the default behavior)
        """
        message = None
        # If the exception was generated by late validation, use its error
        # message (contains the parameter name and value)
        if isinstance( e, LateValidationError ):
            message = e.message
        return message
    
    def build_param_dict( self, incoming, input_datasets, output_datasets, output_paths, job_working_directory ):
        """
        Build the dictionary of parameters for substituting into the command
        line. Each value is wrapped in a `InputValueWrapper`, which allows
        all the attributes of the value to be used in the template, *but* 
        when the __str__ method is called it actually calls the 
        `to_param_dict_value` method of the associated input.
        """
        param_dict = dict()
        # All parameters go into the param_dict
        param_dict.update( incoming )
        # Wrap parameters as neccesary
        def wrap_values( inputs, input_values ):
            for input in inputs.itervalues():
                if isinstance( input, Repeat ):  
                    for d in input_values[ input.name ]:
                        wrap_values( input.inputs, d )
                elif isinstance( input, Conditional ):
                    values = input_values[ input.name ]
                    current = values["__current_case__"]
                    wrap_values( input.cases[current].inputs, values )
                elif isinstance( input, DataToolParameter ):
                    input_values[ input.name ] = \
                        DatasetFilenameWrapper( input_values[ input.name ],
                                                datatypes_registry = self.app.datatypes_registry,
                                                tool = self,
                                                name = input.name )
                elif isinstance( input, SelectToolParameter ):
                    input_values[ input.name ] = SelectToolParameterWrapper( input, input_values[ input.name ], self.app, other_values = param_dict )
                else:
                    input_values[ input.name ] = InputValueWrapper( input, input_values[ input.name ], param_dict )
        # HACK: only wrap if check_values is not false, this deals with external
        #       tools where the inputs don't even get passed through. These
        #       tools (e.g. UCSC) should really be handled in a special way.
        if self.check_values:
            wrap_values( self.inputs, param_dict )
        # Additionally, datasets go in the param dict. We wrap them such that
        # if the bare variable name is used it returns the filename (for
        # backwards compatibility). We also add any child datasets to the
        # the param dict encoded as:
        #   "_CHILD___{dataset_name}___{child_designation}",
        # but this should be considered DEPRECATED, instead use:
        #   $dataset.get_child( 'name' ).filename
        for name, data in input_datasets.items():
            param_dict[name] = DatasetFilenameWrapper( data, 
                                                       datatypes_registry = self.app.datatypes_registry, 
                                                       tool = self, 
                                                       name = name )
            if data:
                for child in data.children:
                    param_dict[ "_CHILD___%s___%s" % ( name, child.designation ) ] = DatasetFilenameWrapper( child )
        for name, hda in output_datasets.items():
            # Write outputs to the working directory (for security purposes) if desired.
            if self.app.config.outputs_to_working_directory:
                try:
                    false_path = [ dp.false_path for dp in output_paths if dp.real_path == hda.file_name ][0]
                    param_dict[name] = DatasetFilenameWrapper( hda, false_path = false_path )
                    open( false_path, 'w' ).close()
                except IndexError:
                    log.warning( "Unable to determine alternate path for writing job outputs, outputs will be written to their real paths" )
                    param_dict[name] = DatasetFilenameWrapper( hda )
            else:
                param_dict[name] = DatasetFilenameWrapper( hda )
            # Provide access to a path to store additional files
            # TODO: path munging for cluster/dataset server relocatability
            param_dict[name].files_path = os.path.abspath(os.path.join( job_working_directory, "dataset_%s_files" % (hda.dataset.id) ))
            for child in hda.children:
                param_dict[ "_CHILD___%s___%s" % ( name, child.designation ) ] = DatasetFilenameWrapper( child )
        for out_name, output in self.outputs.iteritems():
            if out_name not in param_dict and output.filters:
                #assume the reason we lack this output is because a filter failed to pass; for tool writing convienence, provide a NoneDataset
                param_dict[ out_name ] = NoneDataset( datatypes_registry = self.app.datatypes_registry, ext = output.format )
        # We add access to app here, this allows access to app.config, etc
        param_dict['__app__'] = RawObjectWrapper( self.app )
        # More convienent access to app.config.new_file_path; we don't need to wrap a string
        # But this method of generating additional datasets should be considered DEPRECATED
        # TODO: path munging for cluster/dataset server relocatability
        param_dict['__new_file_path__'] = os.path.abspath(self.app.config.new_file_path)
        # The following points to location (xxx.loc) files which are pointers to locally cached data
        param_dict['GALAXY_DATA_INDEX_DIR'] = self.app.config.tool_data_path
        # Return the dictionary of parameters
        return param_dict
    
    def build_param_file( self, param_dict, directory=None ):
        """
        Build temporary file for file based parameter transfer if needed
        """
        if self.command and "$param_file" in self.command:
            fd, param_filename = tempfile.mkstemp( dir=directory )
            os.close( fd )
            f = open( param_filename, "wt" )
            for key, value in param_dict.items():
                # parameters can be strings or lists of strings, coerce to list
                if type(value) != type([]):
                    value = [ value ]
                for elem in value:
                    f.write( '%s=%s\n' % (key, elem) ) 
            f.close()
            param_dict['param_file'] = param_filename
            return param_filename
        else:
            return None
            
    def build_config_files( self, param_dict, directory=None ):
        """
        Build temporary file for file based parameter transfer if needed
        """
        config_filenames = []
        for name, filename, template_text in self.config_files:
            # If a particular filename was forced by the config use it
            if filename is not None:
                if directory is None:
                    raise Exception( "Config files with fixed filenames require a working directory" )
                config_filename = os.path.join( directory, filename )
            else:
                fd, config_filename = tempfile.mkstemp( dir=directory )
                os.close( fd )
            f = open( config_filename, "wt" )
            f.write( fill_template( template_text, context=param_dict ) )
            f.close()
            param_dict[name] = config_filename
            config_filenames.append( config_filename )
        return config_filenames
        
    def build_command_line( self, param_dict ):
        """
        Build command line to invoke this tool given a populated param_dict
        """
        command_line = None
        if not self.command:
            return
        try:                
            # Substituting parameters into the command
            command_line = fill_template( self.command, context=param_dict )
            # Remove newlines from command line
            command_line = command_line.replace( "\n", " " ).replace( "\r", " " )
        except Exception, e:
            # Modify exception message to be more clear
            #e.args = ( 'Error substituting into command line. Params: %r, Command: %s' % ( param_dict, self.command ) )
            raise
        return command_line

    def build_redirect_url_params( self, param_dict ):
        """Substitute parameter values into self.redirect_url_params"""
        if not self.redirect_url_params:
            return
        redirect_url_params = None            
        # Substituting parameter values into the url params
        redirect_url_params = fill_template( self.redirect_url_params, context=param_dict )
        # Remove newlines
        redirect_url_params = redirect_url_params.replace( "\n", " " ).replace( "\r", " " )
        return redirect_url_params

    def parse_redirect_url( self, data, param_dict ):
        """Parse the REDIRECT_URL tool param"""
        # Tools that send data to an external application via a redirect must include the following 3 tool params:
        # REDIRECT_URL - the url to which the data is being sent
        # DATA_URL - the url to which the receiving application will send an http post to retrieve the Galaxy data
        # GALAXY_URL - the url to which the external application may post data as a response
        redirect_url = param_dict.get( 'REDIRECT_URL' )
        redirect_url_params = self.build_redirect_url_params( param_dict )
        # Add the parameters to the redirect url.  We're splitting the param string on '**^**'
        # because the self.parse() method replaced white space with that separator.
        params = redirect_url_params.split( '**^**' )
        rup_dict = {}
        for param in params:
            p_list = param.split( '=' )
            p_name = p_list[0]
            p_val = p_list[1]
            rup_dict[ p_name ] = p_val
        DATA_URL = param_dict.get( 'DATA_URL', None )
        assert DATA_URL is not None, "DATA_URL parameter missing in tool config."
        DATA_URL += "/%s/display" % str( data.id )
        redirect_url += "?DATA_URL=%s" % DATA_URL
        # Add the redirect_url_params to redirect_url
        for p_name in rup_dict:
            redirect_url += "&%s=%s" % ( p_name, rup_dict[ p_name ] )
        # Add the current user email to redirect_url
        if data.history.user:
            USERNAME = str( data.history.user.email )
        else:
            USERNAME = 'Anonymous'
        redirect_url += "&USERNAME=%s" % USERNAME
        return redirect_url

    def call_hook( self, hook_name, *args, **kwargs ):
        """
        Call the custom code hook function identified by 'hook_name' if any,
        and return the results
        """
        try:
            code = self.get_hook( hook_name )
            if code:
                return code( *args, **kwargs )
        except Exception, e:
            e.args = ( "Error in '%s' hook '%s', original message: %s" % ( self.name, hook_name, e.args[0] ) )
            raise

    def exec_before_job( self, app, inp_data, out_data, param_dict={} ):
        pass

    def exec_after_process( self, app, inp_data, out_data, param_dict, job = None ):
        pass

    def collect_associated_files( self, output, job_working_directory ):
        for name, hda in output.items():
            temp_file_path = os.path.join( job_working_directory, "dataset_%s_files" % ( hda.dataset.id ) )
            try:
                if len( os.listdir( temp_file_path ) ) > 0:
                    store_file_path = os.path.join( os.path.join( self.app.config.file_path, *directory_hash_id( hda.dataset.id ) ), "dataset_%d_files" % hda.dataset.id )
                    shutil.move( temp_file_path, store_file_path )
                    # fix permissions
                    for basedir, dirs, files in os.walk( store_file_path ):
                        util.umask_fix_perms( basedir, self.app.config.umask, 0777, self.app.config.gid )
                        for file in files:
                            path = os.path.join( basedir, file )
                            if os.path.islink( path ):
                                continue # ignore symlinks
                            util.umask_fix_perms( path, self.app.config.umask, 0666, self.app.config.gid )
            except:
                continue
    
    def collect_child_datasets( self, output):
        children = {}
        #Loop through output file names, looking for generated children in form of 'child_parentId_designation_visibility_extension'
        for name, outdata in output.items():
            for filename in glob.glob(os.path.join(self.app.config.new_file_path,"child_%i_*" % outdata.id) ):
                if not name in children:
                    children[name] = {}
                fields = os.path.basename(filename).split("_")
                fields.pop(0)
                parent_id = int(fields.pop(0))
                designation = fields.pop(0)
                visible = fields.pop(0).lower()
                if visible == "visible": visible = True
                else: visible = False
                ext = fields.pop(0).lower()
                child_dataset = self.app.model.HistoryDatasetAssociation( extension=ext,
                                                                          parent_id=outdata.id,
                                                                          designation=designation,
                                                                          visible=visible,
                                                                          dbkey=outdata.dbkey,
                                                                          create_dataset=True,
                                                                          sa_session=self.sa_session )
                self.app.security_agent.copy_dataset_permissions( outdata.dataset, child_dataset.dataset )
                # Move data from temp location to dataset location
                shutil.move( filename, child_dataset.file_name )
                self.sa_session.add( child_dataset )
                self.sa_session.flush()
                child_dataset.set_size()
                child_dataset.name = "Secondary Dataset (%s)" % ( designation )
                child_dataset.init_meta()
                child_dataset.set_meta()
                child_dataset.set_peek()
                # Associate new dataset with job
                job = None
                for assoc in outdata.creating_job_associations:
                    job = assoc.job
                    break   
                if job:
                    assoc = self.app.model.JobToOutputDatasetAssociation( '__new_child_file_%s|%s__' % ( name, designation ), child_dataset )
                    assoc.job = job
                    self.sa_session.add( assoc )
                    self.sa_session.flush()
                child_dataset.state = outdata.state
                self.sa_session.add( child_dataset )
                self.sa_session.flush()
                # Add child to return dict 
                children[name][designation] = child_dataset
                for dataset in outdata.dataset.history_associations: #need to update all associated output hdas, i.e. history was shared with job running
                    if outdata == dataset: continue
                    # Create new child dataset
                    child_data = child_dataset.copy( parent_id = dataset.id )
                    self.sa_session.add( child_dataset )
                    self.sa_session.flush()
        return children
        
    def collect_primary_datasets( self, output):
        primary_datasets = {}
        #Loop through output file names, looking for generated primary datasets in form of 'primary_associatedWithDatasetID_designation_visibility_extension(_DBKEY)'
        for name, outdata in output.items():
            for filename in glob.glob(os.path.join(self.app.config.new_file_path,"primary_%i_*" % outdata.id) ):
                if not name in primary_datasets:
                    primary_datasets[name] = {}
                fields = os.path.basename(filename).split("_")
                fields.pop(0)
                parent_id = int(fields.pop(0))
                designation = fields.pop(0)
                visible = fields.pop(0).lower()
                if visible == "visible": visible = True
                else: visible = False
                ext = fields.pop(0).lower()
                dbkey = outdata.dbkey
                if fields:
                    dbkey = fields[ 0 ]
                # Create new primary dataset
                primary_data = self.app.model.HistoryDatasetAssociation( extension=ext,
                                                                         designation=designation,
                                                                         visible=visible,
                                                                         dbkey=dbkey,
                                                                         create_dataset=True,
                                                                         sa_session=self.sa_session )
                self.app.security_agent.copy_dataset_permissions( outdata.dataset, primary_data.dataset )
                self.sa_session.add( primary_data )
                self.sa_session.flush()
                # Move data from temp location to dataset location
                shutil.move( filename, primary_data.file_name )
                primary_data.set_size()
                primary_data.name = outdata.name
                primary_data.info = outdata.info
                primary_data.init_meta( copy_from=outdata )
                primary_data.dbkey = dbkey
                primary_data.set_meta()
                primary_data.set_peek()
                # Associate new dataset with job
                job = None
                for assoc in outdata.creating_job_associations:
                    job = assoc.job
                    break   
                if job:
                    assoc = self.app.model.JobToOutputDatasetAssociation( '__new_primary_file_%s|%s__' % ( name, designation ), primary_data )
                    assoc.job = job
                    self.sa_session.add( assoc )
                    self.sa_session.flush()
                primary_data.state = outdata.state
                self.sa_session.add( primary_data )
                self.sa_session.flush()
                outdata.history.add_dataset( primary_data )
                # Add dataset to return dict 
                primary_datasets[name][designation] = primary_data
                for dataset in outdata.dataset.history_associations: #need to update all associated output hdas, i.e. history was shared with job running
                    if outdata == dataset: continue
                    new_data = primary_data.copy()
                    dataset.history.add( new_data )
                    self.sa_session.add( new_data )
                    self.sa_session.flush()
        return primary_datasets

class DataSourceTool( Tool ):
    tool_type = 'data_source'
    def exec_before_job( self, app, inp_data, out_data, param_dict={} ):
        #TODO: Allow for a generic way for all Tools to have output dataset properties be set to input parameter values
        #as defined in a tool XML
        dbkey = param_dict.get( 'dbkey' )
        organism = param_dict.get( 'organism' )
        table = param_dict.get( 'table' )
        description = param_dict.get( 'description' )
        info = param_dict.get( 'info' )
        if description == 'range':
            description = param_dict.get( 'position', '' )
            if not description:
                description = 'unknown position'
        gb_landmark_region = param_dict.get( 'q' )
        data_type = param_dict.get( 'data_type' )
        items = out_data.items()
        for name, data in items:
            if organism and table and description:
                # This is UCSC
                data.name  = '%s on %s: %s (%s)' % ( data.name, organism, table, description )
            elif gb_landmark_region:
                # This is GBrowse
                data.name = '%s on %s' % ( data.name, gb_landmark_region )
            data.info = info
            data.dbkey = dbkey
            if data_type not in app.datatypes_registry.datatypes_by_extension:
                # Setting data_type to tabular will force the data to be sniffed in exec_after_process()
                data_type = 'tabular'
            data.change_datatype( data_type )
            # Store external data source's request parameters temporarily in output file.
            # In case the config setting for "outputs_to_working_directory" is True, we must write to
            # the DatasetFilenameWrapper object in the param_dict since it's "false_path" attribute
            # is the temporary path to the output dataset ( until the job is run ).  However,
            # even if the "outputs_to_working_directory" setting is False, we can still open the file
            # the same way for temporarily storing the request parameters.
            
            ## TODO: Input parameters should be jsonified and written into a <configfile> and passed to data_source.py,
            ## instead of writing tab separated key, value pairs to the output file
            out = open( str( param_dict.get( name ) ), 'w' )
            for key, value in param_dict.items():
                print >> out, '%s\t%s' % ( key, value )
            out.close()

    def exec_after_process( self, app, inp_data, out_data, param_dict, job = None ):
        log.debug('after proc called')
        name, data = out_data.items()[0]
        data.set_size()
        #TODO: these should be already be set before the tool runs:
        if data.state == data.states.OK:
            data.name = param_dict.get( 'name', data.name )
            data.info = param_dict.get( 'info', data.name )
            data.dbkey = param_dict.get( 'dbkey', data.dbkey )
            data.extension = param_dict.get( 'data_type', data.extension )
        #TODO: these should be possible as part of data_source.py and external set_meta, see the upload tool:
        if data.extension in [ 'txt', 'tabular' ]:
            data_type = sniff.guess_ext( data.file_name, sniff_order=app.datatypes_registry.sniff_order )
            if data.extension != data_type:
                data.change_datatype( data_type )
        elif not isinstance( data.datatype, datatypes.interval.Bed ) and isinstance( data.datatype, datatypes.interval.Interval ):
            if data.missing_meta(): 
                data.change_datatype( 'tabular' )
        data.set_peek()
        self.sa_session.add( data )
        self.sa_session.flush()

class DataDestinationTool( Tool ):
    tool_type = 'data_destination'

class SetMetadataTool( Tool ):
    tool_type = 'set_metadata'
    def exec_after_process( self, app, inp_data, out_data, param_dict, job = None ):
        for name, dataset in inp_data.iteritems():
            external_metadata = galaxy.datatypes.metadata.JobExternalOutputMetadataWrapper( job )
            if external_metadata.external_metadata_set_successfully( dataset, app.model.context ):
                dataset.metadata.from_JSON_dict( external_metadata.get_output_filenames_by_dataset( dataset, app.model.context ).filename_out )    
            # If setting external metadata has failed, how can we inform the user?
            # For now, we'll leave the default metadata and set the state back to its original.
            dataset.datatype.after_setting_metadata( dataset )
            dataset.state = param_dict.get( '__ORIGINAL_DATASET_STATE__' )
            self.sa_session.add( dataset )
            self.sa_session.flush()

#load tool_type to ToolClass mappings
tool_types = {}
for tool_class in [ Tool, DataDestinationTool, SetMetadataTool, DataSourceTool ]:
    tool_types[ tool_class.tool_type ] = tool_class

# ---- Utility classes to be factored out -----------------------------------
        
class BadValue( object ):
    def __init__( self, value ):
        self.value = value

class RawObjectWrapper( object ):
    """
    Wraps an object so that __str__ returns module_name:class_name.
    """
    def __init__( self, obj ):
        self.obj = obj
    def __str__( self ):
        return "%s:%s" % (self.obj.__module__, self.obj.__class__.__name__)
    def __getattr__( self, key ):
        return getattr( self.obj, key )

class InputValueWrapper( object ):
    """
    Wraps an input so that __str__ gives the "param_dict" representation.
    """
    def __init__( self, input, value, other_values={} ):
        self.input = input
        self.value = value
        self._other_values = other_values
    def __str__( self ):
        return self.input.to_param_dict_string( self.value, self._other_values )
    def __getattr__( self, key ):
        return getattr( self.value, key )

class SelectToolParameterWrapper( object ):
    """
    Wraps a SelectTooParameter so that __str__ returns the selected value, but all other
    attributes are accessible.
    """
    def __init__( self, input, value, app, other_values={} ):
        self.input = input
        self.value = value
        self.input.value_label = input.value_to_display_text( value, app )
        self._other_values = other_values
    def __str__( self ):
        return self.input.to_param_dict_string( self.value, other_values = self._other_values )
    def __getattr__( self, key ):
        return getattr( self.input, key )

class DatasetFilenameWrapper( object ):
    """
    Wraps a dataset so that __str__ returns the filename, but all other
    attributes are accessible.
    """
    
    class MetadataWrapper:
        """
        Wraps a Metadata Collection to return MetadataParameters wrapped according to the metadata spec.
        Methods implemented to match behavior of a Metadata Collection.
        """
        def __init__( self, metadata ):
            self.metadata = metadata
        def __getattr__( self, name ):
            rval = self.metadata.get( name, None )
            if name in self.metadata.spec:
                if rval is None:
                    rval = self.metadata.spec[name].no_value
                rval = self.metadata.spec[name].param.to_string( rval )
                setattr( self, name, rval ) #lets store this value, so we don't need to recalculate if needed again
            return rval
        def __nonzero__( self ):
            return self.metadata.__nonzero__()
        def __iter__( self ):
            return self.metadata.__iter__()
        def get( self, key, default=None ):
            try:
                return getattr( self, key )
            except:
                return default
        def items( self ):
            return iter( [ ( k, self.get( k ) ) for k, v in self.metadata.items() ] )
    
    def __init__( self, dataset, datatypes_registry = None, tool = None, name = None, false_path = None ):
        if not dataset:
            try:
                #TODO: allow this to work when working with grouping
                ext = tool.inputs[name].extensions[0]
            except:
                ext = 'data'
            self.dataset = NoneDataset( datatypes_registry = datatypes_registry, ext = ext )
        else:
            self.dataset = dataset
            self.metadata = self.MetadataWrapper( dataset.metadata )
        self.false_path = false_path
    def __str__( self ):
        if self.false_path is not None:
            return self.false_path
        else:
            return self.dataset.file_name
    def __getattr__( self, key ):
        if self.false_path is not None and key == 'file_name':
            return self.false_path
        else:
            return getattr( self.dataset, key )
        
def json_fix( val ):
    if isinstance( val, list ):
        return [ json_fix( v ) for v in val ]
    elif isinstance( val, dict ):
        return dict( [ ( json_fix( k ), json_fix( v ) ) for ( k, v ) in val.iteritems() ] )
    elif isinstance( val, unicode ):
        return val.encode( "utf8" )
    else:
        return val
    
def get_incoming_value( incoming, key, default ):
    if "__" + key + "__is_composite" in incoming:
        composite_keys = incoming["__" + key + "__keys"].split()
        value = dict()
        for composite_key in composite_keys:
            value[composite_key] = incoming[key + "_" + composite_key]
        return value
    else:
        return incoming.get( key, default )

class InterruptedUpload( Exception ):
    pass
