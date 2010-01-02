import os, sys, shutil

# change back to the build dir
if os.path.dirname( sys.argv[0] ) != "":
    os.chdir( os.path.dirname( sys.argv[0] ) )

# find setuptools
scramble_lib = os.path.join( "..", "..", "..", "lib" )
sys.path.append( scramble_lib )
import get_platform # fixes fat python 2.5
from ez_setup import use_setuptools
use_setuptools( download_delay=8, to_dir=scramble_lib )
from setuptools import *

# get the tag
if os.access( ".galaxy_tag", os.F_OK ):
    tagfile = open( ".galaxy_tag", "r" )
    tag = tagfile.readline().strip()
else:
    tag = None

# in case you're running this by hand from a dirty module source dir
for dir in [ "build", "dist" ]:
    if os.access( dir, os.F_OK ):
        print "scramble.py: removing dir:", dir
        shutil.rmtree( dir )

# reset args for distutils
me = sys.argv[0]
sys.argv = [ me ]
sys.argv.append( "egg_info" )
if tag is not None:
    #sys.argv.append( "egg_info" )
    sys.argv.append( "--tag-build=%s" %tag )
# svn revision (if any) is handled directly in tag-build
sys.argv.append( "--no-svn-revision" )
sys.argv.append( "bdist_egg" )

# do it
execfile( "setup.py", globals(), locals() )
