#!/usr/bin/env python

"""
Read a chromosome of wiggle data, and write it as a npy array, as 
well as averages over regions of progressively larger size in powers of 10
"""

from __future__ import division

import sys
from galaxy import eggs
import pkg_resources; pkg_resources.require( "bx-python" )
import bx.wiggle
from bx.cookbook import doc_optparse
from bx import misc
max2 = max
pkg_resources.require("numpy>=1.2.1")
from numpy import *
import tempfile
import os
from galaxy.tracks.store import sanitize_name


def write_chrom(max, out_base, instream):
   
    scores = zeros( max, float32 ) * nan
    # Fill array from wiggle
    for line in instream:
        line = line.rstrip("\n\r")
        (chrom, pos, val) = line.split("\t")
        pos, val = int(pos), float(val)
        scores[pos] = val
    
    # Write ra
    fname = "%s_%d" % ( out_base, 1 )
    save( fname, scores )
    os.rename( fname+".npy", fname )

    # Write average
    for window in 10, 100, 1000, 10000, 100000:
        input = scores.copy()
        size = len( input )
        input.resize( ( ( size / window ), window ) )
        masked = ma.masked_array( input, isnan( input ) )
        averaged = mean( masked, 1 )
        averaged.set_fill_value( nan )
        fname = "%s_%d" % ( out_base, window )
        save( fname, averaged.filled() )
        del masked, averaged
        os.rename( fname+".npy", fname )

def main():
    max = int( 512*1024*1024 )
    # get chroms and lengths
    chroms = {}
    LEN = {}
    for (chrom, pos, val) in bx.wiggle.Reader( open(sys.argv[1],"r") ):
        chrom_file = chroms.get(chrom, None)
        if not chrom_file:
            chrom_file = chroms[chrom] =  tempfile.NamedTemporaryFile()
        chrom_file.write("%s\t%s\t%s\n" % (chrom,pos,val))
        LEN[chrom] = max2( LEN.get(chrom,0), pos+1 )
    for chrom, stream in chroms.items():
        stream.seek(0)
        prefix = os.path.join(sys.argv[2], sanitize_name(chrom))
        write_chrom( LEN[chrom], prefix, stream )

    manifest_file = open( os.path.join( sys.argv[2], "manifest.tab" ),"w" )
    for key, value in LEN.items():
        print >> manifest_file, "%s\t%s" % (key, value)
    manifest_file.close()
    
    
if __name__ == "__main__": main()
