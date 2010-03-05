#!/usr/bin/env python
#Guruprasad Ananda
"""
Converts coordinates from one build/assembly to another using liftOver binary and mapping files downloaded from UCSC.
"""

import sys, os, string
import tempfile
import re

assert sys.version_info[:2] >= ( 2, 4 )

def stop_err(msg):
    sys.stderr.write(msg)
    sys.exit()

def safe_bed_file(infile):
    """Make a BED file with track and browser lines ready for liftOver.

    liftOver will fail with track or browser lines. We can make it happy
    by converting these to comments. See:

    https://lists.soe.ucsc.edu/pipermail/genome/2007-May/013561.html
    """
    fix_pat = re.compile("^(track|browser)")
    (fd, fname) = tempfile.mkstemp()
    in_handle = open(infile)
    out_handle = open(fname, "w")
    for line in in_handle:
        if fix_pat.match(line):
            line = "#" + line
        out_handle.write(line)
    in_handle.close()
    out_handle.close()
    return fname
    
if len( sys.argv ) != 7:
    stop_err( "USAGE: prog input out_file1 out_file2 input_dbkey output_dbkey minMatch" )

infile = sys.argv[1]
outfile1 = sys.argv[2]
outfile2 = sys.argv[3]
in_dbkey = sys.argv[4]
mapfilepath = sys.argv[5]
minMatch = sys.argv[6]
try:
    assert float(minMatch)
except:
    minMatch = 0.1
#ensure dbkey is set
if in_dbkey == "?": 
    stop_err( "Input dataset genome build unspecified, click the pencil icon in the history item to specify it." )


if not os.path.isfile( mapfilepath ):
    stop_err( "%s mapping is not currently available."  % ( mapfilepath.split('/')[-1].split('.')[0] ) )

safe_infile = safe_bed_file(infile)
cmd_line = "liftOver -minMatch=" + str(minMatch) + " " + safe_infile + " " + mapfilepath + " " + outfile1 + " " + outfile2 + "  > /dev/null 2>&1"
try:
    os.system( cmd_line )
except Exception, exc:
    stop_err( "Exception caught attempting conversion: %s"  % str( exc ) )
finally:
    os.remove(safe_infile)
