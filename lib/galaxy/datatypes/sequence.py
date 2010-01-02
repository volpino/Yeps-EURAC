"""
Sequence classes
"""

import data
import logging
import re
import string
from cgi import escape
from galaxy.datatypes.metadata import MetadataElement
from galaxy.datatypes import metadata
import galaxy.model
from galaxy import util
from sniff import *

log = logging.getLogger(__name__)

class Sequence( data.Text ):
    """Class describing a sequence"""

    """Add metadata elements"""
    MetadataElement( name="sequences", default=0, desc="Number of sequences", readonly=True, visible=False, optional=True, no_value=0 )

    def set_meta( self, dataset, **kwd ):
        """
        Set the number of sequences and the number of data lines in dataset.
        """
        data_lines = 0
        sequences = 0
        for line in file( dataset.file_name ):
            line = line.strip()
            if line and line.startswith( '#' ):
                # We don't count comment lines for sequence data types
                continue
            if line and line.startswith( '>' ):
                sequences += 1
                data_lines +=1
            else:
                data_lines += 1
        dataset.metadata.data_lines = data_lines
        dataset.metadata.sequences = sequences
    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = data.get_file_peek( dataset.file_name, is_multi_byte=is_multi_byte )
            if dataset.metadata.sequences:
                dataset.blurb = "%s sequences" % util.commaify( str( dataset.metadata.sequences ) )
            else:
                dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

class Alignment( data.Text ):
    """Class describing an alignment"""

    """Add metadata elements"""
    MetadataElement( name="species", desc="Species", default=[], param=metadata.SelectParameter, multiple=True, readonly=True, no_value=None )

class Fasta( Sequence ):
    """Class representing a FASTA sequence"""
    file_ext = "fasta"

    def sniff( self, filename ):
        """
        Determines whether the file is in fasta format
        
        A sequence in FASTA format consists of a single-line description, followed by lines of sequence data. 
        The first character of the description line is a greater-than (">") symbol in the first column. 
        All lines should be shorter than 80 charcters
        
        For complete details see http://www.ncbi.nlm.nih.gov/blast/fasta.shtml
        
        Rules for sniffing as True:
            We don't care about line length (other than empty lines).
            The first non-empty line must start with '>' and the Very Next line.strip() must have sequence data and not be a header.
                'sequence data' here is loosely defined as non-empty lines which do not start with '>'
                This will cause Color Space FASTA (csfasta) to be detected as True (they are, after all, still FASTA files - they have a header line followed by sequence data)
                    Previously this method did some checking to determine if the sequence data had integers (presumably to differentiate between fasta and csfasta)
                    This should be done through sniff order, where csfasta (currently has a null sniff function) is detected for first (stricter definition) followed sometime after by fasta
            We will only check that the first purported sequence is correctly formatted.
        
        >>> fname = get_test_fname( 'sequence.maf' )
        >>> Fasta().sniff( fname )
        False
        >>> fname = get_test_fname( 'sequence.fasta' )
        >>> Fasta().sniff( fname )
        True
        """
        
        try:
            fh = open( filename )
            while True:
                line = fh.readline()
                if not line:
                    break #EOF
                line = line.strip()
                if line: #first non-empty line
                    if line.startswith( '>' ):
                        #The next line.strip() must not be '', nor startwith '>'
                        line = fh.readline().strip()
                        if line == '' or line.startswith( '>' ):
                            break
                        return True
                    else:
                        break #we found a non-empty line, but its not a fasta header
            fh.close()
        except:
            pass
        return False

class csFasta( Sequence ):
    """ Class representing the SOLID Color-Space sequence ( csfasta ) """
    file_ext = "csfasta"

    def sniff( self, filename ):
        """
        Color-space sequence: 
            >2_15_85_F3
            T213021013012303002332212012112221222112212222

        >>> fname = get_test_fname( 'sequence.fasta' )
        >>> csFasta().sniff( fname )
        False
        >>> fname = get_test_fname( 'sequence.csfasta' )
        >>> csFasta().sniff( fname )
        True
        """
        try:
            fh = open( filename )
            while True:
                line = fh.readline()
                if not line:
                    break #EOF
                line = line.strip()
                if line and not line.startswith( '#' ): #first non-empty non-comment line
                    if line.startswith( '>' ):
                        line = fh.readline().strip()
                        if line == '' or line.startswith( '>' ):
                            break
                        elif line[0] not in string.ascii_uppercase:
                            return False
                        elif len( line ) > 1 and not re.search( '^\d+$', line[1:] ):
                            return False
                        return True
                    else:
                        break #we found a non-empty line, but it's not a header
            fh.close()
        except:
            pass
        return False

class Fastq ( Sequence ):
    """Class representing a generic FASTQ sequence"""
    file_ext = "fastq"

    def set_meta( self, dataset, **kwd ):
        """
        Set the number of sequences and the number of data lines
        in dataset.
        """
        data_lines = 0
        sequences = 0
        for line in file( dataset.file_name ):
            line = line.strip()
            if line and line.startswith( '#' ):
                # We don't count comment lines for sequence data types
                continue
            if line and line.startswith( '@' ):
                sequences += 1
                data_lines +=1
            else:
                data_lines += 1
        dataset.metadata.data_lines = data_lines
        dataset.metadata.sequences = sequences
    def sniff ( self, filename ):
        """
        Determines whether the file is in generic fastq format
        For details, see http://maq.sourceforge.net/fastq.shtml

        Note: There are three kinds of FASTQ files, known as "Sanger" (sometimes called "Standard"), Solexa, and Illumina
              These differ in the representation of the quality scores

        >>> fname = get_test_fname( '1.fastqsanger' )
        >>> Fastq().sniff( fname )
        True
        >>> fname = get_test_fname( '2.fastqsanger' )
        >>> Fastq().sniff( fname )
        True
        """
        headers = get_headers( filename, None )
        bases_regexp = re.compile( "^[NGTAC]*" )
        # check that first block looks like a fastq block
        try:
            if len( headers ) >= 4 and headers[0][0] and headers[0][0][0] == "@" and headers[2][0] and headers[2][0][0] == "+" and headers[1][0]:
                # Check the sequence line, make sure it contains only G/C/A/T/N
                if not bases_regexp.match( headers[1][0] ):
                    return False
                return True 
            return False
        except:
            return False

class FastqSanger( Fastq ):
    """Class representing a FASTQ sequence ( the Sanger variant )"""
    file_ext = "fastqsanger"

try:
    from galaxy import eggs
    import pkg_resources; pkg_resources.require( "bx-python" )
    import bx.align.maf
except:
    pass

#trying to import maf_utilities here throws an ImportError due to a circular import between jobs and tools:
#from galaxy.tools.util.maf_utilities import build_maf_index_species_chromosomes
#Traceback (most recent call last):
#  File "./scripts/paster.py", line 27, in <module>
#    command.run()
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/script/command.py", line 78, in run
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/script/command.py", line 117, in invoke
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/script/command.py", line 212, in run
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/script/serve.py", line 227, in command
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/script/serve.py", line 250, in loadapp
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 193, in loadapp
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 213, in loadobj
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 237, in loadcontext
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 267, in _loadconfig
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 397, in get_context
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 439, in _context_from_explicit
#  File "build/bdist.solaris-2.11-i86pc/egg/paste/deploy/loadwsgi.py", line 18, in import_string
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/pkg_resources.py", line 1912, in load
#    entry = __import__(self.module_name, globals(),globals(), ['__name__'])
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/galaxy/web/buildapp.py", line 18, in <module>
#    from galaxy import config, jobs, util, tools
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/galaxy/jobs/__init__.py", line 3, in <module>
#    from galaxy import util, model
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/galaxy/model/__init__.py", line 13, in <module>
#    import galaxy.datatypes.registry
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/galaxy/datatypes/registry.py", line 6, in <module>
#    import data, tabular, interval, images, sequence, qualityscore, genetics, xml, coverage, tracks, chrominfo
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/galaxy/datatypes/sequence.py", line 344, in <module>
#    from galaxy.tools.util.maf_utilities import build_maf_index_species_chromosomes
#  File "/afs/bx.psu.edu/home/dan/galaxy/central/lib/galaxy/tools/__init__.py", line 15, in <module>
#    from galaxy import util, jobs, model
#ImportError: cannot import name jobs
#so we'll copy and paste for now...terribly icky
#*** ANYCHANGE TO THIS METHOD HERE OR IN maf_utilities MUST BE PROPAGATED ***
def COPIED_build_maf_index_species_chromosomes( filename, index_species = None ):
    species = []
    species_chromosomes = {}
    indexes = bx.interval_index_file.Indexes()
    blocks = 0
    try:
        maf_reader = bx.align.maf.Reader( open( filename ) )
        while True:
            pos = maf_reader.file.tell()
            block = maf_reader.next()
            if block is None:
                break
            blocks += 1
            for c in block.components:
                spec = c.src
                chrom = None
                if "." in spec:
                    spec, chrom = spec.split( ".", 1 )
                if spec not in species: 
                    species.append( spec )
                    species_chromosomes[spec] = []
                if chrom and chrom not in species_chromosomes[spec]:
                    species_chromosomes[spec].append( chrom )
                if index_species is None or spec in index_species:
                    forward_strand_start = c.forward_strand_start
                    forward_strand_end = c.forward_strand_end
                    try:
                        forward_strand_start = int( forward_strand_start )
                        forward_strand_end = int( forward_strand_end )
                    except ValueError:
                        continue #start and end are not integers, can't add component to index, goto next component
                        #this likely only occurs when parse_e_rows is True?
                        #could a species exist as only e rows? should the
                    if forward_strand_end > forward_strand_start:
                        #require positive length; i.e. certain lines have start = end = 0 and cannot be indexed
                        indexes.add( c.src, forward_strand_start, forward_strand_end, pos, max=c.src_size )
    except Exception, e:
        #most likely a bad MAF
        log.debug( 'Building MAF index on %s failed: %s' % ( filename, e ) )
        return ( None, [], {}, 0 )
    return ( indexes, species, species_chromosomes, blocks )

class Maf( Alignment ):
    """Class describing a Maf alignment"""
    file_ext = "maf"
    
    #Readonly and optional, users can't unset it, but if it is not set, we are generally ok; if required use a metadata validator in the tool definition
    MetadataElement( name="blocks", default=0, desc="Number of blocks", readonly=True, optional=True, visible=False, no_value=0 )
    MetadataElement( name="species_chromosomes", desc="Species Chromosomes", param=metadata.FileParameter, readonly=True, no_value=None, visible=False, optional=True )
    MetadataElement( name="maf_index", desc="MAF Index File", param=metadata.FileParameter, readonly=True, no_value=None, visible=False, optional=True )

    def init_meta( self, dataset, copy_from=None ):
        Alignment.init_meta( self, dataset, copy_from=copy_from )
    def set_meta( self, dataset, overwrite = True, **kwd ):
        """
        Parses and sets species, chromosomes, index from MAF file.
        """
        #these metadata values are not accessable by users, always overwrite
        indexes, species, species_chromosomes, blocks = COPIED_build_maf_index_species_chromosomes( dataset.file_name )
        if indexes is None:
            return #this is not a MAF file
        dataset.metadata.species = species
        dataset.metadata.blocks = blocks
        
        #write species chromosomes to a file
        chrom_file = dataset.metadata.species_chromosomes
        if not chrom_file:
            chrom_file = dataset.metadata.spec['species_chromosomes'].param.new_file( dataset = dataset )
        chrom_out = open( chrom_file.file_name, 'wb' )
        for spec, chroms in species_chromosomes.items():
            chrom_out.write( "%s\t%s\n" % ( spec, "\t".join( chroms ) ) )
        chrom_out.close()
        dataset.metadata.species_chromosomes = chrom_file
        
        index_file = dataset.metadata.maf_index
        if not index_file:
            index_file = dataset.metadata.spec['maf_index'].param.new_file( dataset = dataset )
        indexes.write( open( index_file.file_name, 'wb' ) )
        dataset.metadata.maf_index = index_file
    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            # The file must exist on disk for the get_file_peek() method
            dataset.peek = data.get_file_peek( dataset.file_name, is_multi_byte=is_multi_byte )
            if dataset.metadata.blocks:
                dataset.blurb = "%s blocks" % util.commaify( str( dataset.metadata.blocks ) )
            else:
                # Number of blocks is not known ( this should not happen ), and auto-detect is
                # needed to set metadata
                dataset.blurb = "? blocks"
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'
    def display_peek( self, dataset ):
        """Returns formated html of peek"""
        return self.make_html_table( dataset )
    def make_html_table( self, dataset, skipchars=[] ):
        """Create HTML table, used for displaying peek"""
        out = ['<table cellspacing="0" cellpadding="3">']
        try:
            out.append('<tr><th>Species:&nbsp;')
            for species in dataset.metadata.species:
                out.append( '%s&nbsp;' % species )
            out.append( '</th></tr>' )
            if not dataset.peek:
                dataset.set_peek()
            data = dataset.peek
            lines =  data.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                out.append( '<tr><td>%s</td></tr>' % escape( line ) )
            out.append( '</table>' )
            out = "".join( out )
        except Exception, exc:
            out = "Can't create peek %s" % exc
        return out
    def sniff( self, filename ):
        """
        Determines wether the file is in maf format
        
        The .maf format is line-oriented. Each multiple alignment ends with a blank line. 
        Each sequence in an alignment is on a single line, which can get quite long, but 
        there is no length limit. Words in a line are delimited by any white space. 
        Lines starting with # are considered to be comments. Lines starting with ## can 
        be ignored by most programs, but contain meta-data of one form or another.
        
        The first line of a .maf file begins with ##maf. This word is followed by white-space-separated 
        variable=value pairs. There should be no white space surrounding the "=".
     
        For complete details see http://genome.ucsc.edu/FAQ/FAQformat#format5
        
        >>> fname = get_test_fname( 'sequence.maf' )
        >>> Maf().sniff( fname )
        True
        >>> fname = get_test_fname( 'sequence.fasta' )
        >>> Maf().sniff( fname )
        False
        """
        headers = get_headers( filename, None )
        try:
            if len(headers) > 1 and headers[0][0] and headers[0][0] == "##maf":
                return True
            else:
                return False
        except:
            return False

class Axt( data.Text ):
    """Class describing an axt alignment"""
    
    # gvk- 11/19/09 - This is really an alignment, but we no longer have tools that use this data type, and it is
    # here simply for backward compatibility ( although it is still in the datatypes registry ).  Subclassing
    # from data.Text eliminates managing metadata elements inherited from the Alignemnt class.

    file_ext = "axt"

    def sniff( self, filename ):
        """
        Determines whether the file is in axt format
        
        axt alignment files are produced from Blastz, an alignment tool available from Webb Miller's lab 
        at Penn State University.
        
        Each alignment block in an axt file contains three lines: a summary line and 2 sequence lines.
        Blocks are separated from one another by blank lines.
        
        The summary line contains chromosomal position and size information about the alignment. It
        consists of 9 required fields.
        
        The sequence lines contain the sequence of the primary assembly (line 2) and aligning assembly
        (line 3) with inserts.  Repeats are indicated by lower-case letters.
    
        For complete details see http://genome.ucsc.edu/goldenPath/help/axt.html
        
        >>> fname = get_test_fname( 'alignment.axt' )
        >>> Axt().sniff( fname )
        True
        >>> fname = get_test_fname( 'alignment.lav' )
        >>> Axt().sniff( fname )
        False
        """
        headers = get_headers( filename, None )
        if len(headers) < 4:
            return False
        for hdr in headers:
            if len(hdr) > 0 and hdr[0].startswith("##matrix=axt"):
                return True
            if len(hdr) > 0 and not hdr[0].startswith("#"):
                if len(hdr) != 9:
                    return False
                try:
                    map ( int, [hdr[0], hdr[2], hdr[3], hdr[5], hdr[6], hdr[8]] )
                except:
                    return False
                if hdr[7] not in data.valid_strand:
                    return False
                else:
                    return True

class Lav( data.Text ):
    """Class describing a LAV alignment"""

    file_ext = "lav"

    # gvk- 11/19/09 - This is really an alignment, but we no longer have tools that use this data type, and it is
    # here simply for backward compatibility ( although it is still in the datatypes registry ).  Subclassing
    # from data.Text eliminates managing metadata elements inherited from the Alignemnt class.

    def sniff( self, filename ):
        """
        Determines whether the file is in lav format
        
        LAV is an alignment format developed by Webb Miller's group. It is the primary output format for BLASTZ.
        The first line of a .lav file begins with #:lav.
    
        For complete details see http://www.bioperl.org/wiki/LAV_alignment_format
        
        >>> fname = get_test_fname( 'alignment.lav' )
        >>> Lav().sniff( fname )
        True
        >>> fname = get_test_fname( 'alignment.axt' )
        >>> Lav().sniff( fname )
        False
        """
        headers = get_headers( filename, None )
        try:
            if len(headers) > 1 and headers[0][0] and headers[0][0].startswith('#:lav'):
                return True
            else:
                return False
        except:
            return False
