"""
Qualityscore class
"""

import data
import logging
from galaxy.datatypes.sniff import *
from galaxy import util

log = logging.getLogger(__name__)

class QualityScoreSOLiD ( data.Text ):
    """
    until we know more about quality score formats
    """
    file_ext = "qualsolid"

    def sniff( self, filename ):
        """
        >>> fname = get_test_fname( 'sequence.fasta' )
        >>> QualityScoreSOLiD().sniff( fname )
        False
        >>> fname = get_test_fname( 'sequence.qualsolid' )
        >>> QualityScoreSOLiD().sniff( fname )
        True
        """
        try:
            fh = open( filename )
            readlen = None
            goodblock = 0
            while True:
                line = fh.readline()
                if not line:
                    if goodblock > 0:
                        return True
                    else:
                        break #EOF
                line = line.strip()
                if line and not line.startswith( '#' ): #first non-empty non-comment line
                    if line.startswith( '>' ):
                        line = fh.readline().strip()
                        if line == '' or line.startswith( '>' ):
                            break
                        try:
                            [ int( x ) for x in line.split() ]
                            if not(readlen):
                                readlen = len(line.split())
                            assert len(line.split()) == readlen    #SOLiD reads should be of the same length
                        except:
                            break
                        goodblock += 1
                        if goodblock > 10:
                            return True
                    else:
                        break #we found a non-empty line, but it's not a header
            fh.close()
        except:
            pass
        return False

class QualityScore454 ( data.Text ):
    """
    until we know more about quality score formats
    """
    file_ext = "qual454"

    def sniff( self, filename ):
        """
        >>> fname = get_test_fname( 'sequence.fasta' )
        >>> QualityScore454().sniff( fname )
        False
        >>> fname = get_test_fname( 'sequence.qual454' )
        >>> QualityScore454().sniff( fname )
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
                        try:
                            [ int( x ) for x in line.split() ]
                        except:
                            break
                        return True
                    else:
                        break #we found a non-empty line, but it's not a header
            fh.close()
        except:
            pass
        return False

class QualityScoreSolexa ( data.Text ):
    """
    until we know more about quality score formats
    """
    file_ext = "qualsolexa"
   