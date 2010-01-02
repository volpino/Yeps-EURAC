"""
Tabular datatype

"""
import pkg_resources
pkg_resources.require( "bx-python" )

import logging
import data
from galaxy import util
from cgi import escape
from galaxy.datatypes import metadata
from galaxy.datatypes.metadata import MetadataElement
from sniff import *

log = logging.getLogger(__name__)

class Tabular( data.Text ):
    """Tab delimited data"""

    """Add metadata elements"""
    MetadataElement( name="comment_lines", default=0, desc="Number of comment lines", readonly=False, optional=True, no_value=0 )
    MetadataElement( name="columns", default=0, desc="Number of columns", readonly=True, visible=False, no_value=0 )
    MetadataElement( name="column_types", default=[], desc="Column types", param=metadata.ColumnTypesParameter, readonly=True, visible=False, no_value=[] )

    def init_meta( self, dataset, copy_from=None ):
        data.Text.init_meta( self, dataset, copy_from=copy_from )
    def set_meta( self, dataset, overwrite = True, skip = None, **kwd ):
        """
        Tries to determine the number of columns as well as those columns
        that contain numerical values in the dataset.  A skip parameter is
        used because various tabular data types reuse this function, and
        their data type classes are responsible to determine how many invalid
        comment lines should be skipped. Using None for skip will cause skip 
        to be zero, but the first line will be processed as a header.

        Items of interest:
        1. We treat 'overwrite' as always True (we always want to set tabular metadata when called).
        2. If a tabular file has no data, it will have one column of type 'str'.
        3. We used to check only the first 100 lines when setting metadata and this class's
           set_peek() method read the entire file to determine the number of lines in the file.
           Since metadata can now be processed on cluster nodes, we've merged the line count portion
           of the set_peek() processing here, and we now check the entire contents of the file.
        """
        # Store original skip value to check with later
        requested_skip = skip
        if skip is None:
            skip = 0
        column_type_set_order = [ 'int', 'float', 'list', 'str'  ] #Order to set column types in
        default_column_type = column_type_set_order[-1] # Default column type is lowest in list
        column_type_compare_order = list( column_type_set_order ) #Order to compare column types
        column_type_compare_order.reverse() 
        def type_overrules_type( column_type1, column_type2 ):
            if column_type1 is None or column_type1 == column_type2:
                return False
            if column_type2 is None:
                return True
            for column_type in column_type_compare_order:
                if column_type1 == column_type:
                    return True
                if column_type2 == column_type:
                    return False
            #neither column type was found in our ordered list, this cannot happen
            raise "Tried to compare unknown column types"
        def is_int( column_text ):
            try:
                int( column_text )
                return True
            except: 
                return False
        def is_float( column_text ):
            try:
                float( column_text )
                return True
            except: 
                if column_text.strip().lower() == 'na':
                    return True #na is special cased to be a float
                return False
        def is_list( column_text ):
            return "," in column_text
        def is_str( column_text ):
            #anything, except an empty string, is True
            if column_text == "":
                return False
            return True
        is_column_type = {} #Dict to store column type string to checking function
        for column_type in column_type_set_order:
            is_column_type[column_type] = locals()[ "is_%s" % ( column_type ) ]
        def guess_column_type( column_text ):
            for column_type in column_type_set_order:
                if is_column_type[column_type]( column_text ):
                    return column_type
            return None
        data_lines = 0
        comment_lines = 0
        column_types = []
        first_line_column_types = [default_column_type] # default value is one column of type str
        if dataset.has_data():
            #NOTE: if skip > num_check_lines, we won't detect any metadata, and will use default
            for i, line in enumerate( file ( dataset.file_name ) ):
                line = line.rstrip( '\r\n' )
                if i < skip or not line or line.startswith( '#' ):
                    # We'll call blank lines comments
                    comment_lines += 1
                else:
                    data_lines += 1
                    fields = line.split( '\t' )
                    for field_count, field in enumerate( fields ):
                        if field_count >= len( column_types ): #found a previously unknown column, we append None
                            column_types.append( None )
                        column_type = guess_column_type( field )
                        if type_overrules_type( column_type, column_types[field_count] ):
                            column_types[field_count] = column_type
                    if i == 0 and requested_skip is None:
                        # This is our first line, people seem to like to upload files that have a header line, but do not 
                        # start with '#' (i.e. all column types would then most likely be detected as str).  We will assume
                        # that the first line is always a header (this was previous behavior - it was always skipped).  When
                        # the requested skip is None, we only use the data from the first line if we have no other data for
                        # a column.  This is far from perfect, as
                        # 1,2,3	1.1	2.2	qwerty
                        # 0	0		1,2,3
                        # will be detected as
                        # "column_types": ["int", "int", "float", "list"]
                        # instead of
                        # "column_types": ["list", "float", "float", "str"]  *** would seem to be the 'Truth' by manual
                        # observation that the first line should be included as data.  The old method would have detected as
                        # "column_types": ["int", "int", "str", "list"]
                        first_line_column_types = column_types
                        column_types = [ None for col in first_line_column_types ]
        #we error on the larger number of columns
        #first we pad our column_types by using data from first line
        if len( first_line_column_types ) > len( column_types ):
            for column_type in first_line_column_types[len( column_types ):]:
                column_types.append( column_type )
        #Now we fill any unknown (None) column_types with data from first line
        for i in range( len( column_types ) ):
            if column_types[i] is None:
                if len( first_line_column_types ) <= i or first_line_column_types[i] is None:
                    column_types[i] = default_column_type
                else:
                    column_types[i] = first_line_column_types[i]
        # Set the discovered metadata values for the dataset
        dataset.metadata.data_lines = data_lines
        dataset.metadata.comment_lines = comment_lines
        dataset.metadata.column_types = column_types
        dataset.metadata.columns = len( column_types )
    def make_html_table( self, dataset, skipchars=[] ):
        """Create HTML table, used for displaying peek"""
        out = ['<table cellspacing="0" cellpadding="3">']
        try:
            out.append( '<tr>' )
            # Generate column header
            for i in range( 1, dataset.metadata.columns+1 ):
                out.append( '<th>%s</th>' % str( i ) )
            out.append( '</tr>' )
            out.append( self.make_html_peek_rows( dataset, skipchars=skipchars ) )
            out.append( '</table>' )
            out = "".join( out )
        except Exception, exc:
            out = "Can't create peek %s" % str( exc )
        return out
    def make_html_peek_rows( self, dataset, skipchars=[] ):
        out = [""]
        comments = []
        if not dataset.peek:
            dataset.set_peek()
        data = dataset.peek
        lines =  data.splitlines()
        for line in lines:
            line = line.rstrip( '\r\n' )
            if not line:
                continue
            comment = False
            for skipchar in skipchars:
                if line.startswith( skipchar ):
                    comments.append( line )
                    comment = True
                    break
            if comment:
                continue
            elems = line.split( '\t' )
            if len( elems ) != dataset.metadata.columns:
                # We may have an invalid comment line or invalid data
                comments.append( line )
                comment = True
                continue
            while len( comments ) > 0: # Keep comments
                try:
                    out.append( '<tr><td colspan="100%">' )
                except:
                    out.append( '<tr><td>' )
                out.append( '%s</td></tr>'  % escape( comments.pop(0) ) )
            out.append( '<tr>' )
            for elem in elems: # valid data
                elem = escape( elem )
                out.append( '<td>%s</td>' % elem )
            out.append( '</tr>' )
        # Peek may consist only of comments
        while len( comments ) > 0:
            try:
                out.append( '<tr><td colspan="100%">' )
            except:
                out.append( '<tr><td>' )
            out.append( '%s</td></tr>'  % escape( comments.pop(0) ) )
        return "".join( out )
    def set_peek( self, dataset, line_count=None, is_multi_byte=False ):
        data.Text.set_peek( self, dataset, line_count=line_count, is_multi_byte=is_multi_byte )
        if dataset.metadata.comment_lines:
            dataset.blurb = "%s, %s comments" % ( dataset.blurb, util.commaify( str( dataset.metadata.comment_lines ) ) )
    def display_peek( self, dataset ):
        """Returns formatted html of peek"""
        return self.make_html_table( dataset )
    def as_gbrowse_display_file( self, dataset, **kwd ):
        return open( dataset.file_name )
    def as_ucsc_display_file( self, dataset, **kwd ):
        return open( dataset.file_name )

class Taxonomy( Tabular ):
    def __init__(self, **kwd):
        """Initialize taxonomy datatype"""
        Tabular.__init__( self, **kwd )
        self.column_names = ['Name', 'TaxId', 'Root', 'Superkingdom', 'Kingdom', 'Subkingdom',
                             'Superphylum', 'Phylum', 'Subphylum', 'Superclass', 'Class', 'Subclass',
                             'Superorder', 'Order', 'Suborder', 'Superfamily', 'Family', 'Subfamily',
                             'Tribe', 'Subtribe', 'Genus', 'Subgenus', 'Species', 'Subspecies'
                             ]
    def make_html_table( self, dataset, skipchars=[] ):
        """Create HTML table, used for displaying peek"""
        out = ['<table cellspacing="0" cellpadding="3">']
        comments = []
        try:
            # Generate column header
            out.append( '<tr>' )
            for i, name in enumerate( self.column_names ):
                out.append( '<th>%s.%s</th>' % ( str( i+1 ), name ) )
            # This data type requires at least 24 columns in the data
            if dataset.metadata.columns - len( self.column_names ) > 0:
                for i in range( len( self.column_names ), dataset.metadata.columns ):
                    out.append( '<th>%s</th>' % str( i+1 ) )
                out.append( '</tr>' )
            out.append( self.make_html_peek_rows( dataset, skipchars=skipchars ) )
            out.append( '</table>' )
            out = "".join( out )
        except Exception, exc:
            out = "Can't create peek %s" % exc
        return out

class Sam( Tabular ):
    file_ext = 'sam'
    def __init__(self, **kwd):
        """Initialize taxonomy datatype"""
        Tabular.__init__( self, **kwd )
        self.column_names = ['QNAME', 'FLAG', 'RNAME', 'POS', 'MAPQ', 'CIGAR',
                             'MRNM', 'MPOS', 'ISIZE', 'SEQ', 'QUAL', 'OPT'
                             ]
    def make_html_table( self, dataset, skipchars=[] ):
        """Create HTML table, used for displaying peek"""
        out = ['<table cellspacing="0" cellpadding="3">']
        try:
            # Generate column header
            out.append( '<tr>' )
            for i, name in enumerate( self.column_names ):
                out.append( '<th>%s.%s</th>' % ( str( i+1 ), name ) )
            # This data type requires at least 11 columns in the data
            if dataset.metadata.columns - len( self.column_names ) > 0:
                for i in range( len( self.column_names ), dataset.metadata.columns ):
                    out.append( '<th>%s</th>' % str( i+1 ) )
                out.append( '</tr>' )
            out.append( self.make_html_peek_rows( dataset, skipchars=skipchars ) )
            out.append( '</table>' )
            out = "".join( out )
        except Exception, exc:
            out = "Can't create peek %s" % exc
        return out
    def sniff( self, filename ):
        """
        Determines whether the file is in SAM format
        
        A file in SAM format consists of lines of tab-separated data.
        The following header line may be the first line:
        @QNAME  FLAG    RNAME   POS     MAPQ    CIGAR   MRNM    MPOS    ISIZE   SEQ     QUAL
        or
        @QNAME  FLAG    RNAME   POS     MAPQ    CIGAR   MRNM    MPOS    ISIZE   SEQ     QUAL    OPT
        Data in the OPT column is optional and can consist of tab-separated data

        For complete details see http://samtools.sourceforge.net/SAM1.pdf
        
        Rules for sniffing as True:
            There must be 11 or more columns of data on each line
            Columns 2 (FLAG), 4(POS), 5 (MAPQ), 8 (MPOS), and 9 (ISIZE) must be numbers (9 can be negative)
            We will only check that up to the first 5 alignments are correctly formatted.
        
        >>> fname = get_test_fname( 'sequence.maf' )
        >>> Sam().sniff( fname )
        False
        >>> fname = get_test_fname( '1.sam' )
        >>> Sam().sniff( fname )
        True
        """
        try:
            fh = open( filename )
            count = 0
            while True:
                line = fh.readline()
                line = line.strip()
                if not line:
                    break #EOF
                if line: 
                    if line[0] != '@':
                        linePieces = line.split('\t')
                        if len(linePieces) < 11:
                            return False
                        try:
                            check = int(linePieces[1])
                            check = int(linePieces[3])
                            check = int(linePieces[4])
                            check = int(linePieces[7])
                            check = int(linePieces[8])
                        except ValueError:
                            return False
                        count += 1
                        if count == 5:
                            return True
            fh.close()
            if count < 5 and count > 0:
                return True
        except:
            pass
        return False
