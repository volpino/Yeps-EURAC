#!/usr/bin/env python

import sys

from glob import glob
from subprocess import call
from shutil import copyfile
from os import path

# Scripts that should not be packed -- just copied
do_not_pack = set( [ "ie_pngfix.js", "aflax.js" ] )

cmd = "java -jar ../../scripts/yuicompressor.jar --type js %(fname)s -o packed/%(fname)s"

# If specific scripts specified on command line, just pack them, otherwise pack
# all.

if len( sys.argv ) > 1:
    to_pack = sys.argv[1:]
else:
    to_pack = glob( "*.js" )

for fname in to_pack:
    d = dict( fname=fname )
    print "%(fname)s --> packed/%(fname)s" % d
    if fname in do_not_pack:
        copyfile( fname, path.join( 'packed', fname ) )
    else:
        out = call( cmd % d, shell=True )
