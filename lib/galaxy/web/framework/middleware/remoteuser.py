"""
Middleware for handling $REMOTE_USER if use_remote_user is enabled.
"""

import socket

errorpage = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html lang="en">
    <head>
        <title>Galaxy</title>
        <style type="text/css">
        body {
            min-width: 500px;
            text-align: center;
        }
        .errormessage {
            font: 75%% verdana, "Bitstream Vera Sans", geneva, arial, helvetica, helve, sans-serif;
            padding: 10px;
            margin: 100px auto;
            min-height: 32px;
            max-width: 500px;
            border: 1px solid #AA6666;
            background-color: #FFCCCC;
            text-align: left;
        }
        </style>
    </head>
    <body>
        <div class="errormessage">
            <h4>%s</h4>
            <p>%s</p>
        </div>
    </body>
</html>
"""

UCSC_MAIN_SERVERS = (
    'hgw1.cse.ucsc.edu',
    'hgw2.cse.ucsc.edu',
    'hgw3.cse.ucsc.edu',
    'hgw4.cse.ucsc.edu',
    'hgw5.cse.ucsc.edu',
    'hgw6.cse.ucsc.edu',
    'hgw7.cse.ucsc.edu',
    'hgw8.cse.ucsc.edu',
)
UCSC_ARCHAEA_SERVERS = (
    'lowepub.cse.ucsc.edu',
)

class RemoteUser( object ):
    def __init__( self, app, maildomain=None, ucsc_display_sites=[] ):
        self.app = app
        self.maildomain = maildomain
        self.allow_ucsc_main = False
        self.allow_ucsc_archaea = False
        if 'main' in ucsc_display_sites or 'test' in ucsc_display_sites:
            self.allow_ucsc_main = True
        if 'archaea' in ucsc_display_sites:
            self.allow_ucsc_archaea = True
    def __call__( self, environ, start_response ):
        # Allow through UCSC if the UCSC display links are enabled
        if ( self.allow_ucsc_main or self.allow_ucsc_archaea ) and environ.has_key( 'REMOTE_ADDR' ):
            try:
                host = socket.gethostbyaddr( environ[ 'REMOTE_ADDR' ] )[0]
            except( socket.error, socket.herror, socket.gaierror, socket.timeout ):
                # in the event of a lookup failure, deny access
                host = None
            if ( self.allow_ucsc_main and host in UCSC_MAIN_SERVERS ) or \
               ( self.allow_ucsc_archaea and host in UCSC_ARCHAEA_SERVERS ):
                environ[ 'HTTP_REMOTE_USER' ] = 'ucsc_browser_display@example.org'
                return self.app( environ, start_response )
        # Apache sets REMOTE_USER to the string '(null)' when using the
        # Rewrite* method for passing REMOTE_USER and a user is
        # un-authenticated.  Any other possible values need to go here as well.
        if environ.has_key( 'HTTP_REMOTE_USER' ) and environ[ 'HTTP_REMOTE_USER' ] != '(null)':
            path_info = environ.get('PATH_INFO', '')
            if path_info.startswith( '/user' ):
                title = "Access to Galaxy user controls is disabled"
                message = """
                    User controls are disabled when Galaxy is configured
                    for external authentication.
                """
                return self.error( start_response, title, message )
            elif not environ[ 'HTTP_REMOTE_USER' ].count( '@' ):
                if self.maildomain is not None:
                    environ[ 'HTTP_REMOTE_USER' ] += '@' + self.maildomain
                else:
                    title = "Access to Galaxy is denied"
                    message = """
                        Galaxy is configured to authenticate users via an external
                        method (such as HTTP authentication in Apache), but only a
                        username (not an email address) was provided by the
                        upstream (proxy) server.  Since Galaxy usernames are email
                        addresses, a default mail domain must be set.</p>
                        <p>Please contact your local Galaxy administrator.  The
                        variable <code>remote_user_maildomain</code> must be set
                        before you may access Galaxy.
                    """
                    return self.error( start_response, title, message )
            return self.app( environ, start_response )
        else:
            title = "Access to Galaxy is denied"
            message = """
                Galaxy is configured to authenticate users via an external
                method (such as HTTP authentication in Apache), but a username
                was not provided by the upstream (proxy) server.  This is
                generally due to a misconfiguration in the upstream server.</p>
                <p>Please contact your local Galaxy administrator.
            """
            return self.error( start_response, title, message )
    def error( self, start_response, title="Access denied", message="Please contact your local Galaxy administrator." ):
        start_response( '403 Forbidden', [('Content-type', 'text/html')] )
        return [errorpage % (title, message)]
