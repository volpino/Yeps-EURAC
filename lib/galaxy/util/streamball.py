"""
A simple wrapper for writing tarballs as a stream.
"""

import logging, tarfile

log = logging.getLogger( __name__ )

class StreamBall( object ):
    def __init__( self, mode, members=None ):
        self.members = members
        if members is None:
            self.members = {}
        self.mode = mode
        self.wsgi_status = None
        self.wsgi_headeritems = None
    def add( self, file, relpath ):
        self.members[file] = relpath
    def stream( self, environ, start_response ):
        response_write = start_response( self.wsgi_status, self.wsgi_headeritems )
        class tarfileobj:
            def write( self, *args, **kwargs ):
                response_write( *args, **kwargs )
        tf = tarfile.open( mode=self.mode, fileobj=tarfileobj() )
        for file, rel in self.members.items():
            tf.add( file, arcname=rel )
        tf.close()
        return []
