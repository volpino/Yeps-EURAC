"""
File format detector
"""
import logging, sys, os, csv, tempfile, shutil, re, zipfile
import registry
from galaxy import util

log = logging.getLogger(__name__)
        
def get_test_fname(fname):
    """Returns test data filename"""
    path, name = os.path.split(__file__)
    full_path = os.path.join(path, 'test', fname)
    return full_path

def stream_to_file( stream, suffix='', prefix='', dir=None, text=False ):
    """Writes a stream to a temporary file, returns the temporary file's name"""
    fd, temp_name = tempfile.mkstemp( suffix=suffix, prefix=prefix, dir=dir, text=text )
    CHUNK_SIZE = 1048576
    data_checked = False
    is_compressed = False
    is_binary = False
    is_multi_byte = False
    while 1:
        chunk = stream.read( CHUNK_SIZE )
        if not chunk:
            break
        if not data_checked:
            # See if we're uploading a compressed file
            if zipfile.is_zipfile( temp_name ):
                is_compressed = True
            else:
                try:
                    if unicode( chunk[:2] ) == unicode( util.gzip_magic ):
                        is_compressed = True
                except:
                    pass
            if not is_compressed:
                # See if we have a multi-byte character file
                chars = chunk[:100]
                is_multi_byte = util.is_multi_byte( chars )
                if not is_multi_byte:
                    for char in chars:
                        if ord( char ) > 128:
                            is_binary = True
                            break
            data_checked = True
        if not is_compressed and not is_binary:
            os.write( fd, chunk.encode( "utf-8" ) )
        else:
            # Compressed files must be encoded after they are uncompressed in the upload utility,
            # while binary files should not be encoded at all.
            os.write( fd, chunk )
    os.close( fd )
    return temp_name, is_multi_byte

def check_newlines( fname, bytes_to_read=52428800 ):
    """
    Determines if there are any non-POSIX newlines in the first
    number_of_bytes (by default, 50MB) of the file.
    """
    CHUNK_SIZE = 2 ** 20
    f = open( fname, 'r' )
    for chunk in f.read( CHUNK_SIZE ):
        if f.tell() > bytes_to_read:
            break
        if chunk.count( '\r' ):
            f.close()
            return True
    f.close()
    return False

def convert_newlines( fname ):
    """
    Converts in place a file from universal line endings 
    to Posix line endings.

    >>> fname = get_test_fname('temp.txt')
    >>> file(fname, 'wt').write("1 2\\r3 4")
    >>> convert_newlines(fname)
    2
    >>> file(fname).read()
    '1 2\\n3 4\\n'
    """
    fd, temp_name = tempfile.mkstemp()
    fp = os.fdopen( fd, "wt" )
    for i, line in enumerate( file( fname, "U" ) ):
        fp.write( "%s\n" % line.rstrip( "\r\n" ) )
    fp.close()
    shutil.move( temp_name, fname )
    # Return number of lines in file.
    return i + 1

def sep2tabs(fname, patt="\\s+"):
    """
    Transforms in place a 'sep' separated file to a tab separated one

    >>> fname = get_test_fname('temp.txt')
    >>> file(fname, 'wt').write("1 2\\n3 4\\n")
    >>> sep2tabs(fname)
    2
    >>> file(fname).read()
    '1\\t2\\n3\\t4\\n'
    """
    regexp = re.compile( patt )
    fd, temp_name = tempfile.mkstemp()
    fp = os.fdopen( fd, "wt" )
    for i, line in enumerate( file( fname ) ):
        line  = line.rstrip( '\r\n' )
        elems = regexp.split( line )
        fp.write( "%s\n" % '\t'.join( elems ) )
    fp.close()
    shutil.move( temp_name, fname )
    # Return number of lines in file.
    return i + 1

def convert_newlines_sep2tabs( fname, patt="\\s+" ):
    """
    Combines above methods: convert_newlines() and sep2tabs()
    so that files do not need to be read twice

    >>> fname = get_test_fname('temp.txt')
    >>> file(fname, 'wt').write("1 2\\r3 4")
    >>> convert_newlines_sep2tabs(fname)
    2
    >>> file(fname).read()
    '1\\t2\\n3\\t4\\n'
    """
    regexp = re.compile( patt )
    fd, temp_name = tempfile.mkstemp()
    fp = os.fdopen( fd, "wt" )
    for i, line in enumerate( file( fname, "U" ) ):
        line  = line.rstrip( '\r\n' )
        elems = regexp.split( line )
        fp.write( "%s\n" % '\t'.join( elems ) )
    fp.close()
    shutil.move( temp_name, fname )
    # Return number of lines in file.
    return i + 1

def get_headers( fname, sep, count=60, is_multi_byte=False ):
    """
    Returns a list with the first 'count' lines split by 'sep'
    
    >>> fname = get_test_fname('complete.bed')
    >>> get_headers(fname,'\\t')
    [['chr7', '127475281', '127491632', 'NM_000230', '0', '+', '127486022', '127488767', '0', '3', '29,172,3225,', '0,10713,13126,'], ['chr7', '127486011', '127488900', 'D49487', '0', '+', '127486022', '127488767', '0', '2', '155,490,', '0,2399']]
    """
    headers = []
    for idx, line in enumerate(file(fname)):
        line = line.rstrip('\n\r')
        if is_multi_byte:
            # TODO: fix this - sep is never found in line
            line = unicode( line, 'utf-8' )
            sep = sep.encode( 'utf-8' )
        headers.append( line.split(sep) )
        if idx == count:
            break
    return headers
    
def is_column_based( fname, sep='\t', skip=0, is_multi_byte=False ):
    """
    Checks whether the file is column based with respect to a separator 
    (defaults to tab separator).
    
    >>> fname = get_test_fname('test.gff')
    >>> is_column_based(fname)
    True
    >>> fname = get_test_fname('test_tab.bed')
    >>> is_column_based(fname)
    True
    >>> is_column_based(fname, sep=' ')
    False
    >>> fname = get_test_fname('test_space.txt')
    >>> is_column_based(fname)
    False
    >>> is_column_based(fname, sep=' ')
    True
    >>> fname = get_test_fname('test_ensembl.tab')
    >>> is_column_based(fname)
    True
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> is_column_based(fname, sep=' ', skip=0)
    False
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> is_column_based(fname)
    True
    """
    headers = get_headers( fname, sep, is_multi_byte=is_multi_byte )
    count = 0
    if not headers:
        return False
    for hdr in headers[skip:]:
        if hdr and hdr[0] and not hdr[0].startswith('#'):
            if len(hdr) > 1:
                count = len(hdr)
            break
    if count < 2:
        return False
    for hdr in headers[skip:]:
        if hdr and hdr[0] and not hdr[0].startswith('#'):
            if len(hdr) != count:
                return False
    return True

def guess_ext( fname, sniff_order=None, is_multi_byte=False ):
    """
    Returns an extension that can be used in the datatype factory to
    generate a data for the 'fname' file

    >>> fname = get_test_fname('megablast_xml_parser_test1.blastxml')
    >>> guess_ext(fname)
    'blastxml'
    >>> fname = get_test_fname('interval.interval')
    >>> guess_ext(fname)
    'interval'
    >>> fname = get_test_fname('interval1.bed')
    >>> guess_ext(fname)
    'bed'
    >>> fname = get_test_fname('test_tab.bed')
    >>> guess_ext(fname)
    'bed'
    >>> fname = get_test_fname('sequence.maf')
    >>> guess_ext(fname)
    'maf'
    >>> fname = get_test_fname('sequence.fasta')
    >>> guess_ext(fname)
    'fasta'
    >>> fname = get_test_fname('file.html')
    >>> guess_ext(fname)
    'html'
    >>> fname = get_test_fname('test.gff')
    >>> guess_ext(fname)
    'gff'
    >>> fname = get_test_fname('gff_version_3.gff')
    >>> guess_ext(fname)
    'gff3'
    >>> fname = get_test_fname('temp.txt')
    >>> file(fname, 'wt').write("a\\t2\\nc\\t1\\nd\\t0")
    >>> guess_ext(fname)
    'tabular'
    >>> fname = get_test_fname('temp.txt')
    >>> file(fname, 'wt').write("a 1 2 x\\nb 3 4 y\\nc 5 6 z")
    >>> guess_ext(fname)
    'txt'
    >>> fname = get_test_fname('test_tab1.tabular')
    >>> guess_ext(fname)
    'tabular'
    >>> fname = get_test_fname('alignment.lav')
    >>> guess_ext(fname)
    'lav'
    >>> fname = get_test_fname('1.sff')
    >>> guess_ext(fname)
    'sff'
    >>> fname = get_test_fname('1.bam')
    >>> guess_ext(fname)
    'bam'
    >>> fname = get_test_fname('3.bam')
    >>> guess_ext(fname)
    'bam'
    """
    if sniff_order is None:
        datatypes_registry = registry.Registry()
        sniff_order = datatypes_registry.sniff_order
    for datatype in sniff_order:
        """
        Some classes may not have a sniff function, which is ok.  In fact, the
        Tabular and Text classes are 2 examples of classes that should never have
        a sniff function.  Since these classes are default classes, they contain 
        few rules to filter out data of other formats, so they should be called
        from this function after all other datatypes in sniff_order have not been
        successfully discovered.
        """
        try:
            if datatype.sniff( fname ):
                return datatype.file_ext
        except:
            pass
    headers = get_headers( fname, None )
    is_binary = False
    if is_multi_byte:
        is_binary = False
    else:
        for hdr in headers:
            for char in hdr:
                if len( char ) > 1:
                    for c in char:
                        if ord( c ) > 128:
                            is_binary = True
                            break
                elif ord( char ) > 128:
                    is_binary = True
                    break
                if is_binary:
                    break
            if is_binary:
                break
    if is_binary:
        return 'data'        #default binary data type file extension
    if is_column_based( fname, '\t', 1, is_multi_byte=is_multi_byte ):
        return 'tabular'    #default tabular data type file extension
    return 'txt'            #default text data type file extension

if __name__ == '__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    
