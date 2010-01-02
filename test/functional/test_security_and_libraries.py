import galaxy.model
from galaxy.model.orm import *
from galaxy.model.mapping import context as sa_session
from base.twilltestcase import *

not_logged_in_security_msg = 'You must be logged in as an administrator to access this feature.'
logged_in_security_msg = 'You must be an administrator to access this feature.'

import sys
class TestSecurityAndLibraries( TwillTestCase ):
    def test_000_admin_features_when_not_logged_in( self ):
        """Testing admin_features when not logged in"""
        self.logout()
        self.visit_url( "%s/admin" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/reload_tool?tool_id=upload1" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/roles" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/create_role" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/create_role" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/role" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/groups" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/create_group" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/admin/users" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/library_admin/library" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
        self.visit_url( "%s/library_admin/folder?obj_id=1&new=True" % self.url )
        self.check_page_for_string( not_logged_in_security_msg )
    def test_005_login_as_admin_user( self ):
        """Testing logging in as an admin user test@bx.psu.edu - tests initial settings for DefaultUserPermissions and DefaultHistoryPermissions"""
        self.login( email='test@bx.psu.edu' ) # test@bx.psu.edu is configured as our admin user
        self.visit_page( "admin" )
        self.check_page_for_string( 'Administration' )
        global admin_user
        admin_user = sa_session.query( galaxy.model.User ) \
                               .filter( galaxy.model.User.table.c.email=='test@bx.psu.edu' ) \
                               .first()
        assert admin_user is not None, 'Problem retrieving user with email "test@bx.psu.edu" from the database'
        # Get the admin user's private role for later use
        global admin_user_private_role
        admin_user_private_role = None
        for role in admin_user.all_roles():
            if role.name == admin_user.email and role.description == 'Private Role for %s' % admin_user.email:
                admin_user_private_role = role
                break
        if not admin_user_private_role:
            raise AssertionError( "Private role not found for user '%s'" % admin_user.email )
        # Make sure DefaultUserPermissions are correct
        if len( admin_user.default_permissions ) > 1:
            raise AssertionError( '%d DefaultUserPermissions associated with user %s ( should be 1 )' \
                                  % ( len( admin_user.default_permissions ), admin_user.email ) )
        dup = sa_session.query( galaxy.model.DefaultUserPermissions ) \
                         .filter( galaxy.model.DefaultUserPermissions.table.c.user_id==admin_user.id ) \
                         .first()
        if not dup.action == galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action:
            raise AssertionError( 'The DefaultUserPermission.action for user "%s" is "%s", but it should be "%s"' \
                                  % ( admin_user.email, dup.action, galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action ) )
        # Make sure DefaultHistoryPermissions are correct
        # Logged in as admin_user
        latest_history = sa_session.query( galaxy.model.History ) \
                                   .filter( and_( galaxy.model.History.table.c.deleted==False,
                                                  galaxy.model.History.table.c.user_id==admin_user.id ) ) \
                                   .order_by( desc( galaxy.model.History.table.c.create_time ) ) \
                                   .first()
        if len( latest_history.default_permissions ) > 1:
            raise AssertionError( '%d DefaultHistoryPermissions were created for history id %d when it was created ( should have been 1 )' \
                                  % ( len( latest_history.default_permissions ), latest_history.id ) )
        dhp = sa_session.query( galaxy.model.DefaultHistoryPermissions ) \
                        .filter( galaxy.model.DefaultHistoryPermissions.table.c.history_id==latest_history.id ) \
                        .first()
        if not dhp.action == galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action:
            raise AssertionError( 'The DefaultHistoryPermission.action for history id %d is "%s", but it should be "%s"' \
                                  % ( latest_history.id, dhp.action, galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action ) )
        self.home()
        self.visit_url( "%s/admin/user?id=%s" % ( self.url, self.security.encode_id( admin_user.id ) ) )
        self.check_page_for_string( admin_user.email )
        # Try deleting the admin_user's private role
        check_str = "You cannot eliminate a user's private role association."
        self.associate_roles_and_groups_with_user( self.security.encode_id( admin_user.id ), admin_user.email,
                                                   out_role_ids=str( admin_user_private_role.id ),
                                                   check_str=check_str )
        self.logout()
    def test_010_login_as_regular_user1( self ):
        """Testing logging in as regular user test1@bx.psu.edu - tests private role creation and changing DefaultHistoryPermissions for new histories"""
        # Some of the history related tests here are similar to some tests in the
        # test_history_functions.py script, so we could potentially eliminate 1 or 2 of them.
        self.login( email='test1@bx.psu.edu' ) # test1@bx.psu.edu is not an admin user
        global regular_user1
        regular_user1 = sa_session.query( galaxy.model.User ) \
                                  .filter( galaxy.model.User.table.c.email=='test1@bx.psu.edu' ) \
                                  .first()
        assert regular_user1 is not None, 'Problem retrieving user with email "test1@bx.psu.edu" from the database'
        self.visit_page( "admin" )
        self.check_page_for_string( logged_in_security_msg )
        # Make sure a private role exists for regular_user1
        private_role = None
        for role in regular_user1.all_roles():
            if role.name == regular_user1.email and role.description == 'Private Role for %s' % regular_user1.email:
                private_role = role
                break
        if not private_role:
            raise AssertionError( "Private role not found for user '%s'" % regular_user1.email )
        global regular_user1_private_role
        regular_user1_private_role = private_role
        # Add a dataset to the history
        self.upload_file( '1.bed' )
        latest_dataset = sa_session.query( galaxy.model.Dataset ) \
                                   .order_by( desc( galaxy.model.Dataset.table.c.create_time ) ) \
                                   .first()
        # Make sure DatasetPermissions is correct - default is 'manage permissions'
        if len( latest_dataset.actions ) > 1:
            raise AssertionError( '%d DatasetPermissions were created for dataset id %d when it was created ( should have been 1 )' \
                                  % ( len( latest_dataset.actions ), latest_dataset.id ) )
        dp = sa_session.query( galaxy.model.DatasetPermissions ) \
                       .filter( galaxy.model.DatasetPermissions.table.c.dataset_id==latest_dataset.id ) \
                       .first()
        if not dp.action == galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action:
            raise AssertionError( 'The DatasetPermissions.action for dataset id %d is "%s", but it should be "manage permissions"' \
                                  % ( latest_dataset.id, dp.action ) )
        # Change DefaultHistoryPermissions for regular_user1
        permissions_in = []
        actions_in = []
        for key, value in galaxy.model.Dataset.permitted_actions.items():
            # NOTE: setting the 'access' permission with the private role makes this dataset private
            permissions_in.append( key )
            actions_in.append( value.action )
        # Sort actions for later comparison
        actions_in.sort()
        role_id = str( private_role.id )
        self.user_set_default_permissions( permissions_in=permissions_in, role_id=role_id )
        # Make sure the default permissions are changed for new histories
        self.new_history()
        # logged in as regular_user1
        latest_history = sa_session.query( galaxy.model.History ) \
                                   .filter( and_( galaxy.model.History.table.c.deleted==False,
                                                  galaxy.model.History.table.c.user_id==regular_user1.id ) ) \
                                   .order_by( desc( galaxy.model.History.table.c.create_time ) ) \
                                   .first()
        if len( latest_history.default_permissions ) != len( galaxy.model.Dataset.permitted_actions.items() ):
            raise AssertionError( '%d DefaultHistoryPermissions were created for history id %d, should have been %d' % \
                                  ( len( latest_history.default_permissions ), latest_history.id, len( galaxy.model.Dataset.permitted_actions.items() ) ) )
        dhps = []
        for dhp in latest_history.default_permissions:
            dhps.append( dhp.action )
        # Sort permissions for later comparison
        dhps.sort()
        for key, value in galaxy.model.Dataset.permitted_actions.items():
            if value.action not in dhps:
                raise AssertionError( '%s not in history id %d default_permissions after they were changed' % ( value.action, latest_history.id ) )
        # Add a dataset to the history
        self.upload_file( '1.bed' )
        latest_dataset = sa_session.query( galaxy.model.Dataset ).order_by( desc( galaxy.model.Dataset.table.c.create_time ) ).first()
        # Make sure DatasetPermissionss are correct
        if len( latest_dataset.actions ) != len( latest_history.default_permissions ):
            raise AssertionError( '%d DatasetPermissionss were created for dataset id %d when it was created ( should have been %d )' % \
                                  ( len( latest_dataset.actions ), latest_dataset.id, len( latest_history.default_permissions ) ) )
        dps = []
        for dp in latest_dataset.actions:
            dps.append( dp.action )
        # Sort actions for later comparison
        dps.sort()
        # Compare DatasetPermissions with permissions_in - should be the same
        if dps != actions_in:
            raise AssertionError( 'DatasetPermissionss "%s" for dataset id %d differ from changed default permissions "%s"' \
                                      % ( str( dps ), latest_dataset.id, str( actions_in ) ) )
        # Compare DefaultHistoryPermissions and DatasetPermissionss - should be the same
        if dps != dhps:
                raise AssertionError( 'DatasetPermissionss "%s" for dataset id %d differ from DefaultHistoryPermissions "%s" for history id %d' \
                                      % ( str( dps ), latest_dataset.id, str( dhps ), latest_history.id ) )
        self.logout()

    def test_015_login_as_regular_user2( self ):
        """Testing logging in as regular user test2@bx.psu.edu - tests changing DefaultHistoryPermissions for the current history"""
        email = 'test2@bx.psu.edu'
        self.login( email=email ) # This will not be an admin user
        global regular_user2
        regular_user2 = sa_session.query( galaxy.model.User ) \
                                  .filter( galaxy.model.User.table.c.email==email ) \
                                  .first()
        assert regular_user2 is not None, 'Problem retrieving user with email "" from the database' % email
        # Logged in as regular_user2
        latest_history = sa_session.query( galaxy.model.History ) \
                                   .filter( and_( galaxy.model.History.table.c.deleted==False,
                                                  galaxy.model.History.table.c.user_id==regular_user2.id ) ) \
                                   .order_by( desc( galaxy.model.History.table.c.create_time ) ) \
                                   .first()
        self.upload_file( '1.bed' )
        latest_dataset = sa_session.query( galaxy.model.Dataset ).order_by( desc( galaxy.model.Dataset.table.c.create_time ) ).first()
        permissions_in = [ 'DATASET_MANAGE_PERMISSIONS' ]
        # Make sure these are in sorted order for later comparison
        actions_in = [ 'manage permissions' ]
        permissions_out = [ 'DATASET_ACCESS' ]
        actions_out = [ 'access' ]
        global regular_user2_private_role
        regular_user2_private_role = None
        for role in regular_user2.all_roles():
            if role.name == regular_user2.email and role.description == 'Private Role for %s' % regular_user2.email:
                regular_user2_private_role = role
                break
        if not regular_user2_private_role:
            raise AssertionError( "Private role not found for user '%s'" % regular_user2.email )
        role_id = str( regular_user2_private_role.id )
        # Change DefaultHistoryPermissions for the current history
        self.history_set_default_permissions( permissions_out=permissions_out, permissions_in=permissions_in, role_id=role_id )
        if len( latest_history.default_permissions ) != len( actions_in ):
            raise AssertionError( '%d DefaultHistoryPermissions were created for history id %d, should have been %d' \
                                  % ( len( latest_history.default_permissions ), latest_history.id, len( permissions_in ) ) )
        # Make sure DefaultHistoryPermissions were correctly changed for the current history
        dhps = []
        for dhp in latest_history.default_permissions:
            dhps.append( dhp.action )
        # Sort permissions for later comparison
        dhps.sort()
        # Compare DefaultHistoryPermissions and actions_in - should be the same
        if dhps != actions_in:
            raise AssertionError( 'DefaultHistoryPermissions "%s" for history id %d differ from actions "%s" passed for changing' \
                                      % ( str( dhps ), latest_history.id, str( actions_in ) ) )
        # Make sure DatasetPermissionss are correct
        if len( latest_dataset.actions ) != len( latest_history.default_permissions ):
            raise AssertionError( '%d DatasetPermissionss were created for dataset id %d when it was created ( should have been %d )' \
                                  % ( len( latest_dataset.actions ), latest_dataset.id, len( latest_history.default_permissions ) ) )
        dps = []
        for dp in latest_dataset.actions:
            dps.append( dp.action )
        # Sort actions for comparison
        dps.sort()
        # Compare DatasetPermissionss and DefaultHistoryPermissions - should be the same
        if dps != dhps:
            raise AssertionError( 'DatasetPermissionss "%s" for dataset id %d differ from DefaultHistoryPermissions "%s"' \
                                      % ( str( dps ), latest_dataset.id, str( dhps ) ) )
        self.logout()
    def test_020_create_new_user_account_as_admin( self ):
        """Testing creating a new user account as admin"""
        self.login( email=admin_user.email )
        email = 'test3@bx.psu.edu'
        password = 'testuser'
        previously_created = self.create_new_account_as_admin( email=email, password=password )
        # Get the user object for later tests
        global regular_user3
        regular_user3 = sa_session.query( galaxy.model.User ).filter( galaxy.model.User.table.c.email==email ).first()
        assert regular_user3 is not None, 'Problem retrieving user with email "%s" from the database' % email
        # Make sure DefaultUserPermissions were created
        if not regular_user3.default_permissions:
            raise AssertionError( 'No DefaultUserPermissions were created for user %s when the admin created the account' % email )
        # Make sure a private role was created for the user
        if not regular_user3.roles:
            raise AssertionError( 'No UserRoleAssociations were created for user %s when the admin created the account' % email )
        if not previously_created and len( regular_user3.roles ) != 1:
            raise AssertionError( '%d UserRoleAssociations were created for user %s when the admin created the account ( should have been 1 )' \
                                  % ( len( regular_user3.roles ), regular_user3.email ) )
        for ura in regular_user3.roles:
            role = sa_session.query( galaxy.model.Role ).get( ura.role_id )
            if not previously_created and role.type != 'private':
                raise AssertionError( 'Role created for user %s when the admin created the account is not private, type is' \
                                      % str( role.type ) )
        if not previously_created:
            # Make sure a history was not created ( previous test runs may have left deleted histories )
            histories = sa_session.query( galaxy.model.History ) \
                                  .filter( and_( galaxy.model.History.table.c.user_id==regular_user3.id,
                                           galaxy.model.History.table.c.deleted==False ) ) \
                                  .all()
            if histories:
                raise AssertionError( 'Histories were incorrectly created for user %s when the admin created the account' % email )
            # Make sure the user was not associated with any groups
            if regular_user3.groups:
                raise AssertionError( 'Groups were incorrectly associated with user %s when the admin created the account' % email )
    def test_025_reset_password_as_admin( self ):
        """Testing reseting a user password as admin"""
        email = 'test3@bx.psu.edu'
        self.reset_password_as_admin( user_id=self.security.encode_id( regular_user3.id ), password='testreset' )
        self.logout()
    def test_030_login_after_password_reset( self ):
        """Testing logging in after an admin reset a password - tests DefaultHistoryPermissions for accounts created by an admin"""
        self.login( email='test3@bx.psu.edu', password='testreset' )
        # Make sure a History and HistoryDefaultPermissions exist for the user
        # Logged in as regular_user3
        latest_history = sa_session.query( galaxy.model.History ) \
                                   .filter( and_( galaxy.model.History.table.c.deleted==False,
                                                  galaxy.model.History.table.c.user_id==regular_user3.id ) ) \
                                   .order_by( desc( galaxy.model.History.table.c.create_time ) ) \
                                   .first()
        if not latest_history.user_id == regular_user3.id:
            raise AssertionError( 'A history was not created for user %s when he logged in' % email )
        if not latest_history.default_permissions:
            raise AssertionError( 'No DefaultHistoryPermissions were created for history id %d when it was created' % latest_history.id )
        if len( latest_history.default_permissions ) > 1:
            raise AssertionError( 'More than 1 DefaultHistoryPermissions were created for history id %d when it was created' % latest_history.id )
        dhp =  sa_session.query( galaxy.model.DefaultHistoryPermissions ) \
                         .filter( galaxy.model.DefaultHistoryPermissions.table.c.history_id==latest_history.id ) \
                         .first()
        if not dhp.action == galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action:
            raise AssertionError( 'The DefaultHistoryPermission.action for history id %d is "%s", but it should be "manage permissions"' \
                                  % ( latest_history.id, dhp.action ) )
        # Upload a file to create a HistoryDatasetAssociation
        self.upload_file( '1.bed' )
        latest_dataset = sa_session.query( galaxy.model.Dataset ).order_by( desc( galaxy.model.Dataset.table.c.create_time ) ).first()
        for dp in latest_dataset.actions:
            # Should only have 1 DatasetPermissions
            if dp.action != galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action:
                raise AssertionError( 'The DatasetPermissions for dataset id %d is %s ( should have been %s )' \
                                      % ( latest_dataset.id,
                                          latest_dataset.actions.action, 
                                          galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action ) )
        self.logout()
        # Reset the password to the default for later tests
        self.login( email='test@bx.psu.edu' )
        self.reset_password_as_admin( user_id=self.security.encode_id( regular_user3.id ), password='testuser' )
    def test_035_mark_user_deleted( self ):
        """Testing marking a user account as deleted"""
        self.mark_user_deleted( user_id=self.security.encode_id( regular_user3.id ), email=regular_user3.email )
        # Deleting a user should not delete any associations
        sa_session.refresh( regular_user3 )
        if not regular_user3.active_histories:
            raise AssertionError( 'HistoryDatasetAssociations for regular_user3 were incorrectly deleted when the user was marked deleted' )
    def test_040_undelete_user( self ):
        """Testing undeleting a user account"""
        self.undelete_user( user_id=self.security.encode_id( regular_user3.id ), email=regular_user3.email )
    def test_045_create_role( self ):
        """Testing creating new role with 3 members ( and a new group named the same ), then renaming the role"""
        name = 'Role One'
        description = "This is Role Ones description"
        user_ids=[ str( admin_user.id ), str( regular_user1.id ), str( regular_user3.id ) ]
        self.create_role( name=name,
                          description=description,
                          in_user_ids=user_ids,
                          in_group_ids=[],
                          create_group_for_role='yes',
                          private_role=admin_user.email )
        # Get the role object for later tests
        global role_one
        role_one = sa_session.query( galaxy.model.Role ).filter( galaxy.model.Role.table.c.name==name ).first()
        assert role_one is not None, 'Problem retrieving role named "Role One" from the database'
        # Make sure UserRoleAssociations are correct
        if len( role_one.users ) != len( user_ids ):
            raise AssertionError( '%d UserRoleAssociations were created for role id %d when it was created ( should have been %d )' \
                                  % ( len( role_one.users ), role_one.id, len( user_ids ) ) )
        # Each of the following users should now have 2 role associations, their private role and role_one
        for user in [ admin_user, regular_user1, regular_user3 ]:
            sa_session.refresh( user )
            if len( user.roles ) != 2:
                raise AssertionError( '%d UserRoleAssociations are associated with user %s ( should be 2 )' \
                                      % ( len( user.roles ), user.email ) )
        # Make sure the group was created
        self.home()
        self.visit_page( 'admin/groups' )
        self.check_page_for_string( name )
        global group_zero
        group_zero = sa_session.query( galaxy.model.Group ).filter( galaxy.model.Group.table.c.name==name ).first()
        # Rename the role
        rename = "Role One's been Renamed"
        redescription="This is Role One's Re-described"
        self.rename_role( self.security.encode_id( role_one.id ), name=rename, description=redescription )
        self.home()
        self.visit_page( 'admin/roles' )
        self.check_page_for_string( rename )
        self.check_page_for_string( redescription )
        # Reset the role back to the original name and description
        self.rename_role( self.security.encode_id( role_one.id ), name=name, description=description )
    def test_050_create_group( self ):
        """Testing creating new group with 3 members and 1 associated role, then renaming it"""
        name = "Group One's Name"
        user_ids=[ str( admin_user.id ), str( regular_user1.id ), str( regular_user3.id ) ]
        role_ids=[ str( role_one.id ) ]
        self.create_group( name=name, in_user_ids=user_ids, in_role_ids=role_ids )
        # Get the group object for later tests
        global group_one
        group_one = sa_session.query( galaxy.model.Group ).filter( galaxy.model.Group.table.c.name==name ).first()
        assert group_one is not None, 'Problem retrieving group named "Group One" from the database'
        # Make sure UserGroupAssociations are correct
        if len( group_one.users ) != len( user_ids ):
            raise AssertionError( '%d UserGroupAssociations were created for group id %d when it was created ( should have been %d )' \
                                  % ( len( group_one.users ), group_one.id, len( user_ids ) ) )
        # Each user should now have 1 group association, group_one
        for user in [ admin_user, regular_user1, regular_user3 ]:
            sa_session.refresh( user )
            if len( user.groups ) != 1:
                raise AssertionError( '%d UserGroupAssociations are associated with user %s ( should be 1 )' % ( len( user.groups ), user.email ) )
        # Make sure GroupRoleAssociations are correct
        if len( group_one.roles ) != len( role_ids ):
            raise AssertionError( '%d GroupRoleAssociations were created for group id %d when it was created ( should have been %d )' \
                                  % ( len( group_one.roles ), group_one.id, len( role_ids ) ) )
        # Rename the group
        rename = "Group One's been Renamed"
        self.rename_group( self.security.encode_id( group_one.id ), name=rename, )
        self.home()
        self.visit_page( 'admin/groups' )
        self.check_page_for_string( rename )
        # Reset the group back to the original name
        self.rename_group( self.security.encode_id( group_one.id ), name=name )
    def test_055_add_members_and_role_to_group( self ):
        """Testing editing user membership and role associations of an existing group"""
        name = 'Group Two'
        self.create_group( name=name, in_user_ids=[], in_role_ids=[] )
        # Get the group object for later tests
        global group_two
        group_two = sa_session.query( galaxy.model.Group ).filter( galaxy.model.Group.table.c.name==name ).first()
        assert group_two is not None, 'Problem retrieving group named "Group Two" from the database'
        # group_two should have no associations
        if group_two.users:
            raise AssertionError( '%d UserGroupAssociations were created for group id %d when it was created ( should have been 0 )' \
                              % ( len( group_two.users ), group_two.id ) )
        if group_two.roles:
            raise AssertionError( '%d GroupRoleAssociations were created for group id %d when it was created ( should have been 0 )' \
                              % ( len( group_two.roles ), group_two.id ) )
        user_ids = [ str( regular_user1.id )  ]
        role_ids = [ str( role_one.id ) ]
        self.associate_users_and_roles_with_group( self.security.encode_id( group_two.id ),
                                                   group_two.name,
                                                   user_ids=user_ids,
                                                   role_ids=role_ids )
    def test_060_create_role_with_user_and_group_associations( self ):
        """Testing creating a role with user and group associations"""
        # NOTE: To get this to work with twill, all select lists on the ~/admin/role page must contain at least
        # 1 option value or twill throws an exception, which is: ParseError: OPTION outside of SELECT
        # Due to this bug in twill, we create the role, we bypass the page and visit the URL in the
        # associate_users_and_groups_with_role() method.
        name = 'Role Two'
        description = 'This is Role Two'
        user_ids=[ str( admin_user.id ) ]
        group_ids=[ str( group_two.id ) ]
        private_role=admin_user.email
        # Create the role
        self.create_role( name=name,
                          description=description,
                          in_user_ids=user_ids,
                          in_group_ids=group_ids,
                          private_role=private_role )
        # Get the role object for later tests
        global role_two
        role_two = sa_session.query( galaxy.model.Role ).filter( galaxy.model.Role.table.c.name==name ).first()
        assert role_two is not None, 'Problem retrieving role named "Role Two" from the database'
        # Make sure UserRoleAssociations are correct
        if len( role_two.users ) != len( user_ids ):
            raise AssertionError( '%d UserRoleAssociations were created for role id %d when it was created with %d members' \
                                  % ( len( role_two.users ), role_two.id, len( user_ids ) ) )
        # admin_user should now have 3 role associations, private role, role_one, role_two
        sa_session.refresh( admin_user )
        if len( admin_user.roles ) != 3:
            raise AssertionError( '%d UserRoleAssociations are associated with user %s ( should be 3 )' % ( len( admin_user.roles ), admin_user.email ) )
        # Make sure GroupRoleAssociations are correct
        sa_session.refresh( role_two )
        if len( role_two.groups ) != len( group_ids ):
            raise AssertionError( '%d GroupRoleAssociations were created for role id %d when it was created ( should have been %d )' \
                                  % ( len( role_two.groups ), role_two.id, len( group_ids ) ) )
        # group_two should now be associated with 2 roles: role_one, role_two
        sa_session.refresh( group_two )
        if len( group_two.roles ) != 2:
            raise AssertionError( '%d GroupRoleAssociations are associated with group id %d ( should be 2 )' % ( len( group_two.roles ), group_two.id ) )
    def test_065_change_user_role_associations( self ):
        """Testing changing roles associated with a user"""
        # Create a new role with no associations
        name = 'Role Three'
        description = 'This is Role Three'
        user_ids=[]
        group_ids=[]
        private_role=admin_user.email
        self.create_role( name=name,
                          description=description,
                          in_user_ids=user_ids,
                          in_group_ids=group_ids,
                          private_role=private_role )
        # Get the role object for later tests
        global role_three
        role_three = sa_session.query( galaxy.model.Role ).filter( galaxy.model.Role.table.c.name==name ).first()
        assert role_three is not None, 'Problem retrieving role named "Role Three" from the database'
        # Associate the role with a user
        sa_session.refresh( admin_user )
        role_ids = []
        for ura in admin_user.non_private_roles:
            role_ids.append( str( ura.role_id ) )
        role_ids.append( str( role_three.id ) )
        group_ids = []
        for uga in admin_user.groups:
            group_ids.append( str( uga.group_id ) )
        check_str = "User '%s' has been updated with %d associated roles and %d associated groups" % ( admin_user.email, len( role_ids ), len( group_ids ) )
        self.associate_roles_and_groups_with_user( self.security.encode_id( admin_user.id ),
                                                   str( admin_user.email ),
                                                   in_role_ids=role_ids,
                                                   in_group_ids=group_ids,
                                                   check_str=check_str )
        sa_session.refresh( admin_user )
        # admin_user should now be associated with 4 roles: private, role_one, role_two, role_three
        if len( admin_user.roles ) != 4:
            raise AssertionError( '%d UserRoleAssociations are associated with %s ( should be 4 )' % ( len( admin_user.roles ), admin_user.email ) )
    def test_070_create_library( self ):
        """Testing creating a new library, then renaming it"""
        name = "Library One's Name"
        description = "This is Library One's description"
        self.create_library( name=name, description=description )
        self.visit_page( 'library_admin/browse_libraries' )
        self.check_page_for_string( name )
        self.check_page_for_string( description )
        # Get the library object for later tests
        global library_one
        library_one = sa_session.query( galaxy.model.Library ) \
                                .filter( and_( galaxy.model.Library.table.c.name==name,
                                               galaxy.model.Library.table.c.description==description,
                                               galaxy.model.Library.table.c.deleted==False ) ) \
                                .first()
        assert library_one is not None, 'Problem retrieving library named "%s" from the database' % name
        # Set permissions on the library, sort for later testing
        permissions_in = [ k for k, v in galaxy.model.Library.permitted_actions.items() ]
        permissions_out = []
        # Role one members are: admin_user, regular_user1, regular_user3.  Each of these users will be permitted to
        # LIBRARY_ADD, LIBRARY_MODIFY, LIBRARY_MANAGE for library items.
        self.set_library_permissions( str( library_one.id ), library_one.name, str( role_one.id ), permissions_in, permissions_out )                                            
        # Rename the library
        rename = "Library One's been Renamed"
        redescription = "This is Library One's Re-described"
        self.rename_library( str( library_one.id ), library_one.name, name=rename, description=redescription )
        self.home()
        self.visit_page( 'library_admin/browse_libraries' )
        self.check_page_for_string( rename )
        self.check_page_for_string( redescription )
        # Reset the library back to the original name and description
        sa_session.refresh( library_one )
        self.rename_library( str( library_one.id ), library_one.name, name=name, description=description )
        sa_session.refresh( library_one )
    def test_075_library_template_features( self ):
        """Testing adding a template to a library, then filling in the contents"""
        # Make sure a form exists
        form_name = 'Library template Form One'
        form_desc = 'This is Form One'
        form_type = galaxy.model.FormDefinition.types.LIBRARY_INFO_TEMPLATE
        self.create_form( name=form_name, desc=form_desc, formtype=form_type )
        global form_one
        form_one = None
        fdcs = sa_session.query( galaxy.model.FormDefinitionCurrent ) \
                         .filter( galaxy.model.FormDefinitionCurrent.table.c.deleted==False ) \
                         .order_by( galaxy.model.FormDefinitionCurrent.table.c.create_time.desc() )
        for fdc in fdcs:
            if form_name == fdc.latest_form.name and form_type == fdc.latest_form.type:
                form_one = fdc.latest_form
                break
        assert form_one is not None, 'Problem retrieving form named (%s) from the database' % form_name
        # Add a new information template to the library
        template_name = 'Library Template 1'
        self.add_library_info_template( 'library_admin',
                                        str( library_one.id ),
                                        str( form_one.id ),
                                        form_one.name )
        # Make sure the template fields are displayed on the library information page
        field_dict = form_one.fields[ 0 ]
        global form_one_field_label
        form_one_field_label = '%s' % str( field_dict.get( 'label', 'Field 0' ) )
        global form_one_field_help
        form_one_field_help = '%s' % str( field_dict.get( 'helptext', 'Field 0 help' ) )
        global form_one_field_required
        form_one_field_required = '%s' % str( field_dict.get( 'required', 'optional' ) ).capitalize()
        # Add information to the library using the template
        global form_one_field_name
        form_one_field_name = 'field_0'
        contents = '%s library contents' % form_one_field_label
        self.visit_url( '%s/library_admin/library?obj_id=%s&information=True' % ( self.url, str( library_one.id ) ) )
        # There are 2 forms on this page and the template is the 2nd form
        tc.fv( '2', form_one_field_name, contents )
        tc.submit( 'edit_info_button' )
        # For some reason, the following check:
        # self.check_page_for_string ( 'The information has been updated.' )
        # ...throws the following exception - I have not idea why!
        # TypeError: 'str' object is not callable
        # The work-around is to not make ANY self.check_page_for_string() calls until the next method
    def test_080_edit_template_contents_admin_view( self ):
        """Test editing template contents on the admin side"""
        # First make sure the templlate contents from the previous method were correctly saved
        contents = '%s library contents' % form_one_field_label
        contents_edited = contents + ' edited'
        self.visit_url( '%s/library_admin/library?obj_id=%s&information=True' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( contents )
        # Edit the contents and then save them
        tc.fv( '2', form_one_field_name, contents_edited )
        tc.submit( 'edit_info_button' )
        self.check_page_for_string( 'The information has been updated.' )
        self.check_page_for_string( contents_edited )
    def test_085_add_public_dataset_to_root_folder( self ):
        """Testing adding a public dataset to the root folder, making sure library template is inherited"""
        actions = [ v.action for k, v in galaxy.model.Library.permitted_actions.items() ]
        actions.sort()
        message = 'Testing adding a public dataset to the root folder'
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for root folder 1.bed" % form_one_field_label
        self.add_library_dataset( 'library_admin',
                                  '1.bed',
                                  str( library_one.id ),
                                  str( library_one.root_folder.id ),
                                  library_one.root_folder.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  message=message.replace( ' ', '+' ),
                                  root=True,
                                  template_field_name1=form_one_field_name,
                                  template_field_contents1=template_contents )
        global ldda_one
        ldda_one = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                             .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                             .first()
        assert ldda_one is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_one from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "1.bed" )
        self.check_page_for_string( message )
        self.check_page_for_string( admin_user.email )
        # Make sure the library permissions were inherited to the library_dataset_dataset_association
        ldda_permissions = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociationPermissions ) \
                                     .filter( galaxy.model.LibraryDatasetDatasetAssociationPermissions.table.c.library_dataset_dataset_association_id == ldda_one.id ) \
                                     .all()
        ldda_permissions = [ lddap_obj.action for lddap_obj in ldda_permissions ]
        ldda_permissions.sort()
        assert actions == ldda_permissions, "Permissions for ldda id %s not correctly inherited from library %s" \
                            % ( ldda_one.id, library_one.name )
        # Make sure DatasetPermissions are correct - default is 'manage permissions'
        if len( ldda_one.dataset.actions ) > 1:
            raise AssertionError( '%d DatasetPermissionss were created for dataset id %d when it was created ( should have been 1 )' \
                                  % ( len( ldda_one.dataset.actions ), ldda_one.dataset.id ) )
        dp = sa_session.query( galaxy.model.DatasetPermissions ).filter( galaxy.model.DatasetPermissions.table.c.dataset_id==ldda_one.dataset.id ).first()
        if not dp.action == galaxy.model.Dataset.permitted_actions.DATASET_MANAGE_PERMISSIONS.action:
            raise AssertionError( 'The DatasetPermissions.action for dataset id %d is "%s", but it should be "manage permissions"' \
                                  % ( ldda_one.dataset.id, dp.action ) )
        # Make sure the library template contents were correctly saved
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( library_one.root_folder.id ), str( ldda_one.id ) ) )
        self.check_page_for_string( template_contents )
        # Make sure other users can access the dataset from the Libraries view
        self.logout()
        self.login( email=regular_user2.email )
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "1.bed" )
        self.logout()
        self.login( email=admin_user.email )
        self.home()
    def test_090_add_new_folder_to_root_folder( self ):
        """Testing adding a folder to a library root folder"""
        root_folder = library_one.root_folder
        name = "Root Folder's Folder One"
        description = "This is the root folder's Folder One"
        self.add_folder( 'library_admin',
                         str( library_one.id ),
                         str( root_folder.id ),
                         name=name,
                         description=description )
        global folder_one
        folder_one = sa_session.query( galaxy.model.LibraryFolder ) \
                               .filter( and_( galaxy.model.LibraryFolder.table.c.parent_id==root_folder.id,
                                              galaxy.model.LibraryFolder.table.c.name==name,
                                              galaxy.model.LibraryFolder.table.c.description==description ) ) \
                               .first()
        assert folder_one is not None, 'Problem retrieving library folder named "%s" from the database' % name
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( name )
        self.check_page_for_string( description )
        self.home()
        self.visit_url( '%s/library_admin/folder?obj_id=%s&library_id=%s&information=True' % ( self.url, str( folder_one.id ), str( library_one.id ) ) )
        # Make sure the template was inherited
        self.check_page_for_string( form_one_field_name )
        # Make sure the template contents were NOT inherited
        contents = '%s library contents' % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Library level template contents were displayed in the folders inherited template fields"
        except:
            pass
        # Add contents to the inherited template
        template_contents = "%s contents for Folder One" % form_one_field_label
        # There are 2 forms on this page and the template is the 2nd form
        tc.fv( '2', form_one_field_name, template_contents )
        tc.submit( 'edit_info_button' )
        self.check_page_for_string( 'The information has been updated.' )
        self.check_page_for_string( template_contents )
    def test_095_add_subfolder_to_folder( self ):
        """Testing adding a folder to a library folder"""
        name = "Folder One's Subfolder"
        description = "This is the Folder One's subfolder"
        self.add_folder( 'library_admin', str( library_one.id ), str( folder_one.id ), name=name, description=description )
        global subfolder_one
        subfolder_one = sa_session.query( galaxy.model.LibraryFolder ) \
                                  .filter( and_( galaxy.model.LibraryFolder.table.c.parent_id==folder_one.id,
                                                 galaxy.model.LibraryFolder.table.c.name==name,
                                                 galaxy.model.LibraryFolder.table.c.description==description ) ) \
                                  .first()
        assert subfolder_one is not None, 'Problem retrieving library folder named "Folder Ones Subfolder" from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( name )
        self.check_page_for_string( description )
        self.home()
        self.visit_url( '%s/library_admin/folder?obj_id=%s&library_id=%s&information=True' % ( self.url, str( subfolder_one.id ), str( library_one.id ) ) )
        # Make sure the template was inherited
        self.check_page_for_string( form_one_field_name )
        # Make sure the template contents were NOT inherited
        contents = "%s contents for Folder One" % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Parent folder level template contents were displayed in the sub-folders inherited template fields"
        except:
            pass
        # Add contents to the inherited template
        template_contents = "%s contents for Folder One's Subfolder" % form_one_field_label
        # There are 2 forms on this page and the template is the 2nd form
        tc.fv( '2', form_one_field_name, template_contents )
        tc.submit( 'edit_info_button' )
        self.check_page_for_string( 'The information has been updated.' )
        self.check_page_for_string( template_contents )
    def test_100_add_2nd_new_folder_to_root_folder( self ):
        """Testing adding a 2nd folder to a library root folder"""
        root_folder = library_one.root_folder
        name = "Folder Two"
        description = "This is the root folder's Folder Two"
        self.add_folder( 'library_admin', str( library_one.id ), str( root_folder.id ), name=name, description=description )
        global folder_two
        folder_two = sa_session.query( galaxy.model.LibraryFolder ) \
                               .filter( and_( galaxy.model.LibraryFolder.table.c.parent_id==root_folder.id,
                                              galaxy.model.LibraryFolder.table.c.name==name,
                                              galaxy.model.LibraryFolder.table.c.description==description ) ) \
                               .first()
        assert folder_two is not None, 'Problem retrieving library folder named "%s" from the database' % name
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( name )
        self.check_page_for_string( description )
        self.home()
        self.visit_url( '%s/library_admin/folder?obj_id=%s&library_id=%s&information=True' % ( self.url, str( subfolder_one.id ), str( library_one.id ) ) )
        # Make sure the template was inherited
        self.check_page_for_string( form_one_field_name )
        # Make sure the template contents were NOT inherited
        contents = '%s library contents' % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Parent folder level template contents were displayed in the sub-folders inherited template fields"
        except:
            pass
    def test_105_add_public_dataset_to_root_folders_2nd_subfolder( self ):
        """Testing adding a public dataset to the root folder's 2nd sub-folder"""
        actions = [ v.action for k, v in galaxy.model.Library.permitted_actions.items() ]
        actions.sort()
        message = "Testing adding a public dataset to the folder named %s" % folder_two.name
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for %s 2.bed" % ( form_one_field_label, folder_two.name )
        self.add_library_dataset( 'library_admin',
                                  '2.bed',
                                  str( library_one.id ),
                                  str( folder_two.id ),
                                  folder_two.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  message=message.replace( ' ', '+' ),
                                  root=False,
                                  template_field_name1=form_one_field_name,
                                  template_field_contents1=template_contents )
        global ldda_two
        ldda_two = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                             .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                             .first()
        assert ldda_two is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_two from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "2.bed" )
        self.check_page_for_string( message )
        self.check_page_for_string( admin_user.email )
        # Make sure the library template contents were correctly saved
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( folder_two.id ), str( ldda_two.id ) ) )
        self.check_page_for_string( template_contents )
    def test_110_add_2nd_public_dataset_to_root_folders_2nd_subfolder( self ):
        """Testing adding a 2nd public dataset to the root folder's 2nd sub-folder"""
        actions = [ v.action for k, v in galaxy.model.Library.permitted_actions.items() ]
        actions.sort()
        message = "Testing adding a 2nd public dataset to the folder named %s" % folder_two.name
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for %s 3.bed" % ( form_one_field_label, folder_two.name )
        self.add_library_dataset( 'library_admin',
                                  '3.bed',
                                  str( library_one.id ),
                                  str( folder_two.id ),
                                  folder_two.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  message=message.replace( ' ', '+' ),
                                  root=False,
                                  template_field_name1=form_one_field_name,
                                  template_field_contents1=template_contents )
        global ldda_three
        ldda_three = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                               .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                               .first()
        assert ldda_three is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_three from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "3.bed" )
        self.check_page_for_string( message )
        self.check_page_for_string( admin_user.email )
        # Make sure the library template contents were correctly saved
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( folder_two.id ), str( ldda_three.id ) ) )
        self.check_page_for_string( template_contents )
    def test_115_add_dataset_with_private_role_restriction_to_folder( self ):
        """Testing adding a dataset with a private role restriction to a folder"""
        # Add a dataset restricted by the following:
        # DATASET_MANAGE_PERMISSIONS = "test@bx.psu.edu" via DefaultUserPermissions
        # DATASET_ACCESS = "regular_user1" private role via this test method
        # LIBRARY_ADD = "Role One" via inheritance from parent folder
        # LIBRARY_MODIFY = "Role One" via inheritance from parent folder
        # LIBRARY_MANAGE = "Role One" via inheritance from parent folder
        # "Role One" members are: test@bx.psu.edu, test1@bx.psu.edu, test3@bx.psu.edu
        # This means that only user test1@bx.psu.edu can see the dataset from the Libraries view
        #
        # TODO: this demonstrates a weakness in our logic:  If test@bx.psu.edu cannot
        # access the dataset from the Libraries view, then the DATASET_MANAGE_PERMISSIONS
        # setting is useless if test@bx.psu.edu is not an admin.  This should be corrected,
        # by displaying a warning message on the permissions form.
        message ='This is a test of the fourth dataset uploaded'
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for %s 4.bed" % ( form_one_field_label, folder_one.name )
        self.add_library_dataset( 'library_admin',
                                  '4.bed',
                                  str( library_one.id ),
                                  str( folder_one.id ),
                                  folder_one.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  roles=[ str( regular_user1_private_role.id ) ],
                                  message=message.replace( ' ', '+' ),
                                  root=False,
                                  template_field_name1=form_one_field_name,
                                  template_field_contents1=template_contents )
        global ldda_four
        ldda_four = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                              .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                              .first()
        assert ldda_four is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_four from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "4.bed" )
        self.check_page_for_string( message )
        self.check_page_for_string( admin_user.email )
        self.home()
        # Make sure the library template contents were correctly saved
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( folder_one.id ), str( ldda_four.id ) ) )
        self.check_page_for_string( template_contents )
    def test_120_accessing_dataset_with_private_role_restriction( self ):
        """Testing accessing a dataset with a private role restriction"""
        # admin_user should not be able to see 2.bed from the analysis view's access libraries
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        try:
            self.check_page_for_string( folder_one.name )
            raise AssertionError( '%s can see library folder %s when it contains only datasets restricted by role %s' \
                                  % ( admin_user.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        try:
            self.check_page_for_string( '4.bed' )
            raise AssertionError( '%s can see dataset 4.bed in library folder %s when it was restricted by role %s' \
                                  % ( admin_user.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        self.logout()
        # regular_user1 should be able to see 4.bed from the analysis view's access librarys
        # since it was associated with regular_user1's private role
        self.login( email='test1@bx.psu.edu' )
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( folder_one.name )
        self.check_page_for_string( '4.bed' )
        self.logout()
        # regular_user2 should not be able to see 1.bed from the analysis view's access librarys
        self.login( email='test2@bx.psu.edu' )
        try:
            self.check_page_for_string( folder_one.name )
            raise AssertionError( '%s can see library folder %s when it contains only datasets restricted by role %s' \
                                  % ( regular_user2.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        try:
            self.check_page_for_string( '4.bed' )
            raise AssertionError( '%s can see dataset 4.bed in library folder %s when it was restricted by role %s' \
                                  % ( regular_user2.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        self.logout()
        # regular_user3 should not be able to see 2.bed from the analysis view's access librarys
        self.login( email='test3@bx.psu.edu' )
        try:
            self.check_page_for_string( folder_one.name )
            raise AssertionError( '%s can see library folder %s when it contains only datasets restricted by role %s' \
                                  % ( regular_user3.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        try:
            self.check_page_for_string( '4.bed' )
            raise AssertionError( '%s can see dataset 4.bed in library folder %s when it was restricted by role %s' \
                                  % ( regular_user3.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass # This is the behavior we want
        self.logout()
        self.login( email=admin_user.email )
        self.home()
    def test_125_change_dataset_access_permission( self ):
        """Testing changing the access permission on a dataset with a private role restriction"""
        # We need admin_user to be able to access 2.bed
        permissions_in = [ k for k, v in galaxy.model.Dataset.permitted_actions.items() ] + \
                         [ k for k, v in galaxy.model.Library.permitted_actions.items() ]
        permissions_out = []
        role_ids_str = '%s,%s' % ( str( role_one.id ), str( admin_user_private_role.id ) )
        self.set_library_dataset_permissions( str( library_one.id ), str( folder_one.id ), str( ldda_four.id ), ldda_four.name,
                                              role_ids_str, permissions_in, permissions_out )
        # admin_user should now be able to see 4.bed from the analysis view's access libraries
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( ldda_four.name )
        self.home()
    def test_130_add_dataset_with_role_associated_with_group_and_users( self ):
        """Testing adding a dataset with a role that is associated with a group and users"""
        self.login( email='test@bx.psu.edu' )
        # Add a dataset restricted by role_two, which is currently associated as follows:
        # groups: group_two
        # users: test@bx.psu.edu, test1@bx.psu.edu via group_two
        message = 'Testing adding a dataset with a role that is associated with a group and users'
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for %s 5.bed" % ( form_one_field_label, folder_one.name )
        self.add_library_dataset( 'library_admin',
                                  '5.bed',
                                  str( library_one.id ),
                                  str( folder_one.id ),
                                  folder_one.name,
                                  file_type='bed',
                                  dbkey='hg17',
                                  roles=[ str( role_two.id ) ],
                                  message=message.replace( ' ', '+' ),
                                  root=False,
                                  template_field_name1=form_one_field_name,
                                  template_field_contents1=template_contents )
        global ldda_five
        ldda_five = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                              .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                              .first()
        assert ldda_five is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_five from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "5.bed" )
        self.check_page_for_string( message )
        self.check_page_for_string( admin_user.email )
        self.home()
        # Make sure the library template contents were correctly saved
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( folder_one.id ), str( ldda_five.id ) ) )
        self.check_page_for_string( template_contents )
    def test_135_accessing_dataset_with_role_associated_with_group_and_users( self ):
        """Testing accessing a dataset with a role that is associated with a group and users"""
        # admin_user should be able to see 5.bed since she is associated with role_two
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( "5.bed" )
        self.check_page_for_string( admin_user.email )
        self.logout()
        # regular_user1 should be able to see 5.bed since she is associated with group_two
        self.login( email = 'test1@bx.psu.edu' )
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( folder_one.name )
        self.check_page_for_string( '5.bed' )
        self.check_page_for_string( admin_user.email )
        # Check the permissions on the dataset 5.bed - they are as folows:
        # DATASET_MANAGE_PERMISSIONS = test@bx.psu.edu
        # DATASET_ACCESS = Role Two
        #                  Role Two associations: test@bx.psu.edu and Group Two
        #                  Group Two members: Role One, Role Two, test1@bx.psu.edu
        #                  Role One associations: test@bx.psu.edu, test1@bx.psu.edu, test3@bx.psu.edu
        # LIBRARY_ADD = Role One
        #               Role One aassociations: test@bx.psu.edu, test1@bx.psu.edu, test3@bx.psu.edu
        # LIBRARY_MODIFY = Role One
        #                  Role One aassociations: test@bx.psu.edu, test1@bx.psu.edu, test3@bx.psu.edu
        # LIBRARY_MANAGE = Role One
        #                  Role One aassociations: test@bx.psu.edu, test1@bx.psu.edu, test3@bx.psu.edu
        self.home()
        self.visit_url( '%s/library/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s' \
                        % ( self.url, str( library_one.id ), str( folder_one.id ), str( ldda_five.id ) ) )
        self.check_page_for_string( '5.bed' )
        self.check_page_for_string( 'This is the latest version of this library dataset' )
        # Current user test1@bx.psu.edu has Role One, which has the LIBRARY_MODIFY permission
        self.check_page_for_string( 'Edit attributes of 5.bed' )
        self.home()
        # Test importing the restricted dataset into a history, can't use the 
        # ~/library_admin/libraries form as twill barfs on it so we'll simulate the form submission
        # by going directly to the form action
        self.visit_url( '%s/library/datasets?do_action=add&ldda_ids=%d&library_id=%s' \
                        % ( self.url, ldda_five.id, str( library_one.id ) ) )
        self.check_page_for_string( '1 dataset(s) have been imported into your history' )
        self.logout()
        # regular_user2 should not be able to see 5.bed
        self.login( email = 'test2@bx.psu.edu' )
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        try:
            self.check_page_for_string( folder_one.name )
            raise AssertionError( '%s can see library folder %s when it contains only datasets restricted by role %s' \
                                  % ( regular_user2.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        try:
            self.check_page_for_string( '5.bed' )
            raise AssertionError( '%s can see dataset 5.bed in library folder %s when it was restricted by role %s' \
                                  % ( regular_user2.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        # regular_user3 should not be able to see folder_one ( even though it does not contain any datasets that she
        # can access ) since she has Role One, and Role One has all library permissions ( see above ).
        self.login( email = 'test3@bx.psu.edu' )
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( folder_one.name )
        # regular_user3 should not be able to see 5.bed since users must have every role associated
        # with the dataset in order to access it, and regular_user3 isnot associated with Role Two
        try:
            self.check_page_for_string( '5.bed' )
            raise AssertionError( '%s can see dataset 5.bed in library folder %s when it was restricted by role %s' \
                                  % ( regular_user3.email, folder_one.name, regular_user1_private_role.description ) )
        except:
            pass
        self.logout()
        self.login( email='test@bx.psu.edu' )
    def test_140_copy_dataset_from_history_to_subfolder( self ):
        """Testing copying a dataset from the current history to a subfolder"""
        self.new_history()
        self.upload_file( "6.bed" )
        latest_hda = sa_session.query( galaxy.model.HistoryDatasetAssociation ) \
                               .order_by( desc( galaxy.model.HistoryDatasetAssociation.table.c.create_time ) ) \
                               .first()
        self.add_history_datasets_to_library( str( library_one.id ), str( subfolder_one.id ), subfolder_one.name, str( latest_hda.id ), root=False )
        # Test for DatasetPermissionss, the default setting is "manage permissions"
        last_dataset_created = sa_session.query( galaxy.model.Dataset ) \
                                         .order_by( desc( galaxy.model.Dataset.table.c.create_time ) ) \
                                         .first()
        dps = sa_session.query( galaxy.model.DatasetPermissions ) \
                        .filter( galaxy.model.DatasetPermissions.table.c.dataset_id==last_dataset_created.id ) \
                        .all()
        if not dps:
            raise AssertionError( 'No DatasetPermissionss created for dataset id: %d' % last_dataset_created.id )
        if len( dps ) > 1:
            raise AssertionError( 'More than 1 DatasetPermissionss created for dataset id: %d' % last_dataset_created.id )
        for dp in dps:
            if not dp.action == 'manage permissions':
                raise AssertionError( 'DatasetPermissions.action "%s" is not the DefaultHistoryPermission setting of "manage permissions"' \
                                      % str( dp.action ) )
        global ldda_six
        ldda_six = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                             .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                             .first()
        assert ldda_six is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_six from the database'
        self.home()
        # Make sure the correct template was inherited
        self.visit_url( '%s/library/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s' \
                        % ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six.id ) ) )
        self.check_page_for_string( form_one_field_name )
        # Make sure the template contents were NOT inherited
        contents = "%s contents for Folder One's Subfolder" % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Parent folder template contents were displayed in the sub-folders inherited template fields"
        except:
            pass
    def test_145_editing_dataset_attribute_info( self ):
        """Testing editing a datasets attribute information"""
        new_ldda_name = '6.bed ( version 1 )'
        self.edit_ldda_attribute_info( str( library_one.id ), str( subfolder_one.id ), str( ldda_six.id ), ldda_six.name, new_ldda_name )
        self.home()
        sa_session.refresh( ldda_six )
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( ldda_six.name )
        self.home()
        # Make sure the template contents were NOT inherited
        self.visit_url( '%s/library/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s' \
                        % ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six.id ) ) )
        self.check_page_for_string( form_one_field_name )
        contents = "%s contents for Folder One's Subfolder" % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Parent folder template contents were displayed in the sub-folders inherited template fields"
        except:
            pass
    def test_150_uploading_new_dataset_version( self ):
        """Testing uploading a new version of a library dataset"""
        message = 'Testing uploading a new version of a dataset'
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for %s new version of 6.bed" % ( form_one_field_label, folder_one.name )
        self.upload_new_dataset_version( '6.bed',
                                         str( library_one.id ),
                                         str( subfolder_one.id ),
                                         str( subfolder_one.name ),
                                         str( ldda_six.library_dataset.id ),
                                         ldda_six.name,
                                         file_type='auto',
                                         dbkey='hg18',
                                         message=message.replace( ' ', '+' ),
                                         template_field_name1=form_one_field_name,
                                         template_field_contents1=template_contents )
        global ldda_six_version_two
        ldda_six_version_two = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                                         .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                                         .first()
        assert ldda_six_version_two is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_six_version_two from the database'
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six_version_two.id ) ) )
        self.check_page_for_string( 'This is the latest version of this library dataset' )
        # Make sure the correct template was inherited
        self.check_page_for_string( template_contents )
        # Make sure it does not include any inherited contents
        contents = "%s contents for Folder One's Subfolder" % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Parent folder template contents were displayed in the sub-folders inherited template fields"
        except:
            pass
        # There are 4 forms on this page and the template is the 4th form
        tc.fv( '4', form_one_field_name, template_contents )
        tc.submit( 'edit_info_button' )
        self.check_page_for_string( 'The information has been updated.' )
        self.check_page_for_string( template_contents )
        # Make sure the permissions are the same
        sa_session.refresh( ldda_six )
        if len( ldda_six.actions ) != len( ldda_six_version_two.actions ):
            raise AssertionError( 'ldda "%s" actions "%s" != ldda "%s" actions "%s"' \
                % ( ldda_six.name, str( ldda_six.actions ),
                    ldda_six_version_two.name, str( ldda_six_version_two.actions ) ) )
        if len( ldda_six.library_dataset.actions ) != len( ldda_six_version_two.library_dataset.actions ):
            raise AssertionError( 'ldda.library_dataset "%s" actions "%s" != ldda.library_dataset "%s" actions "%s"' \
                % ( ldda_six.name, str( ldda_six.library_dataset.actions ), ldda_six_version_two.name, str( ldda_six_version_two.library_dataset.actions ) ) )
        if len( ldda_six.dataset.actions ) != len( ldda_six_version_two.dataset.actions ):
            raise AssertionError( 'ldda.dataset "%s" actions "%s" != ldda.dataset "%s" actions "%s"' \
                % ( ldda_six.name, str( ldda_six.dataset.actions ), ldda_six_version_two.name, str( ldda_six_version_two.dataset.actions ) ) )
        # Check the previous version
        self.visit_url( "%s/library_admin/ldda_display_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six.id ) ) )
        self.check_page_for_string( 'This is an expired version of this library dataset' )
        self.home()
        # Make sure ldda_six is no longer displayed in the library
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        try:
            self.check_page_for_string( ldda_six.name )
            raise AssertionError, "Old version of library dataset %s is displayed in library" % ldda_six.name
        except:
            pass
        self.home()
        message = 'Testing uploading a new version of a library dataset'
        # The form_one template should be inherited to the library dataset upload form.
        template_contents = "%s contents for %s 5th new version of 6.bed" % ( form_one_field_label, folder_one.name )
        sa_session.refresh( ldda_six_version_two )
        self.upload_new_dataset_version( '6.bed',
                                         str( library_one.id ),
                                         str( subfolder_one.id ),
                                         str( subfolder_one.name ),
                                         str( ldda_six_version_two.library_dataset.id ),
                                         ldda_six_version_two.name,
                                         file_type='auto',
                                         dbkey='hg18',
                                         message=message.replace( ' ', '+' ),
                                         template_field_name1=form_one_field_name,
                                         template_field_contents1=template_contents )
        global ldda_six_version_five
        ldda_six_version_five = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                                          .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                                          .first()
        assert ldda_six_version_five is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_six_version_five from the database'
        self.home()
        self.visit_url( "%s/library_admin/ldda_edit_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six_version_five.id ) ) )
        self.check_page_for_string( 'This is the latest version of this library dataset' )
        # Make sure the correct template was inherited
        self.check_page_for_string( template_contents )
        # Make sure it does not include any inherited contents
        contents = "%s contents for Folder One's Subfolder" % form_one_field_label
        try:
            self.check_page_for_string( contents )
            raise AssertionError, "Parent folder template contents were displayed in the sub-folders inherited template fields"
        except:
            pass
        # There are 4 forms on this page and the template is the 4th form
        tc.fv( '4', form_one_field_name, template_contents )
        tc.submit( 'edit_info_button' )
        self.check_page_for_string( 'The information has been updated.' )
        self.check_page_for_string( template_contents )
        self.visit_url( "%s/library_admin/ldda_display_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six_version_five.id ) ) )
        check_str = 'Expired versions of %s' % ldda_six_version_five.name
        self.check_page_for_string( check_str )
        self.check_page_for_string( ldda_six.name )
        self.home()
        # Make sure the permissions are the same
        sa_session.refresh( ldda_six )
        if len( ldda_six.actions ) != len( ldda_six_version_five.actions ):
            raise AssertionError( 'ldda "%s" actions "%s" != ldda "%s" actions "%s"' \
                % ( ldda_six.name, str( ldda_six.actions ),
                    ldda_six_version_five.name, str( ldda_six_version_five.actions ) ) )
        if len( ldda_six.library_dataset.actions ) != len( ldda_six_version_five.library_dataset.actions ):
            raise AssertionError( 'ldda.library_dataset "%s" actions "%s" != ldda.library_dataset "%s" actions "%s"' \
                % ( ldda_six.name, str( ldda_six.library_dataset.actions ), ldda_six_version_five.name, str( ldda_six_version_five.library_dataset.actions ) ) )
        if len( ldda_six.dataset.actions ) != len( ldda_six_version_five.dataset.actions ):
            raise AssertionError( 'ldda.dataset "%s" actions "%s" != ldda.dataset "%s" actions "%s"' \
                % ( ldda_six.name, str( ldda_six.dataset.actions ), ldda_six_version_five.name, str( ldda_six_version_five.dataset.actions ) ) )
        # Check the previous version
        self.visit_url( "%s/library_admin/ldda_display_info?library_id=%s&folder_id=%s&obj_id=%s" % \
                        ( self.url, str( library_one.id ), str( subfolder_one.id ), str( ldda_six_version_two.id ) ) )
        self.check_page_for_string( 'This is an expired version of this library dataset' )
        self.home()
    def test_155_upload_directory_of_files_from_admin_view( self ):
        """Testing uploading a directory of files to a root folder from the Admin view"""
        message = 'This is a test for uploading a directory of files'
        template_contents = "%s contents for directory of 3 datasets in %s" % ( form_one_field_label, folder_one.name )
        roles_tuple = [ ( str( role_one.id ), role_one.name ) ]
        check_str = "Added 3 datasets to the library '%s' ( each is selected )." % library_one.root_folder.name
        self.add_dir_of_files_from_admin_view( str( library_one.id ),
                                               str( library_one.root_folder.id ),
                                               roles_tuple=roles_tuple,
                                               message=message.replace( '+', ' ' ),
                                               template_field_name1=form_one_field_name,
                                               template_field_contents1=template_contents )
        self.home()
        self.visit_page( 'library_admin/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        self.check_page_for_string( admin_user.email )
        self.check_page_for_string( message )
        self.home()
    def test_160_change_permissions_on_datasets_uploaded_from_library_dir( self ):
        """Testing changing the permissions on datasets uploaded from a directory"""
        # It would be nice if twill functioned such that the above test resulted in a
        # form with the uploaded datasets selected, but it does not ( they're not checked ),
        # so we'll have to simulate this behavior ( not ideal ) for the 'edit' action.  We
        # first need to get the ldda.id for the 3 new datasets
        latest_3_lddas = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                                   .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.update_time ) ) \
                                   .limit( 3 )
        ldda_ids = ''
        for ldda in latest_3_lddas:
            ldda_ids += '%s,' % str( ldda.id )
        ldda_ids = ldda_ids.rstrip( ',' )
        permissions = [ 'DATASET_ACCESS', 'DATASET_MANAGE_PERMISSIONS' ]
        def build_url( permissions, role ):
            # We'll bypass the library_admin/datasets method and directly call the library_admin/dataset method, setting
            # access, manage permissions, and edit metadata permissions to role_one
            url = '/library_admin/ldda_manage_permissions?obj_id=%s&library_id=%s&folder_id=%s&update_roles_button=Save' % ( ldda_ids, str( library_one.id ), str( folder_one.id ) )
            for p in permissions:
                url += '&%s_in=%s' % ( p, str( role.id ) )
            return url
        url = build_url( permissions, role_one )
        self.home()
        self.visit_url( url )
        self.check_page_for_string( 'Permissions have been updated on 3 datasets' )
        def check_edit_page1( lddas ):
            # Make sure the permissions have been correctly updated for the 3 datasets.  Permissions should 
            # be all of the above on any of the 3 datasets that are imported into a history
            for ldda in lddas:
                # Import each library dataset into our history
                self.home()
                self.visit_url( '%s/library/datasets?do_action=add&ldda_ids=%s&library_id=%s' % ( self.url, str( ldda.id ), str( library_one.id ) ) )
                # Determine the new HistoryDatasetAssociation id created when the library dataset was imported into our history
                last_hda_created = sa_session.query( galaxy.model.HistoryDatasetAssociation ) \
                                             .order_by( desc( galaxy.model.HistoryDatasetAssociation.table.c.create_time ) ) \
                                             .first()
                self.home()
                self.visit_url( '%s/root/edit?id=%s' % ( self.url, str( last_hda_created.id ) ) )
                self.check_page_for_string( 'Edit Attributes' )
                self.check_page_for_string( last_hda_created.name )
                check_str = 'Manage dataset permissions and role associations of %s' % last_hda_created.name
                self.check_page_for_string( check_str )
                self.check_page_for_string( 'Role members can manage the roles associated with this dataset' )
                self.check_page_for_string( 'Role members can import this dataset into their history for analysis' )
        # admin_user is associated with role_one, so should have all permissions on imported datasets
        check_edit_page1( latest_3_lddas )
        self.logout()
        # regular_user1 is associated with role_one, so should have all permissions on imported datasets
        self.login( email='test1@bx.psu.edu' )
        check_edit_page1( latest_3_lddas )
        self.logout()
        # Since regular_user2 is not associated with role_one, she should not have
        # access to any of the 3 datasets, so she will not see folder_one on the libraries page
        self.login( email='test2@bx.psu.edu' )
        self.home()
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_one.id ) ) )
        try:
            self.check_page_for_string( folder_one.name )
            raise AssertionError( '%s can access folder %s even though all contained datasets should be restricted from access by her' \
                                  % ( regular_user2.email, folder_one.name ) )
        except:
            pass # This is the behavior we want
        self.logout()
        # regular_user3 is associated with role_one, so should have all permissions on imported datasets
        self.login( email='test3@bx.psu.edu' )
        check_edit_page1( latest_3_lddas )
        self.logout()
        self.login( email='test@bx.psu.edu' )
        # Change the permissions and test again
        permissions = [ 'DATASET_ACCESS' ]
        url = build_url( permissions, role_one )
        self.home()
        self.visit_url( url )
        self.check_page_for_string( 'Permissions have been updated on 3 datasets' )
        def check_edit_page2( lddas ):
            # Make sure the permissions have been correctly updated for the 3 datasets.  Permissions should 
            # be all of the above on any of the 3 datasets that are imported into a history
            for ldda in lddas:
                self.home()
                self.visit_url( '%s/library/datasets?library_id=%s&do_action=add&ldda_ids=%s' % ( self.url, str( library_one.id ), str( ldda.id ) ) )
                # Determine the new HistoryDatasetAssociation id created when the library dataset was imported into our history
                last_hda_created = sa_session.query( galaxy.model.HistoryDatasetAssociation ) \
                                             .order_by( desc( galaxy.model.HistoryDatasetAssociation.table.c.create_time ) ) \
                                             .first()
                self.home()
                self.visit_url( '%s/root/edit?id=%s' % ( self.url, str( last_hda_created.id ) ) )
                self.check_page_for_string( 'Edit Attributes' )
                self.check_page_for_string( last_hda_created.name )
                self.check_page_for_string( 'View Permissions' )
                self.check_page_for_string( last_hda_created.name )
                try:
                    # This should no longer be possible
                    check_str = 'Manage dataset permissions and role associations of %s' % last_hda_created.name
                    self.check_page_for_string( check_str )
                    raise AssertionError( '%s incorrectly has DATASET_MANAGE_PERMISSIONS on datasets imported from a library' % admin_user.email )
                except:
                    pass
                try:
                    # This should no longer be possible
                    self.check_page_for_string( 'Role members can manage the roles associated with this dataset' )
                    raise AssertionError( '%s incorrectly has DATASET_MANAGE_PERMISSIONS on datasets imported from a library' % admin_user.email )
                except:
                    pass
                try:
                    # This should no longer be possible
                    self.check_page_for_string( 'Role members can import this dataset into their history for analysis' )
                    raise AssertionError( '%s incorrectly has DATASET_MANAGE_PERMISSIONS on datasets imported from a library' % admin_user.email )
                except:
                    pass
        check_edit_page2( latest_3_lddas )
        self.home()
    def test_165_upload_directory_of_files_from_libraries_view( self ):
        """Testing uploading a directory of files to a root folder from the Data Libraries view"""
        # admin_user will not have the option sto upload a directory of files from the
        # Libraries view since a sub-directory named the same as their email is not contained
        # in the configured user_library_import_dir.  However, since members of role_one have
        # the LIBRARY_ADD permission, we can test this feature as regular_user1 or regular_user3
        self.logout()
        self.login( email=regular_user1.email )
        message = 'Uploaded all files in test-data/users/test1...'
        # Since regular_user1 does not have any sub-directories contained within her configured
        # user_library_import_dir, the only option in her server_dir select list will be the
        # directory named the same as her email
        check_str_after_submit = "Added 1 datasets to the library '%s' ( each is selected )." % library_one.root_folder.name
        self.add_dir_of_files_from_libraries_view( str( library_one.id ),
                                                   str( library_one.root_folder.id ),
                                                   regular_user1.email,
                                                   check_str_after_submit=check_str_after_submit,
                                                   message=message.replace( '+', ' ' ) )
        self.home()
        self.visit_page( 'library/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        self.check_page_for_string( regular_user1.email )
        self.check_page_for_string( message )
        self.logout()
        self.login( regular_user3.email )
        message = 'Uploaded all files in test-data/users/test3.../run1'
        # Since regular_user2 has a subdirectory contained within her configured user_library_import_dir,
        # she will have a "None" option in her server_dir select list
        check_str1 = '<option>None</option>'
        self.add_dir_of_files_from_libraries_view( str( library_one.id ),
                                                   str( library_one.root_folder.id ),
                                                   'run1',
                                                   check_str_after_submit=check_str_after_submit,
                                                   message=message.replace( '+', ' ' ) )
        self.home()
        self.visit_page( 'library/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        self.check_page_for_string( regular_user3.email )
        self.check_page_for_string( message )
        self.home()
        self.logout()
        self.login( email=admin_user.email )
    def test_167_download_archive_of_library_files( self ):
        """Testing downloading an archive of files from the library"""
        for format in ( 'tbz', 'tgz', 'zip' ):
            archive = self.download_archive_of_library_files( str( library_one.id ),
                                                              ( str( ldda_one.id ), str( ldda_two.id ) ),
                                                              format )
            self.check_archive_contents( archive, ( ldda_one, ldda_two ) )
            os.remove( archive )
    def test_170_mark_group_deleted( self ):
        """Testing marking a group as deleted"""
        # Logged in as admin_user
        self.home()
        self.visit_url( '%s/admin/groups' % self.url )
        self.check_page_for_string( group_two.name )
        self.mark_group_deleted( self.security.encode_id( group_two.id ), group_two.name )
        sa_session.refresh( group_two )
        if not group_two.deleted:
            raise AssertionError( '%s was not correctly marked as deleted.' % group_two.name )
        # Deleting a group should not delete any associations
        if not group_two.members:
            raise AssertionError( '%s incorrectly lost all members when it was marked as deleted.' % group_two.name )
        if not group_two.roles:
            raise AssertionError( '%s incorrectly lost all role associations when it was marked as deleted.' % group_two.name )
    def test_175_undelete_group( self ):
        """Testing undeleting a deleted group"""
        # Logged in as admin_user
        self.undelete_group( self.security.encode_id( group_two.id ), group_two.name )
        sa_session.refresh( group_two )
        if group_two.deleted:
            raise AssertionError( '%s was not correctly marked as not deleted.' % group_two.name )
    def test_180_mark_role_deleted( self ):
        """Testing marking a role as deleted"""
        # Logged in as admin_user
        self.home()
        self.visit_url( '%s/admin/roles' % self.url )
        self.check_page_for_string( role_two.name )
        self.mark_role_deleted( self.security.encode_id( role_two.id ), role_two.name )
        sa_session.refresh( role_two )
        if not role_two.deleted:
            raise AssertionError( '%s was not correctly marked as deleted.' % role_two.name )
        # Deleting a role should not delete any associations
        if not role_two.users:
            raise AssertionError( '%s incorrectly lost all user associations when it was marked as deleted.' % role_two.name )
        if not role_two.groups:
            raise AssertionError( '%s incorrectly lost all group associations when it was marked as deleted.' % role_two.name )
    def test_185_undelete_role( self ):
        """Testing undeleting a deleted role"""
        # Logged in as admin_user
        self.undelete_role( self.security.encode_id( role_two.id ), role_two.name )
    def test_190_mark_dataset_deleted( self ):
        """Testing marking a library dataset as deleted"""
        # Logged in as admin_user
        self.home()
        self.delete_library_item( str( library_one.id ), str( ldda_two.library_dataset.id ), ldda_two.name, library_item_type='library_dataset' )
        self.home()
        self.visit_page( 'library_admin/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        try:
            # 2.bed was only contained in the library in 1 place, so it should no longer display
            self.check_page_for_string( ldda_two.name )
            raise AssertionError( "Dataset '%s' is incorrectly displayed in the library after it has been deleted." % ldda_two.name )
        except:
            pass
        self.home()
    def test_195_display_deleted_dataset( self ):
        """Testing displaying deleted dataset"""
        # Logged in as admin_user
        self.home()
        self.visit_url( "%s/library_admin/browse_library?obj_id=%s&show_deleted=True" % ( self.url, str( library_one.id ) ) )
        self.check_page_for_string( ldda_two.name )
        self.home()
    def test_200_hide_deleted_dataset( self ):
        """Testing hiding deleted dataset"""
        # Logged in as admin_user
        self.home()
        self.visit_url( "%s/library_admin/browse_library?obj_id=%s&show_deleted=False" % ( self.url, str( library_one.id ) ) )
        try:
            self.check_page_for_string( ldda_two.name )
            raise AssertionError( "Dataset '%s' is incorrectly displayed in the library after it has been deleted." % ldda_two.name )
        except:
            pass
        self.home()
    def test_205_mark_folder_deleted( self ):
        """Testing marking a library folder as deleted"""
        # Logged in as admin_user
        self.home()
        self.delete_library_item( str( library_one.id ), str( folder_two.id ), folder_two.name, library_item_type='folder' )
        self.home()
        self.visit_page( 'library_admin/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        try:
            self.check_page_for_string( folder_two.name )
            raise AssertionError( "Folder '%s' is incorrectly displayed in the library after it has been deleted." % folder_two.name )
        except:
            pass
        self.home()
    def test_210_mark_folder_undeleted( self ):
        """Testing marking a library folder as undeleted"""
        # Logged in as admin_user
        self.home()
        self.undelete_library_item( str( library_one.id ), str( folder_two.id ), folder_two.name, library_item_type='folder' )
        self.home()
        self.visit_page( 'library_admin/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        self.check_page_for_string( folder_two.name )
        try:
            # 2.bed was deleted before the folder was deleted, so state should have been saved.  In order
            # fro 2.bed to be displayed, it would itself have to be marked undeleted.
            self.check_page_for_string( ldda_two.name )
            raise AssertionError( "Dataset '%s' is incorrectly displayed in the library after parent folder was undeleted." % ldda_two.name )
        except:
            pass
        self.home()
    def test_215_mark_library_deleted( self ):
        """Testing marking a library as deleted"""
        # Logged in as admin_user
        self.home()
        # First mark folder_two as deleted to further test state saving when we undelete the library
        self.delete_library_item( str( library_one.id ), str( folder_two.id ), folder_two.name, library_item_type='folder' )
        self.delete_library_item( str( library_one.id ), str( library_one.id ), library_one.name, library_item_type='library' )
        self.home()
        self.visit_page( 'library_admin/deleted_libraries' )
        self.check_page_for_string( library_one.name )
        self.home()
    def test_220_mark_library_undeleted( self ):
        """Testing marking a library as undeleted"""
        # Logged in as admin_user
        self.home()
        self.undelete_library_item( str( library_one.id ), str( library_one.id ), library_one.name, library_item_type='library' )
        self.home()
        self.visit_page( 'library_admin/browse_library?obj_id=%s' % ( str( library_one.id ) ) )
        self.check_page_for_string( library_one.name )
        try:
            # folder_two was marked deleted before the library was deleted, so it should not be displayed
            self.check_page_for_string( folder_two.name )
            raise AssertionError( "Deleted folder '%s' is incorrectly displayed in the library after the library was undeleted." % folder_two.name )
        except:
            pass
        self.home()
    def test_225_purge_user( self ):
        """Testing purging a user account"""
        # Logged in as admin_user
        self.mark_user_deleted( user_id=self.security.encode_id( regular_user3.id ), email=regular_user3.email )
        sa_session.refresh( regular_user3 )
        self.purge_user( self.security.encode_id( regular_user3.id ), regular_user3.email )
        sa_session.refresh( regular_user3 )
        if not regular_user3.purged:
            raise AssertionError( 'User %s was not marked as purged.' % regular_user3.email )
        # Make sure DefaultUserPermissions deleted EXCEPT FOR THE PRIVATE ROLE
        if len( regular_user3.default_permissions ) != 1:
            raise AssertionError( 'DefaultUserPermissions for user %s were not deleted.' % regular_user3.email )
        for dup in regular_user3.default_permissions:
            role = sa_session.query( galaxy.model.Role ).get( dup.role_id )
            if role.type != 'private':
                raise AssertionError( 'DefaultUserPermissions for user %s are not related with the private role.' % regular_user3.email )
        # Make sure History deleted
        for history in regular_user3.histories:
            sa_session.refresh( history )
            if not history.deleted:
                raise AssertionError( 'User %s has active history id %d after their account was marked as purged.' % ( regular_user3.email, hda.id ) )
            # NOTE: Not all hdas / datasets will be deleted at the time a history is deleted - the cleanup_datasets.py script
            # is responsible for this.
        # Make sure UserGroupAssociations deleted
        if regular_user3.groups:
            raise AssertionError( 'User %s has active group id %d after their account was marked as purged.' % ( regular_user3.email, uga.id ) )
        # Make sure UserRoleAssociations deleted EXCEPT FOR THE PRIVATE ROLE
        if len( regular_user3.roles ) != 1:
            raise AssertionError( 'UserRoleAssociations for user %s were not deleted.' % regular_user3.email )
        for ura in regular_user3.roles:
            role = sa_session.query( galaxy.model.Role ).get( ura.role_id )
            if role.type != 'private':
                raise AssertionError( 'UserRoleAssociations for user %s are not related with the private role.' % regular_user3.email )
    def test_230_manually_unpurge_user( self ):
        """Testing manually un-purging a user account"""
        # Logged in as admin_user
        # Reset the user for later test runs.  The user's private Role and DefaultUserPermissions for that role
        # should have been preserved, so all we need to do is reset purged and deleted.
        # TODO: If we decide to implement the GUI feature for un-purging a user, replace this with a method call
        regular_user3.purged = False
        regular_user3.deleted = False
        sa_session.add( regular_user3 )
        sa_session.flush()
    def test_235_purge_group( self ):
        """Testing purging a group"""
        # Logged in as admin_user
        self.mark_group_deleted( self.security.encode_id( group_two.id ), group_two.name )
        self.purge_group( self.security.encode_id( group_two.id ), group_two.name )
        # Make sure there are no UserGroupAssociations
        uga = sa_session.query( galaxy.model.UserGroupAssociation ) \
                        .filter( galaxy.model.UserGroupAssociation.table.c.group_id == group_two.id ) \
                        .first()
        if uga:
            raise AssertionError( "Purging the group did not delete the UserGroupAssociations for group_id '%s'" % group_two.id )
        # Make sure there are no GroupRoleAssociations
        gra = sa_session.query( galaxy.model.GroupRoleAssociation ) \
                        .filter( galaxy.model.GroupRoleAssociation.table.c.group_id == group_two.id ) \
                        .first()
        if gra:
            raise AssertionError( "Purging the group did not delete the GroupRoleAssociations for group_id '%s'" % group_two.id )
        # Undelete the group for later test runs
        self.undelete_group( self.security.encode_id( group_two.id ), group_two.name )
    def test_240_purge_role( self ):
        """Testing purging a role"""
        # Logged in as admin_user
        self.mark_role_deleted( self.security.encode_id( role_two.id ), role_two.name )
        self.purge_role( self.security.encode_id( role_two.id ), role_two.name )
        # Make sure there are no UserRoleAssociations
        uras = sa_session.query( galaxy.model.UserRoleAssociation ) \
                         .filter( galaxy.model.UserRoleAssociation.table.c.role_id == role_two.id ) \
                         .all()
        if uras:
            raise AssertionError( "Purging the role did not delete the UserRoleAssociations for role_id '%s'" % role_two.id )
        # Make sure there are no DefaultUserPermissions associated with the Role
        dups = sa_session.query( galaxy.model.DefaultUserPermissions ) \
                         .filter( galaxy.model.DefaultUserPermissions.table.c.role_id == role_two.id ) \
                         .all()
        if dups:
            raise AssertionError( "Purging the role did not delete the DefaultUserPermissions for role_id '%s'" % role_two.id )
        # Make sure there are no DefaultHistoryPermissions associated with the Role
        dhps = sa_session.query( galaxy.model.DefaultHistoryPermissions ) \
                         .filter( galaxy.model.DefaultHistoryPermissions.table.c.role_id == role_two.id ) \
                         .all()
        if dhps:
            raise AssertionError( "Purging the role did not delete the DefaultHistoryPermissions for role_id '%s'" % role_two.id )
        # Make sure there are no GroupRoleAssociations
        gra = sa_session.query( galaxy.model.GroupRoleAssociation ) \
                        .filter( galaxy.model.GroupRoleAssociation.table.c.role_id == role_two.id ) \
                        .first()
        if gra:
            raise AssertionError( "Purging the role did not delete the GroupRoleAssociations for role_id '%s'" % role_two.id )
        # Make sure there are no DatasetPermissionss
        dp = sa_session.query( galaxy.model.DatasetPermissions ) \
                       .filter( galaxy.model.DatasetPermissions.table.c.role_id == role_two.id ) \
                       .first()
        if dp:
            raise AssertionError( "Purging the role did not delete the DatasetPermissionss for role_id '%s'" % role_two.id )
    def test_245_manually_unpurge_role( self ):
        """Testing manually un-purging a role"""
        # Logged in as admin_user
        # Manually unpurge, then undelete the role for later test runs
        # TODO: If we decide to implement the GUI feature for un-purging a role, replace this with a method call
        role_two.purged = False
        sa_session.add( role_two )
        sa_session.flush()
        self.undelete_role( self.security.encode_id( role_two.id ), role_two.name )
    def test_250_purge_library( self ):
        """Testing purging a library"""
        # Logged in as admin_user
        self.home()
        self.delete_library_item( str( library_one.id ), str( library_one.id ), library_one.name, library_item_type='library' )
        self.purge_library( str( library_one.id ), library_one.name )
        # Make sure the library was purged
        sa_session.refresh( library_one )
        if not ( library_one.deleted and library_one.purged ):
            raise AssertionError( 'The library id %s named "%s" has not been marked as deleted and purged.' % ( str( library_one.id ), library_one.name ) )
        def check_folder( library_folder ):
            for folder in library_folder.folders:
                sa_session.refresh( folder )
                # Make sure all of the library_folders are purged
                if not folder.purged:
                    raise AssertionError( 'The library_folder id %s named "%s" has not been marked purged.' % ( str( folder.id ), folder.name ) )
                check_folder( folder )
            # Make sure all of the LibraryDatasets and associated objects are deleted
            sa_session.refresh( library_folder )
            for library_dataset in library_folder.datasets:
                sa_session.refresh( library_dataset )
                ldda = library_dataset.library_dataset_dataset_association
                if ldda:
                    sa_session.refresh( ldda )
                    if not ldda.deleted:
                        raise AssertionError( 'The library_dataset_dataset_association id %s named "%s" has not been marked as deleted.' % \
                                              ( str( ldda.id ), ldda.name ) )
                    # Make sure all of the datasets have been deleted
                    dataset = ldda.dataset
                    sa_session.refresh( dataset )
                    if not dataset.deleted:
                        raise AssertionError( 'The dataset with id "%s" has not been marked as deleted when it should have been.' % \
                                              str( ldda.dataset.id ) )
                if not library_dataset.deleted:
                    raise AssertionError( 'The library_dataset id %s named "%s" has not been marked as deleted.' % \
                                          ( str( library_dataset.id ), library_dataset.name ) )
        check_folder( library_one.root_folder )
    def test_255_no_library_template( self ):
        """Test library features when library has no template"""
        # Logged in as admin_user
        name = "Library Two"
        description = "This is Library Two"
        # Create a library, adding no template
        self.create_library( name=name, description=description )
        self.visit_page( 'library_admin/browse_libraries' )
        self.check_page_for_string( name )
        self.check_page_for_string( description )
        library_two = sa_session.query( galaxy.model.Library ) \
                                .filter( and_( galaxy.model.Library.table.c.name==name,
                                               galaxy.model.Library.table.c.description==description,
                                               galaxy.model.Library.table.c.deleted==False ) ) \
                                .first()
        assert library_two is not None, 'Problem retrieving library named "%s" from the database' % name
        # Add a dataset to the library
        self.add_library_dataset( 'library_admin',
                                  '7.bed',
                                  str( library_two.id ),
                                  str( library_two.root_folder.id ),
                                  library_two.root_folder.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  message='',
                                  root=True )
        ldda_seven = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                               .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                               .first()
        assert ldda_seven is not None, 'Problem retrieving LibraryDatasetDatasetAssociation ldda_seven from the database'
        self.home()
        self.visit_url( '%s/library_admin/browse_library?obj_id=%s' % ( self.url, str( library_two.id ) ) )
        self.check_page_for_string( "7.bed" )
        self.check_page_for_string( admin_user.email )
        # TODO: add a functional test to cover adding a library dataset via url_paste here...
        # TODO: Add a functional test to cover checking the space_to_tab checkbox here...
        # Delete and purge the library
        self.home()
        self.delete_library_item( str( library_two.id ), str( library_two.id ), library_two.name, library_item_type='library' )
        self.purge_library( str( library_two.id ), library_two.name )
        self.home()
    def test_260_library_permissions( self ):
        """Test library permissions"""
        # Logged in as admin_user
        name = "Library Three"
        description = "This is Library Three"
        # Create a library, adding no template
        self.create_library( name=name, description=description )
        self.visit_page( 'library_admin/browse_libraries' )
        self.check_page_for_string( name )
        self.check_page_for_string( description )
        global library_three
        library_three = sa_session.query( galaxy.model.Library ) \
                                  .filter( and_( galaxy.model.Library.table.c.name==name,
                                                 galaxy.model.Library.table.c.description==description,
                                                 galaxy.model.Library.table.c.deleted==False ) ) \
                                  .first()
        assert library_three is not None, 'Problem retrieving library named "%s" from the database' % name
        # Set library permissions for regular_user1 and regular_user2.  Each of these users will be permitted to
        # LIBRARY_ADD, LIBRARY_MODIFY, LIBRARY_MANAGE for library items.
        permissions_in = [ k for k, v in galaxy.model.Library.permitted_actions.items() ]
        permissions_out = []
        role_ids_str = '%s,%s' % ( str( regular_user1_private_role.id ), str( regular_user2_private_role.id ) )
        self.set_library_permissions( str( library_three.id ), library_three.name, role_ids_str, permissions_in, permissions_out )
        self.logout()
        # Login as regular_user1 and make sure they can see the library
        self.login( email=regular_user1.email )
        self.visit_url( '%s/library/browse_libraries' % self.url )
        self.check_page_for_string( name )
        self.logout()
        # Login as regular_user2 and make sure they can see the library
        self.login( email=regular_user2.email )
        self.visit_url( '%s/library/browse_libraries' % self.url )
        self.check_page_for_string( name )
        # Add a dataset to the library
        message = 'Testing adding 1.bed to Library Three root folder'
        self.add_library_dataset( 'library',
                                  '1.bed',
                                  str( library_three.id ),
                                  str( library_three.root_folder.id ),
                                  library_three.root_folder.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  message=message.replace( ' ', '+' ),
                                  root=True )
        # Add a folder to the library
        name = "Root Folder's Folder X"
        description = "This is the root folder's Folder X"
        self.add_folder( 'library',
                         str( library_three.id ),
                         str( library_three.root_folder.id ), 
                         name=name,
                         description=description )
        global folder_x
        folder_x = sa_session.query( galaxy.model.LibraryFolder ) \
                             .filter( and_( galaxy.model.LibraryFolder.table.c.parent_id==library_three.root_folder.id,
                                            galaxy.model.LibraryFolder.table.c.name==name,
                                            galaxy.model.LibraryFolder.table.c.description==description ) ) \
                             .first()
        # Add an information template to the folder
        template_name = 'Folder Template 1'
        self.add_folder_info_template( 'library',
                                        str( library_one.id ),
                                        str( folder_x.id ),
                                        str( form_one.id ),
                                        form_one.name )
        # Modify the folder's information
        contents = '%s folder contents' % form_one_field_label
        new_name = "Root Folder's Folder Y"
        new_description = "This is the root folder's Folder Y"
        self.edit_folder_info( 'library',
                               str( folder_x.id ),
                               str( library_three.id ),
                               name,
                               new_name,
                               new_description,
                               contents=contents,
                               field_name=form_one_field_name )
        # Twill barfs when self.check_page_for_string() is called after dealing with an information template,
        # the exception is: TypeError: 'str' object is not callable
        # the work-around it to end this method so any calls are in the next method.
    def test_265_template_features_and_permissions( self ):
        """Test library template and more permissions behavior from the Data Libraries view"""
        # Logged in as regular_user2
        sa_session.refresh( folder_x )
        # Add a dataset to the folder
        message = 'Testing adding 2.bed to Library Three root folder'
        self.add_library_dataset( 'library',
                                  '2.bed',
                                  str( library_three.id ),
                                  str( folder_x.id ),
                                  folder_x.name,
                                  file_type='bed',
                                  dbkey='hg18',
                                  message=message.replace( ' ', '+' ),
                                  root=False )
        global ldda_x
        ldda_x = sa_session.query( galaxy.model.LibraryDatasetDatasetAssociation ) \
                           .order_by( desc( galaxy.model.LibraryDatasetDatasetAssociation.table.c.create_time ) ) \
                           .first()
        assert ldda_x is not None, 'Problem retrieving ldda_x from the database'
        # Add an information template to the library
        template_name = 'Library Template 3'
        self.add_library_info_template( 'library',
                                        str( library_three.id ),
                                        str( form_one.id ),
                                        form_one.name )
        # Add information to the library using the template
        contents = '%s library contents' % form_one_field_label
        self.visit_url( '%s/library/library?obj_id=%s&information=True' % ( self.url, str( library_three.id ) ) )
        # There are 2 forms on this page and the template is the 2nd form
        tc.fv( '2', form_one_field_name, contents )
        tc.submit( 'edit_info_button' )
        # For some reason, the following check:
        # self.check_page_for_string ( 'The information has been updated.' )
        # ...throws the following exception - I have not idea why!
        # TypeError: 'str' object is not callable
        # The work-around is to not make ANY self.check_page_for_string() calls until the next method
    def test_270_permissions_as_different_regular_user( self ):
        """Test library template and more permissions behavior from the Data Libraries view as a different user"""
        # Log in as regular_user2
        self.logout()
        self.login( email=regular_user1.email )
        self.visit_url( '%s/library/browse_library?obj_id=%s' % ( self.url, str( library_three.id ) ) )
        self.check_page_for_string( ldda_x.name )
    def test_275_reset_data_for_later_test_runs( self ):
        """Reseting data to enable later test runs to pass"""
        # Logged in as regular_user2
        self.logout()
        self.login( email=admin_user.email )
        self.delete_library_item( str( library_three.id ), str( library_three.id ), library_three.name, library_item_type='library' )
        self.purge_library( str( library_three.id ), library_three.name )
        ##################
        # Eliminate all non-private roles
        ##################
        for role in [ role_one, role_two, role_three ]:
            self.mark_role_deleted( self.security.encode_id( role.id ), role.name )
            self.purge_role( self.security.encode_id( role.id ), role.name )
            # Manually delete the role from the database
            sa_session.refresh( role )
            sa_session.delete( role )
            sa_session.flush()
        ##################
        # Eliminate all groups
        ##################
        for group in [ group_zero, group_one, group_two ]:
            self.mark_group_deleted( self.security.encode_id( group.id ), group.name )
            self.purge_group( self.security.encode_id( group.id ), group.name )
            # Manually delete the group from the database
            sa_session.refresh( group )
            sa_session.delete( group )
            sa_session.flush()
        ##################
        # Make sure all users are associated only with their private roles
        ##################
        for user in [ admin_user, regular_user1, regular_user2, regular_user3 ]:
            sa_session.refresh( user )
            if len( user.roles) != 1:
                raise AssertionError( '%d UserRoleAssociations are associated with %s ( should be 1 )' % ( len( user.roles ), user.email ) )
        #####################
        # Reset DefaultHistoryPermissions for regular_user1
        #####################
        self.logout()
        self.login( email=regular_user1.email )
        # Change DefaultHistoryPermissions for regular_user1 back to the default
        permissions_in = [ 'DATASET_MANAGE_PERMISSIONS' ]
        permissions_out = [ 'DATASET_ACCESS' ]
        self.user_set_default_permissions( permissions_in=permissions_in, permissions_out=permissions_out, role_id=str( regular_user1_private_role.id ) )
        self.logout()
        self.login( email=admin_user.email )
