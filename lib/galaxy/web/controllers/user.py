"""
Contains the user interface in the Universe class
"""
from galaxy.web.base.controller import *
from galaxy.model.orm import *
from galaxy import util
import logging, os, string, re
from random import choice
from galaxy.web.controllers.forms import get_all_forms
from galaxy.web.form_builder import * 
from galaxy.web.controllers import admin

log = logging.getLogger( __name__ )

require_login_template = """
<h1>Welcome to Galaxy</h1>

<p>
    This installation of Galaxy has been configured such that only users who are logged in may use it.%s
</p>
<p/>
"""
require_login_nocreation_template = require_login_template % ""
require_login_creation_template = require_login_template % "  If you don't already have an account, <a href='%s'>you may create one</a>."

VALID_USERNAME_RE = re.compile( "^[a-z0-9\-]+$" )

class User( BaseController ):

    @web.expose
    def index( self, trans, **kwd ):
        return trans.fill_template( '/user/index.mako', user=trans.get_user() )

    @web.expose
    def change_password(self, trans, old_pass='', new_pass='', conf_pass='', **kwd):
        old_pass_err = new_pass_err = conf_pass_err = ''
        user = trans.get_user()
        if not user:
            trans.response.send_redirect( web.url_for( action='login' ) )
        if trans.request.method == 'POST':
            if not user.check_password( old_pass ):
                old_pass_err = "Invalid password"
            elif len( new_pass ) < 6:
                new_pass_err = "Please use a password of at least 6 characters"
            elif new_pass != conf_pass:
                conf_pass_err = "New passwords do not match."
            else:
                user.set_password_cleartext( new_pass )
                trans.sa_session.add( user )
                trans.sa_session.flush()
                trans.log_event( "User change password" )
                return trans.show_ok_message( "Password has been changed for " + user.email)
        # Generate input form        
        return trans.show_form( 
            web.FormBuilder( web.url_for() , "Change Password", submit_text="Submit" )
                .add_password( "old_pass", "Old Password", value='', error=old_pass_err )
                .add_password( "new_pass", "New Password", value='', error=new_pass_err ) 
                .add_password( "conf_pass", "Confirm Password", value='', error=conf_pass_err ) )
    @web.expose
    def change_email(self, trans, email='', conf_email='', password='', **kwd):
        email_err = conf_email_err = pass_err = ''
        user = trans.get_user()
        if not user:
            trans.response.send_redirect( web.url_for( action='login' ) )
        if trans.request.method == "POST":
            if not user.check_password( password ):
                pass_err = "Invalid password"
            elif len( email ) == 0 or "@" not in email or "." not in email:
                email_err = "Please enter a real email address"
            elif len( email) > 255:
                email_err = "Email address exceeds maximum allowable length"
            elif trans.sa_session.query( trans.app.model.User ).filter_by( email=email ).first():
                email_err = "User with that email already exists"
            elif email != conf_email:
                conf_email_err = "Email addresses do not match."
            else:
                user.email = email
                trans.sa_session.add( user )
                trans.sa_session.flush()
                trans.log_event( "User change email" )
                return trans.show_ok_message( "Email has been changed to: " + user.email, refresh_frames=['masthead', 'history'] )        
        return trans.show_form( 
            web.FormBuilder( web.url_for(), "Change Email", submit_text="Submit" )
                .add_text( "email", "Email", value=email, error=email_err )
                .add_text( "conf_email", "Confirm Email", value='', error=conf_email_err ) 
                .add_password( "password", "Password", value='', error=pass_err ) )
    @web.expose
    def change_username(self, trans, username='', **kwd):
        username_err = ''
        user = trans.get_user()
        if not user:
            trans.response.send_redirect( web.url_for( action='login' ) )
        if trans.request.method == "POST":
            if len( username ) < 4:
                username_err = "Username must be at least 4 characters in length"
            elif len( username ) > 255:
                username_err = "USername must be at most 255 characters in length"
            elif not( VALID_USERNAME_RE.match( username ) ):
                username_err = "Username must contain only letters, numbers, '-', and '_'"
            elif trans.sa_session.query( trans.app.model.User ).filter_by( username=username ).first():
                username_err = "This username is not available"
            else:
                user.username = username
                trans.sa_session.add( user )
                trans.sa_session.flush()
                trans.log_event( "User change username" )
                return trans.show_ok_message( "Username been set to: " + user.username )
        else:
            username = user.username or ''
        return trans.show_form( 
            web.FormBuilder( web.url_for(), "Change username", submit_text="Submit" )
                .add_text( "username", "Username", value=username, error=username_err,
                           help="""Your username is an optional identifier that
                                will be used to generate adresses for information
                                you share publicly. Usernames must be at least
                                four characters in length and contain only lowercase
                                letters, numbers, and the '-' character.""" ) )
    @web.expose
    def login( self, trans, email='', password='' ):
        email_error = password_error = None
        # Attempt login
        if trans.app.config.require_login:
            refresh_frames = [ 'masthead', 'history', 'tools' ]
        else:
            refresh_frames = [ 'masthead', 'history' ]
        if email or password:
            user = trans.sa_session.query( trans.app.model.User ).filter( trans.app.model.User.table.c.email==email ).first()
            if not user:
                email_error = "No such user"
            elif user.deleted:
                email_error = "This account has been marked deleted, contact your Galaxy administrator to restore the account."
            elif user.external:
                email_error = "This account was created for use with an external authentication method, contact your local Galaxy administrator to activate it."
            elif not user.check_password( password ):
                password_error = "Invalid password"
            else:
                trans.handle_user_login( user )
                trans.log_event( "User logged in" )
                msg = "Now logged in as " + user.email + "."
                if trans.app.config.require_login:
                    msg += '  <a href="%s">Click here</a> to continue to the front page.' % web.url_for( '/static/welcome.html' )
                return trans.show_ok_message( msg, refresh_frames=refresh_frames )
        form = web.FormBuilder( web.url_for(), "Login", submit_text="Login" ) \
                .add_text( "email", "Email address", value=email, error=email_error ) \
                .add_password( "password", "Password", value='', error=password_error, 
                                help="<a href='%s'>Forgot password? Reset here</a>" % web.url_for( action='reset_password' ) )
        if trans.app.config.require_login:
            if trans.app.config.allow_user_creation:
                return trans.show_form( form, header = require_login_creation_template % web.url_for( action = 'create' ) )
            else:
                return trans.show_form( form, header = require_login_nocreation_template )
        else:
            return trans.show_form( form )
    @web.expose
    def logout( self, trans ):
        if trans.app.config.require_login:
            refresh_frames = [ 'masthead', 'history', 'tools' ]
        else:
            refresh_frames = [ 'masthead', 'history' ]
        # Since logging an event requires a session, we'll log prior to ending the session
        trans.log_event( "User logged out" )
        trans.handle_user_logout()
        msg = "You are no longer logged in."
        if trans.app.config.require_login:
            msg += '  <a href="%s">Click here</a> to return to the login page.' % web.url_for( controller='user', action='login' )
        return trans.show_ok_message( msg, refresh_frames=refresh_frames )
    @web.expose
    def create( self, trans, **kwd ):
        params = util.Params( kwd )
        email = util.restore_text( params.get('email', '') )
        username = util.restore_text( params.get('username', '') )
        password = util.restore_text( params.get('password', '') )
        confirm = util.restore_text( params.get('confirm', '') )
        subscribe = CheckboxField.is_checked( params.get('subscribe', '') ) 
        admin_view = params.get('admin_view', 'False')
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        if trans.app.config.require_login:
            refresh_frames = [ 'masthead', 'history', 'tools' ]
        else:
            refresh_frames = [ 'masthead', 'history' ]
        if not trans.app.config.allow_user_creation and not trans.user_is_admin():
            return trans.show_error_message( 'User registration is disabled.  Please contact your Galaxy administrator for an account.' )
        # Create the user, save all the user info and login to Galaxy
        if params.get('create_user_button', None) == "Submit":
            # check email and password validity
            error = self.__validate(trans, params, email, password, confirm)
            if error:
                kwd[ 'msg' ] = error
                kwd[ 'messagetype' ] = 'error'
                kwd[ 'create_user_button' ] = None
                return trans.response.send_redirect( web.url_for( controller='user', 
                                                                  action='create',
                                                                  **kwd ) )
            # all the values are valid
            user = trans.app.model.User( email=email )
            user.set_password_cleartext( password )
            user.username = username
            trans.sa_session.add( user )
            trans.sa_session.flush()
            trans.app.security_agent.create_private_user_role( user )
            # We set default user permissions, before we log in and set the default history permissions
            trans.app.security_agent.user_set_default_permissions( user, default_access_private = trans.app.config.new_user_dataset_access_role_default_private )
            # save user info
            self.__save_user_info(trans, user, action='create', new_user=True, **kwd)
            if subscribe:
                mail = os.popen("%s -t" % trans.app.config.sendmail_path, 'w')
                mail.write("To: %s\nFrom: %s\nSubject: Join Mailing List\n\nJoin Mailing list." % (trans.app.config.mailing_join_addr,email) )
                if mail.close():
                    return trans.show_warn_message( "Now logged in as " + user.email+". However, subscribing to the mailing list has failed.", refresh_frames=refresh_frames )
            if admin_view == 'False':
                # The handle_user_login() method has a call to the history_set_default_permissions() method
                # (needed when logging in with a history), user needs to have default permissions set before logging in
                trans.handle_user_login( user )
                trans.log_event( "User created a new account" )
                trans.log_event( "User logged in" )
                # subscribe user to email list
                return trans.show_ok_message( "Now logged in as " + user.email, refresh_frames=refresh_frames )
            else:
                trans.response.send_redirect( web.url_for( controller='admin',
                                                           action='users',
                                                           message='Created new user account (%s)' % user.email,
                                                           status='done' ) )
        else:
            #
            # Show the user registration form
            #
            user_info_select, user_info_form, login_info, widgets = self.__user_info_ui(trans, **kwd)
            return trans.fill_template( '/user/register.mako',
                                        user_info_select=user_info_select,
                                        user_info_form=user_info_form, widgets=widgets, 
                                        login_info=login_info, admin_view=admin_view,
                                        msg=msg, messagetype=messagetype)

    def __save_user_info(self, trans, user, action, new_user=True, **kwd):
        '''
        This method saves the user information for new users as well as editing user
        info for existing users. For new users, the user info form is retrieved from 
        the one that user has selected. And for existing users, the user info form is 
        retrieved from the db.
        '''
        params = util.Params( kwd )
        # get all the user information forms
        user_info_forms = get_all_forms( trans, filter=dict(deleted=False),
                                         form_type=trans.app.model.FormDefinition.types.USER_INFO )
        if new_user:
            # if there are no user forms available then there is nothing to save
            if not len( user_info_forms ):
                return
            user_info_type = params.get( 'user_info_select', 'none'  )
            try:
                user_info_form = trans.sa_session.query( trans.app.model.FormDefinition ).get(int(user_info_type))
            except:
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action=action,
                                                                  msg='Invalid user information form id',
                                                                  messagetype='error') )
        else:
            if user.values:
                user_info_form = user.values.form_definition
            else:
                # user was created before any of the user_info forms were created
                if len(user_info_forms) > 1:
                    # when there are multiple user_info forms and the user or admin
                    # can change the user_info form 
                    user_info_type = params.get( 'user_info_select', 'none'  )
                    try:
                        user_info_form = trans.sa_session.query( trans.app.model.FormDefinition ).get(int(user_info_type))
                    except:
                        return trans.response.send_redirect( web.url_for( controller='user',
                                                                          action=action,
                                                                          msg='Invalid user information form id',
                                                                          messagetype='error') )      
                else:
                    # when there is only one user_info form then there is no way
                    # to change the user_info form 
                    user_info_form = user_info_forms[0]
        values = []
        for index, field in enumerate(user_info_form.fields):
            if field['type'] == 'AddressField':
                value = util.restore_text(params.get('field_%i' % index, ''))
                if value == 'new':
                    # save this new address in the list of this user's addresses
                    user_address = trans.app.model.UserAddress( user=user )
                    user_address.desc = util.restore_text(params.get('field_%i_short_desc' % index, ''))
                    user_address.name = util.restore_text(params.get('field_%i_name' % index, ''))
                    user_address.institution = util.restore_text(params.get('field_%i_institution' % index, ''))
                    user_address.address = util.restore_text(params.get('field_%i_address1' % index, ''))+' '+util.restore_text(params.get('field_%i_address2' % index, ''))
                    user_address.city = util.restore_text(params.get('field_%i_city' % index, ''))
                    user_address.state = util.restore_text(params.get('field_%i_state' % index, ''))
                    user_address.postal_code = util.restore_text(params.get('field_%i_postal_code' % index, ''))
                    user_address.country = util.restore_text(params.get('field_%i_country' % index, ''))
                    user_address.phone = util.restore_text(params.get('field_%i_phone' % index, ''))
                    trans.sa_session.add( user_address )
                    trans.sa_session.flush()
                    trans.sa_session.refresh( user )
                    values.append(int(user_address.id))
                elif value == unicode('none'):
                    values.append('')
                else:
                    values.append(int(value))
            elif field['type'] == 'CheckboxField':
                values.append(CheckboxField.is_checked( params.get('field_%i' % index, '') )) 
            else:
                values.append(util.restore_text(params.get('field_%i' % index, '')))
        if new_user or not user.values:
            # new user or existing 
            form_values = trans.app.model.FormValues(user_info_form, values)
            trans.sa_session.add( form_values )
            trans.sa_session.flush()
            user.values = form_values
        elif user.values:  
            # editing the user info of an existing user with existing user info
            user.values.content = values
            trans.sa_session.add( user.values )
        trans.sa_session.add( user )
        trans.sa_session.flush()
    def __validate_email(self, trans, params, email, user=None):
        error = None
        if user:
            if user.email == email:
                return None 
        if len(email) == 0 or "@" not in email or "." not in email:
            error = "Please enter a real email address"
        elif len(email) > 255:
            error = "Email address exceeds maximum allowable length"
        elif trans.sa_session.query( trans.app.model.User ).filter_by(email=email).all():
            error = "User with that email already exists"
        return error
    def __validate_password(self, trans, params, password, confirm):
        error = None
        if len(password) < 6:
            error = "Please use a password of at least 6 characters"
        elif password != confirm:
            error = "Passwords do not match"
        return error
            
    def __validate(self, trans, params, email, password, confirm):
        error = self.__validate_email(trans, params, email)
        if error:
            return error
        error = self.__validate_password(trans, params, password, confirm)
        if error:
            return error
        if len(get_all_forms( trans, 
                                filter=dict(deleted=False),
                                form_type=trans.app.model.FormDefinition.types.USER_INFO )):
            if params.get('user_info_select', 'none') == 'none':
                return 'Select the user type and the user information'
        return None
    
    def __user_info_ui(self, trans, user=None, **kwd):
        '''
        This method creates the user type select box & user information form widgets 
        and is called during user registration and editing user information.
        If there exists only one user information form then show it after main
        login info. However, if there are more than one user info forms then 
        show a selectbox containing all the forms, then the user can select 
        the one that fits the user's description the most
        '''
        params = util.Params( kwd )
        # get all the user information forms
        user_info_forms = get_all_forms( trans, filter=dict(deleted=False),
                                        form_type=trans.app.model.FormDefinition.types.USER_INFO )
        user_info_select = None
        if user:
            if user.values:
                selected_user_form_id = user.values.form_definition.id
            else:
                selected_user_form_id = params.get( 'user_info_select', 'none'  )
        else:
            selected_user_form_id = params.get( 'user_info_select', 'none'  )
        # when there are more than one user information forms then show a select box
        # list all these forms
        if len(user_info_forms) > 1:
            # create the select box
            user_info_select = SelectField('user_info_select', refresh_on_change=True, 
                                           refresh_on_change_values=[str(u.id) for u in user_info_forms])
            if selected_user_form_id == 'none':
                user_info_select.add_option('Select one', 'none', selected=True)
            else:
                user_info_select.add_option('Select one', 'none')
            for u in user_info_forms:
                if selected_user_form_id == str(u.id):
                    user_info_select.add_option(u.name, u.id, selected=True)
                else:
                    user_info_select.add_option(u.name, u.id)
        # when there is just one user information form the just render that form
        elif len(user_info_forms) == 1:
            selected_user_form_id = user_info_forms[0].id
        # now, create the selected user form widgets starting with the basic 
        # login information 
        if user:
            login_info = { 'Email': TextField( 'email', 40, user.email ),
                           'Public Username': TextField( 'username', 40, user.username ),
                           'Current Password': PasswordField( 'current', 40, '' ),
                           'New Password': PasswordField( 'password', 40, '' ),
                           'Confirm': PasswordField( 'confirm', 40, '' ) }
        else:
            login_info = { 'Email': TextField( 'email', 40, 
                                               util.restore_text( params.get('email', '') ) ),
                           'Public Username': TextField( 'username', 40, 
                                                         util.restore_text( params.get('username', '') ) ),
                           'Password': PasswordField( 'password', 40, 
                                                              util.restore_text( params.get('password', '') ) ),
                           'Confirm': PasswordField( 'confirm', 40, 
                                                     util.restore_text( params.get('confirm', '') ) ),
                           'Subscribe To Mailing List': CheckboxField( 'subscribe', 
                                                                       util.restore_text( params.get('subscribe', '') ) ) }
        # user information
        try:
            user_info_form = trans.sa_session.query( trans.app.model.FormDefinition ).get(int(selected_user_form_id))
        except:
            return user_info_select, None, login_info, None
        if user:
            if user.values:
                widgets = user_info_form.get_widgets(user=user, 
                                                     contents=user.values.content, 
                                                     **kwd)
            else:
                widgets = user_info_form.get_widgets(None, contents=[], **kwd)
        else:
            widgets = user_info_form.get_widgets(None, contents=[], **kwd)
        return user_info_select, user_info_form, login_info, widgets

    @web.expose
    def show_info( self, trans, **kwd ):
        '''
        This method displays the user information page which consists of login 
        information, public username, reset password & other user information 
        obtained during registration
        '''
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        # check if this method is called from the admin perspective,
        if params.get('admin_view', 'False') == 'True':
            try:
                user = trans.sa_session.query( trans.app.model.User ).get( int( params.get( 'user_id', None ) ) )
            except:
                return trans.response.send_redirect( web.url_for( controller='admin',
                                                                  action='users',
                                                                  message='Invalid user',
                                                                  status='error' ) )
            admin_view = True
        else:
            user = trans.user
            admin_view = False
        user_info_select, user_info_form, login_info, widgets = self.__user_info_ui(trans, user, **kwd)
        # user's addresses
        show_filter = util.restore_text( params.get( 'show_filter', 'Active'  ) )
        if show_filter == 'All':
            addresses = [address for address in user.addresses]
        elif show_filter == 'Deleted':
            addresses = [address for address in user.addresses if address.deleted]
        else:
            addresses = [address for address in user.addresses if not address.deleted]
        user_info_forms = get_all_forms( trans, filter=dict(deleted=False),
                                         form_type=trans.app.model.FormDefinition.types.USER_INFO )
        return trans.fill_template( '/user/info.mako', user=user, admin_view=admin_view,
                                    user_info_select=user_info_select,
                                    user_info_form=user_info_form, widgets=widgets, 
                                    login_info=login_info, user_info_forms=user_info_forms,
                                    addresses=addresses, show_filter=show_filter,
                                    msg=msg, messagetype=messagetype)
    @web.expose
    def edit_info( self, trans, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        if params.get('admin_view', 'False') == 'True':
            try:
                user = trans.sa_session.query( trans.app.model.User ).get( int( params.get( 'user_id', None ) ) )
            except:
                return trans.response.send_redirect( web.url_for( controller='admin',
                                                                  action='users',
                                                                  message='Invalid user',
                                                                  status='error' ) )
        else:
            user = trans.user
        #
        # Editing login info (email & username)
        #
        if params.get('login_info_button', None) == 'Save':
            email = util.restore_text( params.get('email', '') )
            username = util.restore_text( params.get('username', '') )
            # validate the new values
            error = self.__validate_email(trans, params, email, user)
            if error:
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  msg=error,
                                                                  messagetype='error') )
            # the new email & username
            user.email = email
            user.username = username
            trans.sa_session.add( user )
            trans.sa_session.flush()
            msg = 'The login information has been updated with the changes'
            if params.get('admin_view', 'False') == 'True':
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  user_id=user.id,
                                                                  admin_view=True,
                                                                  msg=msg,
                                                                  messagetype='done' ) )
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info',
                                                              msg=msg,
                                                              messagetype='done') )
        #
        # Change password 
        #
        elif params.get('change_password_button', None) == 'Save':
            password = util.restore_text( params.get('password', '') )
            confirm = util.restore_text( params.get('confirm', '') )
            # when from the user perspective, validate the current password
            if params.get('admin_view', 'False') == 'False':
                current = util.restore_text( params.get('current', '') )
                if not trans.user.check_password( current ):
                    return trans.response.send_redirect( web.url_for( controller='user',
                                                                      action='show_info',
                                                                      msg='Invalid current password',
                                                                      messagetype='error') )
            # validate the new values
            error = self.__validate_password(trans, params, password, confirm)
            if error:
                if params.get('admin_view', 'False') == 'True':
                    return trans.response.send_redirect( web.url_for( controller='user',
                                                                      action='show_info',
                                                                      user_id=user.id,
                                                                      admin_view=True,
                                                                      msg=error,
                                                                      messagetype='error' ) )
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  msg=error,
                                                                  messagetype='error') )
            # save new password
            user.set_password_cleartext( password )
            trans.sa_session.add( user )
            trans.sa_session.flush()
            trans.log_event( "User change password" )
            msg = 'The password has been changed.'
            if params.get('admin_view', 'False') == 'True':
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  user_id=user.id,
                                                                  admin_view=True,
                                                                  msg=msg,
                                                                  messagetype='done' ) )
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info',
                                                              msg=msg,
                                                              messagetype='done') )
        #
        # Edit user information
        #
        elif params.get('edit_user_info_button', None) == 'Save':
            self.__save_user_info(trans, user, "show_info", new_user=False, **kwd)
            msg = "The user information has been updated with the changes."
            if params.get('admin_view', 'False') == 'True':
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  user_id=user.id,
                                                                  admin_view=True,
                                                                  msg=msg,
                                                                  messagetype='done' ) )
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info',
                                                              msg=msg,
                                                              messagetype='done') )
        else:
            if params.get('admin_view', 'False') == 'True':
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  user_id=user.id,
                                                                  admin_view=True ) )
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info' ) )

    @web.expose
    def reset_password( self, trans, email=None, **kwd ):
        error = ''
        reset_user = trans.sa_session.query( trans.app.model.User ).filter( trans.app.model.User.table.c.email==email ).first()
        user = trans.get_user()
        if reset_user:
            if user and user.id != reset_user.id:
                error = "You may only reset your own password"
            else:
                chars = string.letters + string.digits
                new_pass = ""
                for i in range(15):
                    new_pass = new_pass + choice(chars)
                mail = os.popen("%s -t" % trans.app.config.sendmail_path, 'w')
                mail.write("To: %s\nFrom: no-reply@%s\nSubject: Galaxy Password Reset\n\nYour password has been reset to \"%s\" (no quotes)." % (email, trans.request.remote_addr, new_pass) )
                if mail.close():
                    return trans.show_error_message( 'Failed to reset password.  If this problem persists, please submit a bug report.' )
                reset_user.set_password_cleartext( new_pass )
                trans.sa_session.add( reset_user )
                trans.sa_session.flush()
                trans.log_event( "User reset password: %s" % email )
                return trans.show_ok_message( "Password has been reset and emailed to: %s.  <a href='%s'>Click here</a> to return to the login form." % ( email, web.url_for( action='login' ) ) )
        elif email != None:
            error = "The specified user does not exist"
        elif email is None:
            email = ""
        return trans.show_form( 
            web.FormBuilder( web.url_for(), "Reset Password", submit_text="Submit" )
                .add_text( "email", "Email", value=email, error=error ) )
    @web.expose
    def set_default_permissions( self, trans, **kwd ):
        """Sets the user's default permissions for the new histories"""
        if trans.user:
            if 'update_roles_button' in kwd:
                p = util.Params( kwd )
                permissions = {}
                for k, v in trans.app.model.Dataset.permitted_actions.items():
                    in_roles = p.get( k + '_in', [] )
                    if not isinstance( in_roles, list ):
                        in_roles = [ in_roles ]
                    in_roles = [ trans.sa_session.query( trans.app.model.Role ).get( x ) for x in in_roles ]
                    action = trans.app.security_agent.get_action( v.action ).action
                    permissions[ action ] = in_roles
                trans.app.security_agent.user_set_default_permissions( trans.user, permissions )
                return trans.show_ok_message( 'Default new history permissions have been changed.' )
            return trans.fill_template( 'user/permissions.mako' )
        else:
            # User not logged in, history group must be only public
            return trans.show_error_message( "You must be logged in to change your default permitted actions." )
    @web.expose
    def manage_addresses(self, trans, **kwd):
        if trans.user:
            params = util.Params( kwd )
            msg = util.restore_text( params.get( 'msg', ''  ) )
            messagetype = params.get( 'messagetype', 'done' )
            show_filter = util.restore_text( params.get( 'show_filter', 'Active'  ) )
            if show_filter == 'All':
                addresses = [address for address in trans.user.addresses]
            elif show_filter == 'Deleted':
                addresses = [address for address in trans.user.addresses if address.deleted]
            else:
                addresses = [address for address in trans.user.addresses if not address.deleted]
            return trans.fill_template( 'user/address.mako', 
                                        addresses=addresses,
                                        show_filter=show_filter,
                                        msg=msg,
                                        messagetype=messagetype)
        else:
            # User not logged in, history group must be only public
            return trans.show_error_message( "You must be logged in to change your default permitted actions." )
    @web.expose
    def new_address( self, trans, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        admin_view = params.get( 'admin_view', 'False'  )
        error = ''
        user = trans.sa_session.query( trans.app.model.User ).get( int( params.get( 'user_id', None ) ) )
        if not trans.app.config.allow_user_creation and not trans.user_is_admin():
            return trans.show_error_message( 'User registration is disabled.  Please contact your Galaxy administrator for an account.' )
        if params.get( 'save_new_address_button', None  ) == 'Save':
            if not len( util.restore_text( params.get( 'short_desc', ''  ) ) ):
                error = 'Enter a short description for this address'
            elif not len( util.restore_text( params.get( 'name', ''  ) ) ):
                error = 'Enter the full name'
            elif not len( util.restore_text( params.get( 'institution', ''  ) ) ):
                error = 'Enter the institution associated with the user'
            elif not len ( util.restore_text( params.get( 'address1', ''  ) ) ):
                error = 'Enter the address'
            elif not len( util.restore_text( params.get( 'city', ''  ) ) ):
                error = 'Enter the city'
            elif not len( util.restore_text( params.get( 'state', ''  ) ) ):
                error = 'Enter the state/province/region'
            elif not len( util.restore_text( params.get( 'postal_code', ''  ) ) ):
                error = 'Enter the postal code'
            elif not len( util.restore_text( params.get( 'country', ''  ) ) ):
                error = 'Enter the country'
            else:
                user_address = trans.app.model.UserAddress( user=user )
                user_address.desc = util.restore_text( params.get( 'short_desc', ''  ) )
                user_address.name = util.restore_text( params.get( 'name', ''  ) )
                user_address.institution = util.restore_text( params.get( 'institution', ''  ) )
                user_address.address = util.restore_text( params.get( 'address1', ''  ) )+' '+util.restore_text( params.get( 'address2', ''  ) )
                user_address.city = util.restore_text( params.get( 'city', ''  ) )
                user_address.state = util.restore_text( params.get( 'state', ''  ) )
                user_address.postal_code = util.restore_text( params.get( 'postal_code', ''  ) )
                user_address.country = util.restore_text( params.get( 'country', ''  ) )
                user_address.phone = util.restore_text( params.get( 'phone', ''  ) )
                trans.sa_session.add( user_address )
                trans.sa_session.flush()
                msg = 'Address <b>%s</b> has been added' % user_address.desc
                if admin_view == 'True':
                    return trans.response.send_redirect( web.url_for( controller='user',
                                                                      action='show_info',
                                                                      admin_view=True,
                                                                      user_id=user.id,
                                                                      msg=msg,
                                                                      messagetype='done') )
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  msg=msg,
                                                                  messagetype='done') )
        else:
            # show the address form with the current values filled in
            # create the widgets for each address field
            widgets = []
            widgets.append(dict(label='Short description',
                                widget=TextField( 'short_desc', 40, '' ) ) )
            widgets.append(dict(label='Name',
                                widget=TextField( 'name', 40, '' ) ) )
            widgets.append(dict(label='Institution',
                                widget=TextField( 'institution', 40, '' ) ) )
            widgets.append(dict(label='Address Line 1',
                                widget=TextField( 'address1', 40, '' ) ) )
            widgets.append(dict(label='Address Line 2',
                                widget=TextField( 'address2', 40, '' ) ) )
            widgets.append(dict(label='City',
                                widget=TextField( 'city', 40, '' ) ) )
            widgets.append(dict(label='State',
                                widget=TextField( 'state', 40, '' ) ) )
            widgets.append(dict(label='Postal Code',
                                widget=TextField( 'postal_code', 40, '' ) ) )
            widgets.append(dict(label='Country',
                                widget=TextField( 'country', 40, '' ) ) )
            widgets.append(dict(label='Phone',
                                widget=TextField( 'phone', 40, '' ) ) )
            return trans.fill_template( 'user/new_address.mako', user=user,
                                        admin_view=admin_view,
                                        widgets=widgets, msg=msg, messagetype=messagetype)
    @web.expose
    def edit_address( self, trans, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        admin_view = params.get( 'admin_view', 'False'  )
        error = ''
        user = trans.sa_session.query( trans.app.model.User ).get( int( params.get( 'user_id', None ) ) )
        try:
            user_address = trans.sa_session.query( trans.app.model.UserAddress ).get(int(params.get( 'address_id', None  )))
        except:
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info',
                                                              user_id=user.id,
                                                              admin_view=admin_view,
                                                              msg='Invalid address ID',
                                                              messagetype='error' ) )
        if params.get( 'edit_address_button', None  ) == 'Save changes':
            if not len( util.restore_text( params.get( 'short_desc', ''  ) ) ):
                error = 'Enter a short description for this address'
            elif not len( util.restore_text( params.get( 'name', ''  ) ) ):
                error = 'Enter the full name'
            elif not len( util.restore_text( params.get( 'institution', ''  ) ) ):
                error = 'Enter the institution associated with the user'
            elif not len ( util.restore_text( params.get( 'address1', ''  ) ) ):
                error = 'Enter the address'
            elif not len( util.restore_text( params.get( 'city', ''  ) ) ):
                error = 'Enter the city'
            elif not len( util.restore_text( params.get( 'state', ''  ) ) ):
                error = 'Enter the state/province/region'
            elif not len( util.restore_text( params.get( 'postal_code', ''  ) ) ):
                error = 'Enter the postal code'
            elif not len( util.restore_text( params.get( 'country', ''  ) ) ):
                error = 'Enter the country'
            else:
                user_address.desc = util.restore_text( params.get( 'short_desc', ''  ) )
                user_address.name = util.restore_text( params.get( 'name', ''  ) )
                user_address.institution = util.restore_text( params.get( 'institution', ''  ) )
                user_address.address = util.restore_text( params.get( 'address1', ''  ) )+' '+util.restore_text( params.get( 'address2', ''  ) )
                user_address.city = util.restore_text( params.get( 'city', ''  ) )
                user_address.state = util.restore_text( params.get( 'state', ''  ) )
                user_address.postal_code = util.restore_text( params.get( 'postal_code', ''  ) )
                user_address.country = util.restore_text( params.get( 'country', ''  ) )
                user_address.phone = util.restore_text( params.get( 'phone', ''  ) )
                trans.sa_session.add( user_address )
                trans.sa_session.flush()
                msg = 'Changes made to address <b>%s</b> are saved.' % user_address.desc
                if admin_view == 'True':
                    return trans.response.send_redirect( web.url_for( controller='user',
                                                                      action='show_info',
                                                                      user_id=user.id,
                                                                      admin_view=True,
                                                                      msg=msg,
                                                                      messagetype='done' ) )
                return trans.response.send_redirect( web.url_for( controller='user',
                                                                  action='show_info',
                                                                  msg=msg,
                                                                  messagetype='done') )
        else:
            # show the address form with the current values filled in
            # create the widgets for each address field
            widgets = []
            widgets.append(dict(label='Short description',
                                widget=TextField( 'short_desc', 40, user_address.desc ) ) )
            widgets.append(dict(label='Name',
                                widget=TextField( 'name', 40, user_address.name ) ) )
            widgets.append(dict(label='Institution',
                                widget=TextField( 'institution', 40, user_address.institution ) ) )
            widgets.append(dict(label='Address Line 1',
                                widget=TextField( 'address1', 40, user_address.address ) ) )
            widgets.append(dict(label='Address Line 2',
                                widget=TextField( 'address2', 40, '' ) ) )
            widgets.append(dict(label='City',
                                widget=TextField( 'city', 40, user_address.city ) ) )
            widgets.append(dict(label='State',
                                widget=TextField( 'state', 40, user_address.state ) ) )
            widgets.append(dict(label='Postal Code',
                                widget=TextField( 'postal_code', 40, user_address.postal_code ) ) )
            widgets.append(dict(label='Country',
                                widget=TextField( 'country', 40, user_address.country ) ) )
            widgets.append(dict(label='Phone',
                                widget=TextField( 'phone', 40, user_address.phone ) ) )
            return trans.fill_template( 'user/edit_address.mako', user=user,
                                        address=user_address, admin_view=admin_view,
                                        widgets=widgets, msg=msg, messagetype=messagetype)
    @web.expose
    def delete_address( self, trans, address_id=None, user_id=None, admin_view='False'):
        try:
            user_address = trans.sa_session.query( trans.app.model.UserAddress ).get( int( address_id ) )
        except:
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info',
                                                              user_id=user_id,
                                                              admin_view=admin_view,
                                                              msg='Invalid address ID',
                                                              messagetype='error' ) )
        user_address.deleted = True
        trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='user',
                                                          action='show_info',
                                                          admin_view=admin_view,
                                                          user_id=user_id,
                                                          msg='Address <b>%s</b> deleted' % user_address.desc,
                                                          messagetype='done') )
    @web.expose
    def undelete_address( self, trans, address_id=None, user_id=None, admin_view='False'):
        try:
            user_address = trans.sa_session.query( trans.app.model.UserAddress ).get( int( address_id ) )
        except:
            return trans.response.send_redirect( web.url_for( controller='user',
                                                              action='show_info',
                                                              user_id=user_id,
                                                              admin_view=admin_view,
                                                              msg='Invalid address ID',
                                                              messagetype='error' ) )
        user_address.deleted = False
        trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='user',
                                                          action='show_info',
                                                          admin_view=admin_view,
                                                          user_id=user_id,
                                                          msg='Address <b>%s</b> undeleted' % user_address.desc,
                                                          messagetype='done') )

