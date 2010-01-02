"""
Basic tool parameters.
"""

import logging, string, sys, os, os.path
from elementtree.ElementTree import XML, Element
from galaxy import config, datatypes, util
from galaxy.web import form_builder
from galaxy.util.bunch import Bunch
from galaxy.util import string_as_bool, sanitize_param
from sanitize import ToolParameterSanitizer
import validation, dynamic_options
# For BaseURLToolParameter
from galaxy.web import url_for
import galaxy.model

log = logging.getLogger(__name__)

class ToolParameter( object ):
    """
    Describes a parameter accepted by a tool. This is just a simple stub at the
    moment but in the future should encapsulate more complex parameters (lists
    of valid choices, validation logic, ...)
    """
    def __init__( self, tool, param, context=None ):
        self.tool = tool
        self.refresh_on_change = False
        self.refresh_on_change_values = []
        self.name = param.get("name")
        self.type = param.get("type")
        self.label = util.xml_text(param, "label")
        self.help = util.xml_text(param, "help")
        self.sanitizer = param.find( "sanitizer" )
        if self.sanitizer is not None:
            self.sanitizer = ToolParameterSanitizer.from_element( self.sanitizer )
        self.html = "no html set"
        self.repeat = param.get("repeat", None)
        self.condition = param.get( "condition", None )
        self.validators = []
        for elem in param.findall("validator"):
            self.validators.append( validation.Validator.from_element( self, elem ) )

    def get_label( self ):
        """Return user friendly name for the parameter"""
        if self.label: return self.label
        else: return self.name

    def get_html_field( self, trans=None, value=None, other_values={} ):
        raise TypeError( "Abstract Method" )

    def get_html( self, trans=None, value=None, other_values={}):
        """
        Returns the html widget corresponding to the paramter. 
        Optionally attempt to retain the current value specific by 'value'
        """
        return self.get_html_field( trans, value, other_values ).get_html()
        
    def from_html( self, value, trans=None, other_values={} ):
        """
        Convert a value from an HTML POST into the parameters prefered value 
        format. 
        """
        return value
        
    def get_initial_value( self, trans, context ):
        """
        Return the starting value of the parameter
        """
        return None

    def get_required_enctype( self ):
        """
        If this parameter needs the form to have a specific encoding
        return it, otherwise return None (indicating compatibility with
        any encoding)
        """
        return None
        
    def get_dependencies( self ):
        """
        Return the names of any other parameters this parameter depends on
        """
        return []
        
    def filter_value( self, value, trans=None, other_values={} ):
        """
        Parse the value returned by the view into a form usable by the tool OR
        raise a ValueError.
        """
        return value
        
    def to_string( self, value, app ):
        """Convert a value to a string representation suitable for persisting"""
        return str( value )
    
    def to_python( self, value, app ):
        """Convert a value created with to_string back to an object representation"""
        return value
        
    def value_to_basic( self, value, app ):
        if isinstance( value, RuntimeValue ):
            return { "__class__": "RuntimeValue" }
        return self.to_string( value, app )
        
    def value_from_basic( self, value, app, ignore_errors=False ):
        # HACK: Some things don't deal with unicode well, psycopg problem?
        if type( value ) == unicode:
            value = str( value )
        # Handle Runtime values (valid for any parameter?)
        if isinstance( value, dict ) and '__class__' in value and value['__class__'] == "RuntimeValue":
            return RuntimeValue()
        # Delegate to the 'to_python' method
        if ignore_errors:
            try:
                return self.to_python( value, app )
            except:
                return value
        else:
            return self.to_python( value, app )
            
    def value_to_display_text( self, value, app ):
        """
        Convert a value to a text representation suitable for displaying to
        the user
        """
        return value
        
    def to_param_dict_string( self, value, other_values={} ):
        value = str( value )
        if self.tool is None or self.tool.options.sanitize:
            if self.sanitizer:
                value = self.sanitizer.sanitize_param( value )
            else:
                value = sanitize_param( value )
        return value
        
    def validate( self, value, history=None ):
        for validator in self.validators:
            validator.validate( value, history )

    @classmethod
    def build( cls, tool, param ):
        """Factory method to create parameter of correct type"""
        param_type = param.get("type")
        if not param_type or param_type not in parameter_types:
            raise ValueError( "Unknown tool parameter type '%s'" % param_type )
        else:
            return parameter_types[param_type]( tool, param )
        
class TextToolParameter( ToolParameter ):
    """
    Parameter that can take on any text value.
    
    >>> p = TextToolParameter( None, XML( '<param name="blah" type="text" size="4" value="default" />' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <input type="text" name="blah" size="4" value="default">
    >>> print p.get_html( value="meh" )
    <input type="text" name="blah" size="4" value="meh">
    """
    def __init__( self, tool, elem ):
        ToolParameter.__init__( self, tool, elem )
        self.name = elem.get( 'name' )
        self.size = elem.get( 'size' )
        self.value = elem.get( 'value' )
        self.area = string_as_bool( elem.get( 'area', False ) )
    def get_html_field( self, trans=None, value=None, other_values={} ):
        if self.area:
            return form_builder.TextArea( self.name, self.size, value or self.value )
        else:
            return form_builder.TextField( self.name, self.size, value or self.value )
    def get_initial_value( self, trans, context ):
        return self.value

class IntegerToolParameter( TextToolParameter ):
    """
    Parameter that takes an integer value.
    
    >>> p = IntegerToolParameter( None, XML( '<param name="blah" type="integer" size="4" value="10" />' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <input type="text" name="blah" size="4" value="10">
    >>> type( p.from_html( "10" ) )
    <type 'int'>
    >>> type( p.from_html( "bleh" ) )
    Traceback (most recent call last):
        ...
    ValueError: An integer is required
    """
    def __init__( self, tool, elem ):
        TextToolParameter.__init__( self, tool, elem )
        if self.value:
            try:
                int( self.value )
            except:
                raise ValueError( "An integer is required" )
        elif self.value is None:
            raise ValueError( "The settings for this field require a 'value' setting and optionally a default value which must be an integer" )
    def from_html( self, value, trans=None, other_values={} ):
        try: 
            return int( value )
        except: 
            raise ValueError( "An integer is required" )
    def to_python( self, value, app ):
        return int( value )
    def get_initial_value( self, trans, context ):
        if self.value:
            return int( self.value )
        else:
            return 0
            
class FloatToolParameter( TextToolParameter ):
    """
    Parameter that takes a real number value.
    
    >>> p = FloatToolParameter( None, XML( '<param name="blah" type="integer" size="4" value="3.141592" />' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <input type="text" name="blah" size="4" value="3.141592">
    >>> type( p.from_html( "36.1" ) )
    <type 'float'>
    >>> type( p.from_html( "bleh" ) )
    Traceback (most recent call last):
        ...
    ValueError: A real number is required
    """
    def __init__( self, tool, elem ):
        TextToolParameter.__init__( self, tool, elem )
        if self.value:
            try:
                float( self.value )
            except:
                raise ValueError( "A real number is required" )
        elif self.value is None:
            raise ValueError( "The settings for this field require a 'value' setting and optionally a default value which must be a real number" )
    def from_html( self, value, trans=None, other_values={} ):
        try: 
            return float( value )
        except: 
            raise ValueError( "A real number is required" )
    def to_python( self, value, app ):
        return float( value )
    def get_initial_value( self, trans, context ):
        try:
            return float( self.value )
        except:
            return float( 0 )

class BooleanToolParameter( ToolParameter ):
    """
    Parameter that takes one of two values. 
    
    >>> p = BooleanToolParameter( None, XML( '<param name="blah" type="boolean" checked="yes" truevalue="bulletproof vests" falsevalue="cellophane chests" />' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <input type="checkbox" name="blah" value="true" checked><input type="hidden" name="blah" value="true">
    >>> print p.from_html( ["true","true"] )
    True
    >>> print p.to_param_dict_string( True )
    bulletproof vests
    >>> print p.from_html( ["true"] )
    False
    >>> print p.to_param_dict_string( False )
    cellophane chests
    """
    def __init__( self, tool, elem ):
        ToolParameter.__init__( self, tool, elem )
        self.truevalue = elem.get( 'truevalue', 'true' )
        self.falsevalue = elem.get( 'falsevalue', 'false' )
        self.name = elem.get( 'name' )
        self.checked = string_as_bool( elem.get( 'checked' ) )
    def get_html_field( self, trans=None, value=None, other_values={} ):
        checked = self.checked
        if value: 
            checked = form_builder.CheckboxField.is_checked( value )
        return form_builder.CheckboxField( self.name, checked )
    def from_html( self, value, trans=None, other_values={} ):
        return form_builder.CheckboxField.is_checked( value )  
    def to_python( self, value, app ):
        return ( value == 'True' )
    def get_initial_value( self, trans, context ):
        return self.checked
    def to_param_dict_string( self, value, other_values={} ):
        if value:
            return self.truevalue
        else:
            return self.falsevalue

class FileToolParameter( ToolParameter ):
    """
    Parameter that takes an uploaded file as a value.
    
    >>> p = FileToolParameter( None, XML( '<param name="blah" type="file"/>' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <input type="file" name="blah">
    >>> p = FileToolParameter( None, XML( '<param name="blah" type="file" ajax-upload="true"/>' ) )
    >>> print p.get_html()
    <input type="file" name="blah" galaxy-ajax-upload="true">
    """
    def __init__( self, tool, elem ):
        """
        Example: C{<param name="bins" type="file" />}
        """
        ToolParameter.__init__( self, tool, elem )
        self.name = elem.get( 'name' )
        self.ajax = string_as_bool( elem.get( 'ajax-upload' ) )
    def get_html_field( self, trans=None, value=None, other_values={}  ):
        return form_builder.FileField( self.name, ajax = self.ajax, value = value )
    def from_html( self, value, trans=None, other_values={} ):
        # Middleware or proxies may encode files in special ways (TODO: this
        # should be pluggable)
        if type( value ) == dict:
            upload_store = self.tool.app.config.nginx_upload_store
            assert upload_store, \
                "Request appears to have been processed by nginx_upload_module \
                but Galaxy is not configured to recognize it"
            # Check that the file is in the right location
            local_filename = os.path.abspath( value['path'] )
            assert local_filename.startswith( upload_store ), \
                "Filename provided by nginx is not in correct directory"
            value = dict(
                filename = value["name"],
                local_filename = local_filename
            )
        return value
    def get_required_enctype( self ):
        """
        File upload elements require the multipart/form-data encoding
        """
        return "multipart/form-data"
    def to_string( self, value, app ):
        if value in [ None, '' ]:
            return None
        elif isinstance( value, unicode ) or isinstance( value, str ):
            return value
        elif isinstance( value, dict ):
            # or should we jsonify?
            try:
                return value['local_filename']
            except:
                return None
        raise Exception( "FileToolParameter cannot be persisted" )
    def to_python( self, value, app ):
        if value is None:
            return None
        elif isinstance( value, unicode ) or isinstance( value, str ):
            return value
        else:
            raise Exception( "FileToolParameter cannot be persisted" )
    def get_initial_value( self, trans, context ):
        return None
        
class HiddenToolParameter( ToolParameter ):
    """
    Parameter that takes one of two values. 
    
    FIXME: This seems hacky, parameters should only describe things the user
           might change. It is used for 'initializing' the UCSC proxy tool
    
    >>> p = HiddenToolParameter( None, XML( '<param name="blah" type="hidden" value="wax so rockin"/>' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <input type="hidden" name="blah" value="wax so rockin">
    """    
    def __init__( self, tool, elem ):
        ToolParameter.__init__( self, tool, elem )
        self.name = elem.get( 'name' )
        self.value = elem.get( 'value' )
    def get_html_field( self, trans=None, value=None, other_values={} ):
        return form_builder.HiddenField( self.name, self.value )
    def get_initial_value( self, trans, context ):
        return self.value
    def get_label( self ):
        return None
    
## This is clearly a HACK, parameters should only be used for things the user
## can change, there needs to be a different way to specify this. I'm leaving
## it for now to avoid breaking any tools.

class BaseURLToolParameter( ToolParameter ):
    """
    Returns a parameter the contains its value prepended by the 
    current server base url. Used in all redirects.
    """
    def __init__( self, tool, elem ):
        ToolParameter.__init__( self, tool, elem )
        self.name = elem.get( 'name' )
        self.value = elem.get( 'value', '' )
    def get_value( self, trans ):
        # url = trans.request.base + self.value
        url = url_for( self.value, qualified=True )
        return url
    def get_html_field( self, trans=None, value=None, other_values={} ):
        return form_builder.HiddenField( self.name, self.get_value( trans ) )
    def get_initial_value( self, trans, context ):
        return self.value
    def get_label( self ):
        # BaseURLToolParameters are ultimately "hidden" parameters
        return None

class SelectToolParameter( ToolParameter ):
    """
    Parameter that takes on one (or many) or a specific set of values.
    
    >>> p = SelectToolParameter( None, XML( 
    ... '''
    ... <param name="blah" type="select">
    ...     <option value="x">I am X</option>
    ...     <option value="y" selected="true">I am Y</option>
    ...     <option value="z">I am Z</option>
    ... </param>
    ... ''' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <select name="blah" last_selected_value="y">
    <option value="x">I am X</option>
    <option value="y" selected>I am Y</option>
    <option value="z">I am Z</option>
    </select>
    >>> print p.get_html( value="z" )
    <select name="blah" last_selected_value="z">
    <option value="x">I am X</option>
    <option value="y">I am Y</option>
    <option value="z" selected>I am Z</option>
    </select>
    >>> print p.filter_value( "y" )
    y

    >>> p = SelectToolParameter( None, XML( 
    ... '''
    ... <param name="blah" type="select" multiple="true">
    ...     <option value="x">I am X</option>
    ...     <option value="y" selected="true">I am Y</option>
    ...     <option value="z" selected="true">I am Z</option>
    ... </param>
    ... ''' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <select name="blah" multiple last_selected_value="z">
    <option value="x">I am X</option>
    <option value="y" selected>I am Y</option>
    <option value="z" selected>I am Z</option>
    </select>
    >>> print p.get_html( value=["x","y"])
    <select name="blah" multiple last_selected_value="y">
    <option value="x" selected>I am X</option>
    <option value="y" selected>I am Y</option>
    <option value="z">I am Z</option>
    </select>
    >>> print p.to_param_dict_string( ["y", "z"] )
    y,z
    
    >>> p = SelectToolParameter( None, XML( 
    ... '''
    ... <param name="blah" type="select" multiple="true" display="checkboxes">
    ...     <option value="x">I am X</option>
    ...     <option value="y" selected="true">I am Y</option>
    ...     <option value="z" selected="true">I am Z</option>
    ... </param>
    ... ''' ) )
    >>> print p.name
    blah
    >>> print p.get_html()
    <div class="checkUncheckAllPlaceholder" checkbox_name="blah"></div>
    <div><input type="checkbox" name="blah" value="x">I am X</div>
    <div class="odd_row"><input type="checkbox" name="blah" value="y" checked>I am Y</div>
    <div><input type="checkbox" name="blah" value="z" checked>I am Z</div>
    >>> print p.get_html( value=["x","y"])
    <div class="checkUncheckAllPlaceholder" checkbox_name="blah"></div>
    <div><input type="checkbox" name="blah" value="x" checked>I am X</div>
    <div class="odd_row"><input type="checkbox" name="blah" value="y" checked>I am Y</div>
    <div><input type="checkbox" name="blah" value="z">I am Z</div>
    >>> print p.to_param_dict_string( ["y", "z"] )
    y,z
    """
    def __init__( self, tool, elem, context=None ):
        ToolParameter.__init__( self, tool, elem )
        self.multiple = string_as_bool( elem.get( 'multiple', False ) )
        self.display = elem.get( 'display', None )
        self.separator = elem.get( 'separator', ',' )
        self.legal_values = set()
        # TODO: the <dynamic_options> tag is deprecated and should be replaced with the <options> tag.
        self.dynamic_options = elem.get( "dynamic_options", None )
        options = elem.find( 'options' )
        if options is None:
            self.options = None
        else:
            self.options = dynamic_options.DynamicOptions( options, self )
            for validator in self.options.validators:
                self.validators.append( validator )
        if self.dynamic_options is None and self.options is None:
            self.static_options = list()
            for index, option in enumerate( elem.findall( "option" ) ):
                value = option.get( "value" )
                self.legal_values.add( value )
                selected = string_as_bool( option.get( "selected", False ) )
                self.static_options.append( ( option.text, value, selected ) )
        self.is_dynamic = ( ( self.dynamic_options is not None ) or ( self.options is not None ) )
    def get_options( self, trans, other_values ):
        if self.options:
            return self.options.get_options( trans, other_values )
        elif self.dynamic_options:
            return eval( self.dynamic_options, self.tool.code_namespace, other_values )
        else:
            return self.static_options
    def get_legal_values( self, trans, other_values ):
        def _get_UnvalidatedValue_value( value ):
            if isinstance( value, UnvalidatedValue ):
                return value.value
            return value
        if self.options:
            return map( _get_UnvalidatedValue_value, set( v for _, v, _ in self.options.get_options( trans, other_values ) ) )
        elif self.dynamic_options:
            return set( v for _, v, _ in eval( self.dynamic_options, self.tool.code_namespace, other_values ) )
        else:
            return self.legal_values   
    def get_html_field( self, trans=None, value=None, context={} ):
        # Dynamic options are not yet supported in workflow, allow 
        # specifying the value as text for now.
        if self.need_late_validation( trans, context ):
            assert isinstance( value, UnvalidatedValue )
            value = value.value
            if self.multiple:
                if value is None:
                    value = ""
                else:
                    value = "\n".join( value )
                return form_builder.TextArea( self.name, value=value )
            else:
                return form_builder.TextField( self.name, value=(value or "") )
        if value is not None:
            if not isinstance( value, list ): value = [ value ]
        field = form_builder.SelectField( self.name, self.multiple, self.display, self.refresh_on_change, refresh_on_change_values = self.refresh_on_change_values )
        options = self.get_options( trans, context )
        for text, optval, selected in options:
            if isinstance( optval, UnvalidatedValue ):
                optval = optval.value
                text = "%s (unvalidated)" % text
            if value: 
                selected = ( optval in value )
            field.add_option( text, optval, selected )
        return field
    def from_html( self, value, trans=None, context={} ):
        if self.need_late_validation( trans, context ):
            if self.multiple:
                # While it is generally allowed that a select value can be '', 
                # we do not allow this to be the case in a dynamically
                # generated multiple select list being set in workflow building
                # mode we instead treat '' as 'No option Selected' (None)
                if value == '':
                    value = None
                else:
                    value = value.split( "\n" )
            return UnvalidatedValue( value )
        legal_values = self.get_legal_values( trans, context )
        if isinstance( value, list ):
            if not(self.repeat):
                assert self.multiple, "Multiple values provided but parameter is not expecting multiple values"
            rval = []
            for v in value: 
                v = util.restore_text( v )
                if v not in legal_values:
                    raise ValueError( "An invalid option was selected, please verify" )
                rval.append( v )
            return rval
        else:
            value = util.restore_text( value )
            if value not in legal_values:
                raise ValueError( "An invalid option was selected, please verify" )
            return value    
    def to_param_dict_string( self, value, other_values={} ):
        if value is None:
            return "None"
        if isinstance( value, list ):
            if not( self.repeat ):
                assert self.multiple, "Multiple values provided but parameter is not expecting multiple values"
            value = map( str, value )
        else:
            value = str( value )
        if self.tool is None or self.tool.options.sanitize:
            if self.sanitizer:
                value = self.sanitizer.sanitize_param( value )
            else:
                value = sanitize_param( value )
        if isinstance( value, list ):
            value = self.separator.join( value )
        return value
    def value_to_basic( self, value, app ):
        if isinstance( value, UnvalidatedValue ):
            return { "__class__": "UnvalidatedValue", "value": value.value }
        elif isinstance( value, RuntimeValue ):
            # Need to handle runtime value's ourself since delegating to the
            # parent method causes the value to be turned into a string, which
            # breaks multiple selection
            return { "__class__": "RuntimeValue" }
        return value
    def value_from_basic( self, value, app, ignore_errors=False ):
        if isinstance( value, dict ) and value["__class__"] == "UnvalidatedValue":
            return UnvalidatedValue( value["value"] )
        return super( SelectToolParameter, self ).value_from_basic( value, app )
    def need_late_validation( self, trans, context ):
        """
        Determine whether we need to wait to validate this parameters value
        given the current state. For parameters with static options this is
        always false (can always validate immediately). For parameters with
        dynamic options, we need to check whether the other parameters which
        determine what options are valid have been set. For the old style
        dynamic options which do not specify dependencies, this is always true
        (must valiate at runtime).
        """
        # Option list is statically defined, never need late validation
        if not self.is_dynamic:
            return False
        # Old style dynamic options, no dependency information so there isn't
        # a lot we can do: if we're dealing with workflows, have to assume
        # late validation no matter what.
        if self.dynamic_options is not None:
            return ( trans is None or trans.workflow_building_mode )
        # If we got this far, we can actually look at the dependencies
        # to see if their values will not be available until runtime.
        for dep_name in self.get_dependencies():
            dep_value = context[ dep_name ]
            # Dependency on a dataset that does not yet exist
            if isinstance( dep_value, DummyDataset ):
                return True
            # Dependency on a value that has not been checked
            if isinstance( dep_value, UnvalidatedValue ):
                return True
            # Dependency on a value that does not yet exist
            if isinstance( dep_value, RuntimeValue ):
                return True
        # Dynamic, but all dependenceis are known and have values
        return False 
    def get_initial_value( self, trans, context ):
        # More working around dynamic options for workflow
        if self.need_late_validation( trans, context ):
            # Really the best we can do?
            return UnvalidatedValue( None )
        options = list( self.get_options( trans, context ) )
        value = [ optval for _, optval, selected in options if selected ]
        if len( value ) == 0:
            if not self.multiple and options:
                # Nothing selected, but not a multiple select, with some values,
                # so we have to default to something (the HTML form will anyway)
                # TODO: deal with optional parameters in a better way
                value = options[0][1]
            else:
                value = None
        elif len( value ) == 1:
            value = value[0]
        return value
    def value_to_display_text( self, value, app ):
        if isinstance( value, UnvalidatedValue ):
            suffix = "\n(value not yet validated)"
            value = value.value
        else:
            suffix = ""
        if not isinstance( value, list ):
            value = [ value ]
        # FIXME: Currently only translating values back to labels if they
        #        are not dynamic
        if self.is_dynamic:
            rval = map( str, value )
        else:
            options = list( self.static_options )
            rval = []
            for t, v, s in options:
                if v in value:
                    rval.append( t )
        return "\n".join( rval ) + suffix    
    def get_dependencies( self ):
        """
        Get the *names* of the other params this param depends on.
        """
        if self.options:
            return self.options.get_dependency_names()
        else:
            return []

class GenomeBuildParameter( SelectToolParameter ):
    """
    Select list that sets the last used genome build for the current history 
    as "selected".
    
    >>> # Create a mock transcation with 'hg17' as the current build
    >>> from galaxy.util.bunch import Bunch
    >>> trans = Bunch( history=Bunch( genome_build='hg17' ), db_builds=util.dbnames )
    
    >>> p = GenomeBuildParameter( None, XML( 
    ... '''
    ... <param name="blah" type="genomebuild" />
    ... ''' ) )
    >>> print p.name
    blah
    
    >>> # hg17 should be selected by default
    >>> print p.get_html( trans ) # doctest: +ELLIPSIS
    <select name="blah" last_selected_value="hg17">
    <option value="?">unspecified (?)</option>
    ...
    <option value="hg18">Human Mar. 2006 (hg18)</option>
    <option value="hg17" selected>Human May 2004 (hg17)</option>
    ...
    </select>
    
    >>> # If the user selected something else already, that should be used
    >>> # instead
    >>> print p.get_html( trans, value='hg18' ) # doctest: +ELLIPSIS
    <select name="blah" last_selected_value="hg18">
    <option value="?">unspecified (?)</option>
    ...
    <option value="hg18" selected>Human Mar. 2006 (hg18)</option>
    <option value="hg17">Human May 2004 (hg17)</option>
    ...
    </select>
    
    >>> print p.filter_value( "hg17" )
    hg17
    """
    def get_options( self, trans, other_values ):
        last_used_build = trans.history.genome_build
        for dbkey, build_name in trans.db_builds:
            yield build_name, dbkey, ( dbkey == last_used_build )
    def get_legal_values( self, trans, other_values ):
        return set( dbkey for dbkey, _ in trans.db_builds )

class ColumnListParameter( SelectToolParameter ):
    """
    Select list that consists of either the total number of columns or only
    those columns that contain numerical values in the associated DataToolParameter.
    
    # TODO: we need better testing here, but not sure how to associate a DatatoolParameter with a ColumnListParameter
    # from a twill perspective...

    >>> # Mock up a history (not connected to database)
    >>> from galaxy.model import History, HistoryDatasetAssociation
    >>> from galaxy.util.bunch import Bunch
    >>> from galaxy.model.mapping import context as sa_session
    >>> hist = History()
    >>> sa_session.add( hist )
    >>> sa_session.flush()
    >>> hist.add_dataset( HistoryDatasetAssociation( id=1, extension='interval', create_dataset=True, sa_session=sa_session ) )
    >>> dtp =  DataToolParameter( None, XML( '<param name="blah" type="data" format="interval"/>' ) )
    >>> print dtp.name
    blah
    >>> clp = ColumnListParameter ( None, XML( '<param name="numerical_column" type="data_column" data_ref="blah" numerical="true"/>' ) )
    >>> print clp.name
    numerical_column
    """
    def __init__( self, tool, elem ):
        SelectToolParameter.__init__( self, tool, elem )
        self.tool = tool
        self.numerical = string_as_bool( elem.get( "numerical", False ))
        self.force_select = string_as_bool( elem.get( "force_select", True ))
        self.accept_default = string_as_bool( elem.get( "accept_default", False ))
        self.data_ref = elem.get( "data_ref", None )
        self.is_dynamic = True
    def from_html( self, value, trans=None, context={} ):
        """
        Label convention prepends column number with a 'c', but tool uses the integer. This
        removes the 'c' when entered into a workflow.
        """
        if type( value ) == list:
            # We have a multi-select list
            new_value = []
            for item in value:
                if item.startswith( "c" ):
                    item = item[1:]
                new_value.append( item )
            value = new_value
        elif value and value.startswith( "c" ):
            value = value[1:]
        return super( ColumnListParameter, self ).from_html( value, trans, context )
    def get_column_list( self, trans, other_values ):
        """
        Generate a select list containing the columns of the associated 
        dataset (if found).
        """
        column_list = []
        # No value indicates a configuration error, the named DataToolParameter
        # must preceed this parameter in the config
        assert self.data_ref in other_values, "Value for associated DataToolParameter not found"
        # Get the value of the associated DataToolParameter (a dataset)
        dataset = other_values[ self.data_ref ]
        # Check if a dataset is selected
        if dataset is None or dataset == '':
            # NOTE: Both of these values indicate that no dataset is selected.
            #       However, 'None' indicates that the dataset is optional 
            #       while '' indicates that it is not. Currently column
            #       parameters do not work well with optional datasets
            return column_list
        # Generate options
        if not dataset.metadata.columns:
            if self.accept_default:
                column_list.append( '1' )
            return column_list
        if not self.force_select:
            column_list.append( 'None' )
        if self.numerical:
            # If numerical was requsted, filter columns based on metadata
            for i, col in enumerate( dataset.metadata.column_types ):
                if col == 'int' or col == 'float':
                    column_list.append( str( i + 1 ) )
        else:
            for i in range(0, dataset.metadata.columns):
                column_list.append( str( i + 1 ) )
        return column_list
    def get_options( self, trans, other_values ):
        options = []
        column_list = self.get_column_list( trans, other_values )
        if len( column_list ) > 0 and not self.force_select:
            options.append( ('?', 'None', False) )
        for col in column_list:
            if col != 'None':
                options.append( ( 'c' + col, col, False ) )
        return options
    def get_legal_values( self, trans, other_values ):
        return set( self.get_column_list( trans, other_values ) )
    def get_dependencies( self ):
        return [ self.data_ref ]
    def need_late_validation( self, trans, context ):
        if super( ColumnListParameter, self ).need_late_validation( trans, context ):
            return True
        # Get the selected dataset if selected
        dataset = context[ self.data_ref ]
        if dataset:
            # Check if the dataset does not have the expected metadata for columns
            if not dataset.metadata.columns:
                # Only allow late validation if the dataset is not yet ready
                # (since we have reason to expect the metadata to be ready eventually)
                if dataset.is_pending:
                    return True
        # No late validation
        return False
        

class DrillDownSelectToolParameter( SelectToolParameter ):
    """
    Parameter that takes on one (or many) of a specific set of values.
    Creating a hierarchical select menu, which allows users to 'drill down' a tree-like set of options.
    
    >>> p = DrillDownSelectToolParameter( None, XML( 
    ... '''
    ... <param name="some_name" type="drill_down" display="checkbox" hierarchy="recurse" multiple="true">
    ...   <options>
    ...    <option name="Heading 1" value="heading1">
    ...        <option name="Option 1" value="option1"/>
    ...        <option name="Option 2" value="option2"/>
    ...        <option name="Heading 1" value="heading1">
    ...          <option name="Option 3" value="option3"/>
    ...          <option name="Option 4" value="option4"/>
    ...        </option>
    ...    </option>
    ...    <option name="Option 5" value="option5"/>
    ...   </options>
    ... </param>
    ... ''' ) )
    >>> print p.get_html()
    <div><ul class="toolParameterExpandableCollapsable">
    <li><span class="toolParameterExpandableCollapsable">[+]</span><input type="checkbox" name="some_name" value="heading1"">Heading 1
    <ul class="toolParameterExpandableCollapsable" default_state="collapsed">
    <li><input type="checkbox" name="some_name" value="option1"">Option 1
    </li>
    <li><input type="checkbox" name="some_name" value="option2"">Option 2
    </li>
    <li><span class="toolParameterExpandableCollapsable">[+]</span><input type="checkbox" name="some_name" value="heading1"">Heading 1
    <ul class="toolParameterExpandableCollapsable" default_state="collapsed">
    <li><input type="checkbox" name="some_name" value="option3"">Option 3
    </li>
    <li><input type="checkbox" name="some_name" value="option4"">Option 4
    </li>
    </ul>
    </li>
    </ul>
    </li>
    <li><input type="checkbox" name="some_name" value="option5"">Option 5
    </li>
    </ul></div>
    >>> p = DrillDownSelectToolParameter( None, XML( 
    ... '''
    ... <param name="some_name" type="drill_down" display="radio" hierarchy="recurse" multiple="false">
    ...   <options>
    ...    <option name="Heading 1" value="heading1">
    ...        <option name="Option 1" value="option1"/>
    ...        <option name="Option 2" value="option2"/>
    ...        <option name="Heading 1" value="heading1">
    ...          <option name="Option 3" value="option3"/>
    ...          <option name="Option 4" value="option4"/>
    ...        </option>
    ...    </option>
    ...    <option name="Option 5" value="option5"/>
    ...   </options>
    ... </param>
    ... ''' ) )
    >>> print p.get_html()
    <div><ul class="toolParameterExpandableCollapsable">
    <li><span class="toolParameterExpandableCollapsable">[+]</span><input type="radio" name="some_name" value="heading1"">Heading 1
    <ul class="toolParameterExpandableCollapsable" default_state="collapsed">
    <li><input type="radio" name="some_name" value="option1"">Option 1
    </li>
    <li><input type="radio" name="some_name" value="option2"">Option 2
    </li>
    <li><span class="toolParameterExpandableCollapsable">[+]</span><input type="radio" name="some_name" value="heading1"">Heading 1
    <ul class="toolParameterExpandableCollapsable" default_state="collapsed">
    <li><input type="radio" name="some_name" value="option3"">Option 3
    </li>
    <li><input type="radio" name="some_name" value="option4"">Option 4
    </li>
    </ul>
    </li>
    </ul>
    </li>
    <li><input type="radio" name="some_name" value="option5"">Option 5
    </li>
    </ul></div>
    >>> print p.options
    [{'selected': False, 'name': 'Heading 1', 'value': 'heading1', 'options': [{'selected': False, 'name': 'Option 1', 'value': 'option1', 'options': []}, {'selected': False, 'name': 'Option 2', 'value': 'option2', 'options': []}, {'selected': False, 'name': 'Heading 1', 'value': 'heading1', 'options': [{'selected': False, 'name': 'Option 3', 'value': 'option3', 'options': []}, {'selected': False, 'name': 'Option 4', 'value': 'option4', 'options': []}]}]}, {'selected': False, 'name': 'Option 5', 'value': 'option5', 'options': []}]
    """
    def __init__( self, tool, elem, context=None ):
        def recurse_option_elems( cur_options, option_elems ):
            for option_elem in option_elems:
                selected = string_as_bool( option_elem.get( 'selected', False ) )
                cur_options.append( { 'name':option_elem.get( 'name' ), 'value': option_elem.get( 'value'), 'options':[], 'selected':selected  } )
                recurse_option_elems( cur_options[-1]['options'], option_elem.findall( 'option' ) )
        ToolParameter.__init__( self, tool, elem )
        self.multiple = string_as_bool( elem.get( 'multiple', False ) )
        self.display = elem.get( 'display', None )
        self.hierarchy = elem.get( 'hierarchy', 'exact' ) #exact or recurse
        self.separator = elem.get( 'separator', ',' )
        from_file = elem.get( 'from_file', None )
        if from_file:
            if not os.path.isabs( from_file ):
                from_file = os.path.join( tool.app.config.tool_data_path, from_file )
            elem = XML( "<root>%s</root>" % open( from_file ).read() )
        self.is_dynamic = False
        self.dynamic_options = None #backwards compatibility with SelectToolParameter's old dynamic options and late validation
        self.options = []
        self.filtered = {}
        if elem.find( 'filter' ):
            self.is_dynamic = True
            for filter in elem.findall( 'filter' ):
                #currently only filtering by metadata key matching input file is allowed
                if filter.get( 'type' ) == 'data_meta':
                    if filter.get( 'data_ref' ) not in self.filtered:
                        self.filtered[filter.get( 'data_ref' )] = {}
                    self.filtered[filter.get( 'data_ref' )][filter.get( 'meta_key' )] = { 'value': filter.get( 'value' ), 'options':[] }
                    recurse_option_elems( self.filtered[filter.get( 'data_ref' )][filter.get( 'meta_key' )]['options'], filter.find( 'options' ).findall( 'option' ) )
        else:
            recurse_option_elems( self.options, elem.find( 'options' ).findall( 'option' ) )
    
    def get_options( self, trans=None, value=None, other_values={} ):
        if self.is_dynamic:
            options = []
            for filter_key, filter_value in self.filtered.iteritems():
                dataset = other_values[filter_key]
                if dataset.__class__.__name__.endswith( "DatasetFilenameWrapper" ): #this is a bad way to check for this, but problems importing class ( due to circular imports? )
                    dataset = dataset.dataset
                if dataset:
                    for meta_key, meta_dict in filter_value.iteritems():
                        if dataset.metadata.spec[meta_key].param.to_string( dataset.metadata.get( meta_key ) ) == meta_dict['value']:
                            options.extend( meta_dict['options'] )
            return options
        return self.options
    
    def get_legal_values( self, trans, other_values ):
        def recurse_options( legal_values, options ):
            for option in options:
                legal_values.append( option['value'] )
                recurse_options( legal_values, option['options'] )
        legal_values = []
        recurse_options( legal_values, self.get_options( trans=trans, other_values=other_values ) )
        return legal_values
    
    def get_html( self, trans=None, value=None, other_values={} ):
        """
        Returns the html widget corresponding to the paramter. 
        Optionally attempt to retain the current value specific by 'value'
        """        
        return self.get_html_field( trans, value, other_values ).get_html()
                
    def get_html_field( self, trans=None, value=None, other_values={} ):
        # Dynamic options are not yet supported in workflow, allow 
        # specifying the value as text for now.
        if self.need_late_validation( trans, other_values ):
            if value is not None:
                assert isinstance( value, UnvalidatedValue )
                value = value.value
            if self.multiple:
                if value is None:
                    value = ""
                else:
                    value = "\n".join( value )
                return form_builder.TextArea( self.name, value=value )
            else:
                return form_builder.TextField( self.name, value=(value or "") )
        return form_builder.DrillDownField( self.name, self.multiple, self.display, self.refresh_on_change, self.get_options( trans, value, other_values ), value, refresh_on_change_values = self.refresh_on_change_values )
    
    def from_html( self, value, trans=None, other_values={} ):
        if self.need_late_validation( trans, other_values ):
            if self.multiple:
                if value == '': #No option selected
                    value = None
                else:
                    value = value.split( "\n" )
            return UnvalidatedValue( value )
        if not value: return None
        if not isinstance( value, list ):
            value = [value]
        if not( self.repeat ) and len( value ) > 1:
            assert self.multiple, "Multiple values provided but parameter is not expecting multiple values"
        rval = []
        for val in value:
            if val not in self.get_legal_values( trans, other_values ): raise ValueError( "An invalid option was selected, please verify" )
            rval.append( util.restore_text( val ) )
        return rval
    
    def to_param_dict_string( self, value, other_values={} ):
        def get_options_list( value ):
            def get_base_option( value, options ):
                for option in options:
                    if value == option['value']:
                        return option
                    rval = get_base_option( value, option['options'] )
                    if rval: return rval
                return None #not found
            def recurse_option( option_list, option ):
                if not option['options']:
                    option_list.append( option['value'] )
                else:
                    for opt in option['options']:
                        recurse_option( option_list, opt )
            rval = []
            recurse_option( rval, get_base_option( value, self.get_options( other_values = other_values ) ) )
            return rval or [value]
        
        if value is None: return "None"
        rval = []
        if self.hierarchy == "exact":
            rval = value
        else:
            for val in value:
                options = get_options_list( val )
                rval.extend( options )
        if len( rval ) > 1:
            if not( self.repeat ):
                assert self.multiple, "Multiple values provided but parameter is not expecting multiple values"
        rval = self.separator.join( rval )
        if self.tool is None or self.tool.options.sanitize:
            if self.sanitizer:
                rval = self.sanitizer.sanitize_param( rval )
            else:
                rval = sanitize_param( rval )
        return rval
    
    def get_initial_value( self, trans, context ):
        def recurse_options( initial_values, options ):
            for option in options:
                if option['selected']:
                    initial_values.append( option['value'] )
                recurse_options( initial_values, option['options'] )
        # More working around dynamic options for workflow
        if self.need_late_validation( trans, context ):
            # Really the best we can do?
            return UnvalidatedValue( None )
        initial_values = []
        recurse_options( initial_values, self.get_options( trans=trans, other_values=context ) )
        return initial_values

    def value_to_display_text( self, value, app ):
        def get_option_display( value, options ):
            for option in options:
                if value == option['value']:
                    return option['name']
                rval = get_option_display( value, option['options'] )
                if rval: return rval
            return None #not found
        
        if isinstance( value, UnvalidatedValue ):
            suffix = "\n(value not yet validated)"
            value = value.value
        else:
            suffix = ""
        if not value:
            value = []
        elif not isinstance( value, list ):
            value = [ value ]
        # FIXME: Currently only translating values back to labels if they
        #        are not dynamic
        if self.is_dynamic:
            if value:
                if isinstance( value, list ):
                    rval = value
                else:
                    rval = [ value ]
            else:
                rval = []
        else:
            rval = []
            for val in value:
                rval.append( get_option_display( val, self.options ) or val )
        return "\n".join( rval ) + suffix
        
    def get_dependencies( self ):
        """
        Get the *names* of the other params this param depends on.
        """
        return self.filtered.keys()

class DummyDataset( object ):
    pass

class DataToolParameter( ToolParameter ):
    # TODO, Nate: Make sure the following unit tests appropriately test the dataset security
    # components.  Add as many additional tests as necessary.
    """
    Parameter that takes on one (or many) or a specific set of values.

    TODO: There should be an alternate display that allows single selects to be 
          displayed as radio buttons and multiple selects as a set of checkboxes

    TODO: The following must be fixed to test correctly for the new security_check tag in the DataToolParameter ( the last test below is broken )
    Nate's next passs at the dataset security stuff will dramatically alter this anyway.
    """

    def __init__( self, tool, elem ):
        ToolParameter.__init__( self, tool, elem )
        # Add metadata validator
        if not string_as_bool( elem.get( 'no_validation', False ) ):
            self.validators.append( validation.MetadataValidator() )
        # Build tuple of classes for supported data formats
        formats = []
        self.extensions = elem.get( 'format', 'data' ).split( "," )
        for extension in self.extensions:
            extension = extension.strip()
            if tool is None:
                #This occurs for things such as unit tests
                import galaxy.datatypes.registry
                formats.append( galaxy.datatypes.registry.Registry().get_datatype_by_extension( extension.lower() ).__class__ )
            else:
                formats.append( tool.app.datatypes_registry.get_datatype_by_extension( extension.lower() ).__class__ )
        self.formats = tuple( formats )
        self.multiple = string_as_bool( elem.get( 'multiple', False ) )
        # Optional DataToolParameters are used in tools like GMAJ and LAJ
        self.optional = string_as_bool( elem.get( 'optional', False ) )
        # TODO: Enhance dynamic options for DataToolParameters. Currently,
        #       only the special case key='build' of type='data_meta' is
        #       a valid filter
        options = elem.find( 'options' )
        if options is None:
            self.options = None
        else:
            self.options = dynamic_options.DynamicOptions( options, self )
        self.is_dynamic = self.options is not None

    def get_html_field( self, trans=None, value=None, other_values={} ):
        filter_value = None
        if self.options:
            try:
                filter_value = self.options.get_options( trans, other_values )[0][0]
            except IndexError:
                pass #no valid options
        assert trans is not None, "DataToolParameter requires a trans"
        history = trans.get_history()
        assert history is not None, "DataToolParameter requires a history"
        if value is not None:
            if type( value ) != list:
                value = [ value ]
        field = form_builder.SelectField( self.name, self.multiple, None, self.refresh_on_change, refresh_on_change_values = self.refresh_on_change_values )
        # CRUCIAL: the dataset_collector function needs to be local to DataToolParameter.get_html_field()
        def dataset_collector( hdas, parent_hid ):
            user, roles = trans.get_user_and_roles()
            for i, hda in enumerate( hdas ):
                if len( hda.name ) > 30:
                    hda_name = '%s..%s' % ( hda.name[:17], hda.name[-11:] )
                else:
                    hda_name = hda.name
                if parent_hid is not None:
                    hid = "%s.%d" % ( parent_hid, i + 1 )
                else:
                    hid = str( hda.hid )
                if not hda.dataset.state in [galaxy.model.Dataset.states.ERROR, galaxy.model.Dataset.states.DISCARDED] and \
                    hda.visible and \
                    trans.app.security_agent.can_access_dataset( roles, hda.dataset ):
                    # If we are sending data to an external application, then we need to make sure there are no roles
                    # associated with the dataset that restrict it's access from "public".
                    if self.tool and self.tool.tool_type == 'data_destination' and not trans.app.security_agent.dataset_is_public( hda.dataset ):
                        continue
                    if self.options and hda.get_dbkey() != filter_value:
                        continue
                    if isinstance( hda.datatype, self.formats):
                        selected = ( value and ( hda in value ) )
                        field.add_option( "%s: %s" % ( hid, hda_name ), hda.id, selected )
                    else:
                        target_ext, converted_dataset = hda.find_conversion_destination( self.formats, converter_safe = self.converter_safe( other_values, trans ) )
                        if target_ext:
                            if converted_dataset:
                                hda = converted_dataset
                            if not trans.app.security_agent.can_access_dataset( roles, hda.dataset ):
                                continue
                            selected = ( value and ( hda in value ) )
                            field.add_option( "%s: (as %s) %s" % ( hid, target_ext, hda_name ), hda.id, selected )
                # Also collect children via association object
                dataset_collector( hda.children, hid )
        dataset_collector( history.active_datasets, None )
        some_data = bool( field.options )
        if some_data:
            if value is None or len( field.options ) == 1:
                # Ensure that the last item is always selected
                a, b, c = field.options[-1]
                if self.optional:
                    field.options[-1] = a, b, False
                else:
                    field.options[-1] = a, b, True
        if self.optional:
            if not value:
                field.add_option( "Selection is Optional", 'None', True )
            else:
                field.add_option( "Selection is Optional", 'None', False )
        return field

    def get_initial_value( self, trans, context ):
        """
        NOTE: This is wasteful since dynamic options and dataset collection
              happens twice (here and when generating HTML). 
        """
        # Can't look at history in workflow mode
        if trans.workflow_building_mode:
            return DummyDataset()
        assert trans is not None, "DataToolParameter requires a trans"
        history = trans.get_history()
        assert history is not None, "DataToolParameter requires a history"
        if self.optional:
            return None
        most_recent_dataset = [None]
        filter_value = None
        if self.options:
            try:
                filter_value = self.options.get_options( trans, context )[0][0]
            except IndexError:
                pass #no valid options
        def dataset_collector( datasets ):
            def is_convertable( dataset ):
                target_ext, converted_dataset = dataset.find_conversion_destination( self.formats, converter_safe = self.converter_safe( None, trans ) )
                if target_ext is not None:
                    return True
                return False
            for i, data in enumerate( datasets ):
                if data.visible and not data.deleted and data.state not in [data.states.ERROR, data.states.DISCARDED] and ( isinstance( data.datatype, self.formats) or is_convertable( data ) ):
                    if self.options and data.get_dbkey() != filter_value:
                        continue
                    most_recent_dataset[0] = data
                # Also collect children via association object
                dataset_collector( data.children )
        dataset_collector( history.datasets )
        most_recent_dataset = most_recent_dataset.pop()
        if most_recent_dataset is not None:
            return most_recent_dataset
        else:
            return ''

    def from_html( self, value, trans, other_values={} ):
        # Can't look at history in workflow mode, skip validation and such,
        # although, this should never be called in workflow mode right?
        if trans.workflow_building_mode:
            return None
        if not value:
            raise ValueError( "History does not include a dataset of the required format / build" ) 
        if value in [None, "None"]:
            return None
        if isinstance( value, list ):
            return [ trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( v ) for v in value ]
        elif isinstance( value, trans.app.model.HistoryDatasetAssociation ):
            return value
        else:
            return trans.sa_session.query( trans.app.model.HistoryDatasetAssociation ).get( value )

    def to_string( self, value, app ):
        if value is None or isinstance( value, str ):
            return value
        elif isinstance( value, DummyDataset ):
            return None
        return value.id

    def to_python( self, value, app ):
        # Both of these values indicate that no dataset is selected.  However, 'None' 
        # indicates that the dataset is optional, while '' indicates that it is not.
        if value is None or value == '' or value == 'None':
            return value
        return app.model.context.query( app.model.HistoryDatasetAssociation ).get( int( value ) )

    def to_param_dict_string( self, value, other_values={} ):
        if value is None: return "None"
        return value.file_name
        
    def value_to_display_text( self, value, app ):
        if value:
            return "%s: %s" % ( value.hid, value.name )
        else:
            return "No dataset"

    def get_dependencies( self ):
        """
        Get the *names* of the other params this param depends on.
        """
        if self.options:
            return self.options.get_dependency_names()
        else:
            return []

    def converter_safe( self, other_values, trans ):
        if self.tool is None or self.tool.has_multiple_pages or not hasattr( trans, 'workflow_building_mode' ) or trans.workflow_building_mode:
            return False
        if other_values is None:
            return True # we don't know other values, so we can't check, assume ok
        converter_safe = [True]
        def visitor( prefix, input, value, parent = None ):
            if isinstance( input, SelectToolParameter ) and self.name in input.get_dependencies():
                if input.is_dynamic and ( input.dynamic_options or ( not input.dynamic_options and not input.options ) or not input.options.converter_safe ):
                    converter_safe[0] = False #This option does not allow for conversion, i.e. uses contents of dataset file to generate options
        self.tool.visit_inputs( other_values, visitor )
        return False not in converter_safe

# class RawToolParameter( ToolParameter ):
#     """
#     Completely nondescript parameter, HTML representation is provided as text
#     contents. 
#     
#     >>> p = RawToolParameter( None, XML( 
#     ... '''
#     ... <param name="blah" type="raw">
#     ... <![CDATA[<span id="$name">Some random stuff</span>]]>
#     ... </param>
#     ... ''' ) )
#     >>> print p.name
#     blah
#     >>> print p.get_html().strip()
#     <span id="blah">Some random stuff</span>
#     """
#     def __init__( self, tool, elem ):
#         ToolParameter.__init__( self, tool, elem )
#         self.template = string.Template( elem.text )
#     def get_html( self, prefix="" ):
#         context = dict( self.__dict__ )
#         context.update( dict( prefix=prefix ) )
#         return self.template.substitute( context )
        
# class HistoryIDParameter( ToolParameter ):
#     """
#     Parameter that takes a name value, makes history.id available. 
#     
#     FIXME: This is a hack (esp. if hidden params are a hack) but in order to
#            have the history accessable at the job level, it is necessary
#            I also probably wrote this docstring test thing wrong.
#     
#     >>> from galaxy.model import History
#     >>> from galaxy.util.bunch import Bunch
#     >>> hist = History( id=1 )
#     >>> p = HistoryIDParameter( None, XML( '<param name="blah" type="history"/>' ) )
#     >>> print p.name
#     blah
#     >>> html_string = '<input type="hidden" name="blah" value="%d">' % hist.id
#     >>> assert p.get_html( trans=Bunch( history=hist ) ) == html_string
#     """  
#     def __init__( self, tool, elem ):
#         ToolParameter.__init__( self, tool, elem )
#         self.name = elem.get('name')
#     def get_html( self, trans, value=None, other_values={} ):
#         assert trans.history is not None, "HistoryIDParameter requires a history"
#         self.html = form_builder.HiddenField( self.name, trans.history.id ).get_html()
#         return self.html

parameter_types = dict( text        = TextToolParameter,
                        integer     = IntegerToolParameter,
                        float       = FloatToolParameter,
                        boolean     = BooleanToolParameter,
                        genomebuild = GenomeBuildParameter,
                        select      = SelectToolParameter,
                        data_column = ColumnListParameter,
                        hidden      = HiddenToolParameter,
                        baseurl     = BaseURLToolParameter,
                        file        = FileToolParameter,
                        data        = DataToolParameter,
                        drill_down = DrillDownSelectToolParameter )

class UnvalidatedValue( object ):
    """
    Wrapper to mark a value that has not been validated
    """
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return str( self.value )
        
class RuntimeValue( object ):
    """
    Wrapper to note a value that is not yet set, but will be required at
    runtime.
    """
    pass

