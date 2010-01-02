"""
Classes related to parameter validation.
"""

import os, re, logging
from elementtree.ElementTree import XML
from galaxy import model

log = logging.getLogger( __name__ )

class LateValidationError( Exception ):
    def __init__( self, message ):
        self.message = message

class Validator( object ):
    """
    A validator checks that a value meets some conditions OR raises ValueError
    """
    @classmethod
    def from_element( cls, param, elem ):
        type = elem.get( 'type', None )
        assert type is not None, "Required 'type' attribute missing from validator"
        return validator_types[type].from_element( param, elem )
    def validate( self, value, history=None ):
        raise TypeError( "Abstract Method" )
        
class RegexValidator( Validator ):
    """
    Validator that evaluates a regular expression
    
    >>> from galaxy.tools.parameters import ToolParameter
    >>> p = ToolParameter.build( None, XML( '''
    ... <param name="blah" type="text" size="10" value="10">
    ...     <validator type="regex" message="Not gonna happen">[Ff]oo</validator>
    ... </param>
    ... ''' ) )
    >>> t = p.validate( "Foo" )
    >>> t = p.validate( "foo" )
    >>> t = p.validate( "Fop" )
    Traceback (most recent call last):
        ...
    ValueError: Not gonna happen
    """
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message' ), elem.text )
    def __init__( self, message, expression ):
        self.message = message
        # Compile later. RE objects used to not be thread safe. Not sure about
        # the sre module. 
        self.expression = expression  
    def validate( self, value, history=None ):
        if re.match( self.expression, value ) is None:
            raise ValueError( self.message )
        
class ExpressionValidator( Validator ):
    """
    Validator that evaluates a python expression using the value
    
    >>> from galaxy.tools.parameters import ToolParameter
    >>> p = ToolParameter.build( None, XML( '''
    ... <param name="blah" type="text" size="10" value="10">
    ...     <validator type="expression" message="Not gonna happen">value.lower() == "foo"</validator>
    ... </param>
    ... ''' ) )
    >>> t = p.validate( "Foo" )
    >>> t = p.validate( "foo" )
    >>> t = p.validate( "Fop" )
    Traceback (most recent call last):
        ...
    ValueError: Not gonna happen
    """
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message' ), elem.text, elem.get( 'substitute_value_in_message' ) )
    def __init__( self, message, expression, substitute_value_in_message ):
        self.message = message
        self.substitute_value_in_message = substitute_value_in_message
        # Save compiled expression, code objects are thread safe (right?)
        self.expression = compile( expression, '<string>', 'eval' )
    def validate( self, value, history=None ):
        if not( eval( self.expression, dict( value=value ) ) ):
            message = self.message
            if self.substitute_value_in_message:
                message = message % value
            raise ValueError( message )
        
class InRangeValidator( Validator ):
    """
    Validator that ensures a number is in a specific range
    
    >>> from galaxy.tools.parameters import ToolParameter
    >>> p = ToolParameter.build( None, XML( '''
    ... <param name="blah" type="integer" size="10" value="10">
    ...     <validator type="in_range" message="Not gonna happen" min="10" max="20"/>
    ... </param>
    ... ''' ) )
    >>> t = p.validate( 10 )
    >>> t = p.validate( 15 )
    >>> t = p.validate( 20 )
    >>> t = p.validate( 21 )
    Traceback (most recent call last):
        ...
    ValueError: Not gonna happen
    """
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message', None ), elem.get( 'min' ), elem.get( 'max' ) )
    def __init__( self, message, range_min, range_max ):
        self.message = message or ( "Value must be between %f and %f" % ( range_min, range_max ) )
        self.min = float( range_min )
        self.max = float( range_max )    
    def validate( self, value, history=None ):
        if not( self.min <= float( value ) <= self.max ):
            raise ValueError( self.message )   
        
class LengthValidator( Validator ):
    """
    Validator that ensures a number is in a specific range

    >>> from galaxy.tools.parameters import ToolParameter
    >>> p = ToolParameter.build( None, XML( '''
    ... <param name="blah" type="text" size="10" value="foobar">
    ...     <validator type="length" min="2" max="8"/>
    ... </param>
    ... ''' ) )
    >>> t = p.validate( "foo" )
    >>> t = p.validate( "bar" )
    >>> t = p.validate( "f" )
    Traceback (most recent call last):
        ...
    ValueError: Must have length of at least 2
    >>> t = p.validate( "foobarbaz" )
    Traceback (most recent call last):
        ...
    ValueError: Must have length no more than 8
    """
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message', None ), elem.get( 'min', None ), elem.get( 'max', None ) )
    def __init__( self, message, length_min, length_max ):
        self.message = message
        if length_min is not None: 
            length_min = int( length_min )
        if length_max is not None:
            length_max = int( length_max )
        self.min = length_min
        self.max = length_max
    def validate( self, value, history=None ):
        if self.min is not None and len( value ) < self.min:
            raise ValueError( self.message or ( "Must have length of at least %d" % self.min ) )
        if self.max is not None and len( value ) > self.max:
            raise ValueError( self.message or ( "Must have length no more than %d" % self.max ) )

class DatasetOkValidator( Validator ):
    """
    Validator that checks if a dataset is in an 'ok' state
    """
    def __init__( self, message=None ):
        self.message = message
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message', None ) )
    def validate( self, value, history=None ):
        if value and value.state != model.Dataset.states.OK:
            if self.message is None:
                self.message = "The selected dataset is still being generated, select another dataset or wait until it is completed"
            raise ValueError( self.message )

class MetadataValidator( Validator ):
    """
    Validator that checks for missing metadata
    """
    def __init__( self, message = None, check = "", skip = "" ):
        self.message = message
        self.check = check.split( "," )
        self.skip = skip.split( "," )
    @classmethod
    def from_element( cls, param, elem ):
        return cls( message=elem.get( 'message', None ), check=elem.get( 'check', "" ), skip=elem.get( 'skip', "" ) )
    def validate( self, value, history=None ):
        if value and value.missing_meta( check = self.check, skip = self.skip ):
            if self.message is None:
                self.message = "Metadata missing, click the pencil icon in the history item to edit / save the metadata attributes"
            raise ValueError( self.message )

class UnspecifiedBuildValidator( Validator ):
    """
    Validator that checks for missing metadata
    """
    def __init__( self, message=None ):
        if message is None:
            self.message = "Unspecified genome build, click the pencil icon in the history item to set the genome build"
        else:
            self.message = message
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message', None ) )
    def validate( self, value, history=None ):
        #if value is None, we cannot validate
        if value:
            dbkey = value.metadata.dbkey
            if isinstance( dbkey, list ):
                dbkey = dbkey[0]
            if dbkey == '?':
                raise ValueError( self.message )

class NoOptionsValidator( Validator ):
    """Validator that checks for empty select list"""
    def __init__( self, message=None ):
        self.message = message
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message', None ) )
    def validate( self, value, history=None ):
        if value is None:
            if self.message is None:
                self.message = "No options available for selection"
            raise ValueError( self.message )

class EmptyTextfieldValidator( Validator ):
    """Validator that checks for empty text field"""
    def __init__( self, message=None ):
        self.message = message
    @classmethod
    def from_element( cls, param, elem ):
        return cls( elem.get( 'message', None ) )
    def validate( self, value, history=None ):
        if value == '':
            if self.message is None:
                self.message = "Field requires a value"
            raise ValueError( self.message )

class MetadataInFileColumnValidator( Validator ):
    """
    Validator that checks if the value for a dataset's metadata item exists in a file.
    """
    @classmethod
    def from_element( cls, param, elem ):
        filename = elem.get( "filename", None )
        if filename:
            filename = "%s/%s" % ( param.tool.app.config.tool_data_path, filename.strip() )
        metadata_name = elem.get( "metadata_name", None )
        if metadata_name:
            metadata_name = metadata_name.strip()
        metadata_column = int( elem.get( "metadata_column", 0 ) )
        message = elem.get( "message", "Value for metadata %s was not found in %s." % ( metadata_name, filename ) )
        line_startswith = elem.get( "line_startswith", None  )
        if line_startswith:
            line_startswith = line_startswith.strip()
        return cls( filename, metadata_name, metadata_column, message, line_startswith )
    def __init__( self, filename, metadata_name, metadata_column, message="Value for metadata not found.", line_startswith=None ):
        self.metadata_name = metadata_name
        self.message = message
        self.valid_values = []
        for line in open( filename ):
            if line_startswith is None or line.startswith( line_startswith ):
                fields = line.split( '\t' )
                if metadata_column < len( fields ):
                    self.valid_values.append( fields[metadata_column].strip() )
    def validate( self, value, history = None ):
        if not value: return
        if hasattr( value, "metadata" ):
            if value.metadata.spec[self.metadata_name].param.to_string( value.metadata.get( self.metadata_name ) ) in self.valid_values:
                return
        raise ValueError( self.message )

validator_types = dict( expression=ExpressionValidator,
                        regex=RegexValidator,
                        in_range=InRangeValidator,
                        length=LengthValidator,
                        metadata=MetadataValidator,
                        unspecified_build=UnspecifiedBuildValidator,
                        no_options=NoOptionsValidator,
                        empty_field=EmptyTextfieldValidator,
                        dataset_metadata_in_file=MetadataInFileColumnValidator,
                        dataset_ok_validator=DatasetOkValidator )
                        
def get_suite():
    """Get unittest suite for this module"""
    import doctest, sys
    return doctest.DocTestSuite( sys.modules[__name__] )

