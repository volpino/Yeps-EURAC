"""
Image classes
"""

import data
import logging
from galaxy.datatypes.metadata import MetadataElement
from galaxy.datatypes import metadata
from galaxy.datatypes.sniff import *
from urllib import urlencode, quote_plus
import zipfile
import os, subprocess, tempfile

log = logging.getLogger(__name__)

class Image( data.Data ):
    """Class describing an image"""
    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = 'Image in %s format' % dataset.extension
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'

def create_applet_tag_peek( class_name, archive, params ):
    text = """
<!--[if !IE]>-->
<object classid="java:%s" 
      type="application/x-java-applet"
      height="30" width="200" align="center" >
      <param name="archive" value="%s"/>""" % ( class_name, archive )
    for name, value in params.iteritems():
        text += """<param name="%s" value="%s"/>""" % ( name, value )
    text += """
<!--<![endif]-->
<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93" 
        height="30" width="200" >
        <param name="code" value="%s" />
        <param name="archive" value="%s"/>""" % ( class_name, archive )
    for name, value in params.iteritems():
        text += """<param name="%s" value="%s"/>""" % ( name, value )
    text += """</object> 
<!--[if !IE]>-->
</object>
<!--<![endif]-->
"""
    return """<div><p align="center">%s</p></div>""" % text

class Gmaj( data.Data ):
    """Class describing a GMAJ Applet"""
    file_ext = "gmaj.zip"
    copy_safe_peek = False
    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            if hasattr( dataset, 'history_id' ):
                params = {
                "bundle":"display?id=%s&tofile=yes&toext=.zip" % dataset.id,
                "buttonlabel": "Launch GMAJ",
                "nobutton": "false",
                "urlpause" :"100",
                "debug": "false",
                "posturl": quote_plus( "history_add_to?%s" % "&".join( [ "%s=%s" % ( key, value ) for key, value in { 'history_id': dataset.history_id, 'ext': 'maf', 'name': 'GMAJ Output on data %s' % dataset.hid, 'info': 'Added by GMAJ', 'dbkey': dataset.dbkey, 'copy_access_from': dataset.id }.items() ] ) )
                }
                class_name = "edu.psu.bx.gmaj.MajApplet.class"
                archive = "/static/gmaj/gmaj.jar"
                dataset.peek = create_applet_tag_peek( class_name, archive, params )
                dataset.blurb = 'GMAJ Multiple Alignment Viewer'
            else:
                dataset.peek = "After you add this item to your history, you will be able to launch the GMAJ applet."
                dataset.blurb = 'GMAJ Multiple Alignment Viewer'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'
    def display_peek(self, dataset):
        try:
            return dataset.peek
        except:
            return "peek unavailable"
    def get_mime(self):
        """Returns the mime type of the datatype"""
        return 'application/zip'
    def sniff(self, filename):
        """
        NOTE: the sniff.convert_newlines() call in the upload utility will keep Gmaj data types from being 
        correctly sniffed, but the files can be uploaded (they'll be sniffed as 'txt').  This sniff function
        is here to provide an example of a sniffer for a zip file.
        """
        if not zipfile.is_zipfile( filename ):
            return False
        contains_gmaj_file = False
        zip_file = zipfile.ZipFile(filename, "r")
        for name in zip_file.namelist():
            if name.split(".")[1].strip().lower() == 'gmaj':
                contains_gmaj_file = True
                break
        zip_file.close()
        if not contains_gmaj_file:
            return False
        return True
            
class Html( data.Text ):
    """Class describing an html file"""
    file_ext = "html"

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            dataset.peek = "HTML file"
            dataset.blurb = data.nice_size( dataset.get_size() )
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'
    def get_mime(self):
        """Returns the mime type of the datatype"""
        return 'text/html'
    def sniff( self, filename ):
        """
        Determines whether the file is in html format

        >>> fname = get_test_fname( 'complete.bed' )
        >>> Html().sniff( fname )
        False
        >>> fname = get_test_fname( 'file.html' )
        >>> Html().sniff( fname )
        True
        """
        headers = get_headers( filename, None )
        try:
            for i, hdr in enumerate(headers):
                if hdr and hdr[0].lower().find( '<html>' ) >=0:
                    return True
            return False
        except:
            return True

class Laj( data.Text ):
    """Class describing a LAJ Applet"""
    file_ext = "laj"
    copy_safe_peek = False

    def set_peek( self, dataset, is_multi_byte=False ):
        if not dataset.dataset.purged:
            if hasattr( dataset, 'history_id' ):
                params = {
                "alignfile1": "display?id=%s" % dataset.id,
                "buttonlabel": "Launch LAJ",
                "title": "LAJ in Galaxy",
                "posturl": quote_plus( "history_add_to?%s" % "&".join( [ "%s=%s" % ( key, value ) for key, value in { 'history_id': dataset.history_id, 'ext': 'lav', 'name': 'LAJ Output', 'info': 'Added by LAJ', 'dbkey': dataset.dbkey, 'copy_access_from': dataset.id }.items() ] ) ),
                "noseq": "true"
                }
                class_name = "edu.psu.cse.bio.laj.LajApplet.class"
                archive = "/static/laj/laj.jar"
                dataset.peek = create_applet_tag_peek( class_name, archive, params )
            else:
                dataset.peek = "After you add this item to your history, you will be able to launch the LAJ applet."
                dataset.blurb = 'LAJ Multiple Alignment Viewer'
        else:
            dataset.peek = 'file does not exist'
            dataset.blurb = 'file purged from disk'
    def display_peek(self, dataset):
        try:
            return dataset.peek
        except:
            return "peek unavailable"
