from galaxy.web.base.controller import *
from galaxy.web.framework.helpers import time_ago, iff, grids
from galaxy.model.orm import *
from galaxy.datatypes import sniff
from galaxy import util
from galaxy.util.streamball import StreamBall
import logging, tempfile, zipfile, tarfile, os, sys
from galaxy.web.form_builder import * 
from datetime import datetime, timedelta
from galaxy.web.controllers.forms import get_all_forms
from sqlalchemy.sql.expression import func, and_
from sqlalchemy.sql import select

log = logging.getLogger( __name__ )

#
# ---- Request Grid ------------------------------------------------------------ 
#

class RequestsGrid( grids.Grid ):
    # Custom column types
    class NameColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request):
            return request.name
    class DescriptionColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request):
            return request.desc
    class SamplesColumn( grids.GridColumn ):
        def get_value(self, trans, grid, request):
            return str(len(request.samples))
    class TypeColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request):
            return request.type.name
    class LastUpdateColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request):
            delta = datetime.utcnow() - request.update_time
            if delta > timedelta( minutes=60 ):
                last_update = '%s hours' % int( delta.seconds / 60 / 60 )
            else:
                last_update = '%s minutes' % int( delta.seconds / 60 )
            return last_update
    class StateColumn( grids.GridColumn ):
        def __init__( self, col_name, key, model_class, event_class, filterable, link ):
            grids.GridColumn.__init__(self, col_name, key=key, model_class=model_class, filterable=filterable, link=link)
            self.event_class = event_class
        def get_value(self, trans, grid, request):
            if request.state() == request.states.REJECTED:
                return '<div class="count-box state-color-error">%s</div>' % request.state()
            elif request.state() == request.states.NEW:
                return '<div class="count-box state-color-queued">%s</div>' % request.state()
            elif request.state() == request.states.SUBMITTED:
                return '<div class="count-box state-color-running">%s</div>' % request.state()
            elif request.state() == request.states.COMPLETE:
                return '<div class="count-box state-color-ok">%s</div>' % request.state()
            return request.state()
        def filter( self, db_session, query, column_filter ):
            """ Modify query to filter request by state. """
            if column_filter == "All":
                return query
            if column_filter:
                # select r.id, r.name, re.id, re.state 
                # from request as r, request_event as re
                # where re.request_id=r.id and re.state='Complete' and re.create_time in
                #                        (select MAX( create_time)
                #                         from request_event
                #                         group by request_id)
                q = query.join(self.event_class.table)\
                         .filter( self.model_class.table.c.id==self.event_class.table.c.request_id )\
                         .filter( self.event_class.table.c.state==column_filter )\
                         .filter( self.event_class.table.c.id.in_(select(columns=[func.max(self.event_class.table.c.id)],
                                                                                  from_obj=self.event_class.table,
                                                                                  group_by=self.event_class.table.c.request_id)))
                #print column_filter, q
            return q
        def get_accepted_filters( self ):
            """ Returns a list of accepted filters for this column. """
            accepted_filter_labels_and_vals = [ model.Request.states.NEW,
                                                model.Request.states.REJECTED,
                                                model.Request.states.SUBMITTED,
                                                model.Request.states.COMPLETE,
                                                "All"]
            accepted_filters = []
            for val in accepted_filter_labels_and_vals:
                label = val.lower()
                args = { self.key: val }
                accepted_filters.append( grids.GridColumnFilter( label, args) )
            return accepted_filters
    class UserColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request):
            return request.user.email
    class DeletedColumn( grids.GridColumn ):
       def get_accepted_filters( self ):
           """ Returns a list of accepted filters for this column. """
           accepted_filter_labels_and_vals = { "active" : "False", "deleted" : "True", "all": "All" }
           accepted_filters = []
           for label, val in accepted_filter_labels_and_vals.items():
               args = { self.key: val }
               accepted_filters.append( grids.GridColumnFilter( label, args) )
           return accepted_filters
    # Grid definition
    title = "Sequencing Requests"
    template = "admin/requests/grid.mako"
    model_class = model.Request
    default_sort_key = "-create_time"
    num_rows_per_page = 50
    preserve_state = True
    use_paging = True
    default_filter = dict( deleted="False", state=model.Request.states.SUBMITTED)
    columns = [
        NameColumn( "Name", 
                    key="name", 
                    model_class=model.Request,
                    link=( lambda item: iff( item.deleted, None, dict( operation="show_request", id=item.id ) ) ),
                    attach_popup=True, 
                    filterable="advanced" ),
        DescriptionColumn( "Description",
                           key='desc',
                           model_class=model.Request,
                           filterable="advanced" ),
        SamplesColumn( "Sample(s)", 
                       link=( lambda item: iff( item.deleted, None, dict( operation="show_request", id=item.id ) ) ), ),
        TypeColumn( "Type",
                    link=( lambda item: iff( item.deleted, None, dict( operation="view_type", id=item.type.id ) ) ), ),
        LastUpdateColumn( "Last update", 
                          format=time_ago ),
        DeletedColumn( "Deleted", 
                       key="deleted", 
                       visible=False, 
                       filterable="advanced" ),
        StateColumn( "State", 
                     model_class=model.Request,
                     event_class=model.RequestEvent,
                     key='state',
                     filterable="advanced",
                     link=( lambda item: iff( item.deleted, None, dict( operation="events", id=item.id ) ) ),
                     ),
        UserColumn( "User",
                    #key='user.email',
                    model_class=model.Request)

    ]
    columns.append( grids.MulticolFilterColumn( "Search", 
                                                cols_to_filter=[ columns[0], columns[1], columns[6] ], 
                                                key="free-text-search",
                                                visible=False,
                                                filterable="standard" ) )
    operations = [
        grids.GridOperation( "Submit", allow_multiple=False, condition=( lambda item: not item.deleted and item.unsubmitted() and item.samples ),
                             confirm="More samples cannot be added to this request once it is submitted. Click OK to submit."  ),
        grids.GridOperation( "Edit", allow_multiple=False, condition=( lambda item: not item.deleted )  ),
        grids.GridOperation( "Reject", allow_multiple=False, condition=( lambda item: not item.deleted and item.submitted() )  ),
        grids.GridOperation( "Delete", allow_multiple=True, condition=( lambda item: not item.deleted )  ),
        grids.GridOperation( "Undelete", condition=( lambda item: item.deleted ) ),    
    ]
    global_actions = [
        grids.GridAction( "Create new request", dict( controller='requests_admin', 
                                                      action='new', 
                                                      select_request_type='True' ) )
    ]


#
# ---- Request Type Gridr ------------------------------------------------------ 
#
class RequestTypeGrid( grids.Grid ):
    # Custom column types
    class NameColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request_type):
            return request_type.name
    class DescriptionColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request_type):
            return request_type.desc
    class RequestFormColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request_type):
            return request_type.request_form.name
    class SampleFormColumn( grids.TextColumn ):
        def get_value(self, trans, grid, request_type):
            return request_type.sample_form.name
    class DeletedColumn( grids.GridColumn ):
       def get_accepted_filters( self ):
           """ Returns a list of accepted filters for this column. """
           accepted_filter_labels_and_vals = { "active" : "False", "deleted" : "True", "all": "All" }
           accepted_filters = []
           for label, val in accepted_filter_labels_and_vals.items():
               args = { self.key: val }
               accepted_filters.append( grids.GridColumnFilter( label, args) )
           return accepted_filters
    # Grid definition
    title = "Requests Types"
    template = "admin/requests/manage_request_types.mako"
    model_class = model.RequestType
    default_sort_key = "-create_time"
    num_rows_per_page = 50
    preserve_state = True
    use_paging = True
    default_filter = dict( deleted="False" )
    columns = [
        NameColumn( "Name", 
                    key="name", 
                    model_class=model.RequestType,
                    link=( lambda item: iff( item.deleted, None, dict( operation="view", id=item.id ) ) ),
                    attach_popup=True,
                    filterable="advanced" ),
        DescriptionColumn( "Description",
                           key='desc',
                           model_class=model.Request,
                           filterable="advanced" ),
        RequestFormColumn( "Request Form", 
                           link=( lambda item: iff( item.deleted, None, dict( operation="view_form", id=item.request_form.id ) ) ), ),
        SampleFormColumn( "Sample Form", 
                           link=( lambda item: iff( item.deleted, None, dict( operation="view_form", id=item.sample_form.id ) ) ), ),
        DeletedColumn( "Deleted", 
                       key="deleted", 
                       visible=False, 
                       filterable="advanced" )
    ]
    columns.append( grids.MulticolFilterColumn( "Search", 
                                                cols_to_filter=[ columns[0], columns[1] ], 
                                                key="free-text-search",
                                                visible=False,
                                                filterable="standard" ) )
    operations = [
        #grids.GridOperation( "Update", allow_multiple=False, condition=( lambda item: not item.deleted  )  ),
        grids.GridOperation( "Delete", allow_multiple=True, condition=( lambda item: not item.deleted  )  ),
        grids.GridOperation( "Undelete", condition=( lambda item: item.deleted ) ),    
    ]
    global_actions = [
        grids.GridAction( "Create new request type", dict( controller='requests_admin', 
                                                           action='create_request_type' ) )
    ]
#
# ---- Request Controller ------------------------------------------------------ 
#

class Requests( BaseController ):
    request_grid = RequestsGrid()
    requesttype_grid = RequestTypeGrid()
    
    @web.expose
    @web.require_admin
    def index( self, trans ):
        return trans.fill_template( "/admin/requests/index.mako" )
    
    @web.expose
    @web.require_admin
    def list( self, trans, **kwd ):
        '''
        List all request made by the current user
        '''
        if 'operation' in kwd:
            operation = kwd['operation'].lower()
            if not kwd.get( 'id', None ):
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='list',
                                                                  status='error',
                                                                  message="Invalid request ID") )
            if operation == "show_request":
                return self.__show_request( trans, **kwd )
            elif operation == "submit":
                return self.__submit_request( trans, **kwd )
            elif operation == "delete":
                return self.__delete_request( trans, **kwd )
            elif operation == "undelete":
                return self.__undelete_request( trans, **kwd )
            elif operation == "edit":
                return self.__edit_request( trans, **kwd )
            elif operation == "reject":
                return self.__reject_request( trans, **kwd )
            elif operation == "events":
                return self.__request_events( trans, **kwd )
            elif operation == "view_type":
                return self.__view_request_type( trans, **kwd )

        # Render the grid view
        return self.request_grid( trans, **kwd )
    def __show_request(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        add_sample = params.get('add_sample', False)
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(kwd['id']) )
        except:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message="Invalid request ID") )
        current_samples = []
        for s in request.samples:
            current_samples.append([s.name, s.values.content])
        if add_sample:
            current_samples.append(['Sample_%i' % (len(current_samples)+1),['' for field in request.type.sample_form.fields]])
        return trans.fill_template( '/admin/requests/show_request.mako',
                                    request=request,
                                    request_details=self.request_details(trans, request.id),
                                    current_samples = current_samples,
                                    sample_copy=self.__copy_sample(current_samples), 
                                    details='hide', edit_mode='False',
                                    msg=msg, messagetype=messagetype )
    @web.expose
    @web.require_admin
    def edit(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( int( params.get( 'request_id', None ) ) )
        except:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message="Invalid request ID",
                                                              **kwd) )
        if params.get('show', False) == 'True':
            return self.__edit_request(trans, id=trans.security.encode_id(request.id), **kwd)
        elif params.get('save_changes_request_button', False) == 'Save changes' \
             or params.get('edit_samples_button', False) == 'Edit samples':
                request_type = trans.sa_session.query( trans.app.model.RequestType ).get( int( params.select_request_type ) )
                if not util.restore_text(params.get('name', '')):
                    msg = 'Please enter the <b>Name</b> of the request'
                    kwd['messagetype'] = 'error'
                    kwd['msg'] = msg
                    kwd['show'] = 'True'
                    return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                      action='edit',
                                                                      **kwd) )
                request = self.__save_request(trans, request, **kwd)
                msg = 'The changes made to the request named %s has been saved' % request.name
                if params.get('save_changes_request_button', False) == 'Save changes':
                    return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                      action='list',
                                                                      message=msg ,
                                                                      status='done') )
                elif params.get('edit_samples_button', False) == 'Edit samples':
                    new_kwd = {}
                    new_kwd['request_id'] = request.id
                    new_kwd['edit_samples_button'] = 'Edit samples'
                    return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                      action='show_request',
                                                                      msg=msg ,
                                                                      messagetype='done',
                                                                      **new_kwd) )
        elif params.get('refresh', False) == 'true':
            return self.__edit_request(trans, id=trans.security.encode_id(request.id), **kwd)
        
    def __edit_request(self, trans, **kwd):
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(kwd['id']) )
        except:
            msg = "Invalid request ID"
            log.warn( msg )
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg) )
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        select_request_type = self.__select_request_type(trans, request.type.id)
        # list of widgets to be rendered on the request form
        widgets = []
        if util.restore_text( params.get( 'name', ''  ) ):
            name = util.restore_text( params.get( 'name', ''  ) )
        else:
            name = request.name
        widgets.append(dict(label='Name', 
                            widget=TextField('name', 40, name), 
                            helptext='(Required)'))
        if util.restore_text( params.get( 'desc', ''  ) ):
            desc = util.restore_text( params.get( 'desc', ''  ) )
        else:
            desc = request.desc
        widgets.append(dict(label='Description', 
                            widget=TextField('desc', 40, desc), 
                            helptext='(Optional)'))
        # libraries selectbox
        libui = self.__library_ui(trans, request.user, request, **kwd)
        widgets = widgets + libui
        widgets = widgets + request.type.request_form.get_widgets( request.user, request.values.content, **kwd )
        return trans.fill_template( '/admin/requests/edit_request.mako',
                                    select_request_type=select_request_type,
                                    request_type=request.type,
                                    request=request,
                                    widgets=widgets,
                                    msg=msg,
                                    messagetype=messagetype)
        return self.__show_request_form(trans)
    def __delete_request(self, trans, **kwd):
        id_list = util.listify( kwd['id'] )
        for id in id_list:
            try:
                request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(id) )
            except:
                msg = "Invalid request ID"
                log.warn( msg )
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='list',
                                                                  status='error',
                                                                  message=msg,
                                                                  **kwd) )
            request.deleted = True
            trans.sa_session.add( request )
            trans.sa_session.flush()
        msg = '%i request(s) has been deleted.' % len(id_list)
        status = 'done'
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          status=status,
                                                          message=msg) )
    def __undelete_request(self, trans, **kwd):
        id_list = util.listify( kwd['id'] )
        for id in id_list:
            try:
                request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(id) )
            except:
                msg = "Invalid request ID"
                log.warn( msg )
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='list',
                                                                  status='error',
                                                                  message=msg,
                                                                  **kwd) )
            request.deleted = False
            trans.sa_session.add( request )
            trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          status='done',
                                                          message='%i request(s) has been undeleted.' % len(id_list) ) )
    def __submit_request(self, trans, **kwd):
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(kwd['id']) )
        except:
            msg = "Invalid request ID"
            log.warn( msg )
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg,
                                                              **kwd) )
        msg = self.__validate(trans, request)
        if msg:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              operation='edit',
                                                              messagetype = 'error',
                                                              msg=msg,
                                                              id=trans.security.encode_id(request.id) ) )
        # change the request state to 'Submitted'
        if request.user.email is not trans.user:
            comments = "Request moved to 'Submitted' state by admin (%s) on behalf of %s." % (trans.user.email, request.user.email)
        else:
            comments = ""
        event = trans.app.model.RequestEvent(request, request.states.SUBMITTED, comments)
        trans.sa_session.add( event )
        trans.sa_session.flush()
        # change the state of each of the samples of thus request
        new_state = request.type.states[0]
        for s in request.samples:
            event = trans.app.model.SampleEvent(s, new_state, 'Samples submitted to the system')
            trans.sa_session.add( event )
        trans.sa_session.add( request )
        trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          id=trans.security.encode_id(request.id),
                                                          status='done',
                                                          message='The request <b>%s</b> has been submitted.' % request.name
                                                          ) )
    def __reject_request(self, trans, **kwd):
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(kwd['id']) )
        except:
            msg = "Invalid request ID"
            log.warn( msg )
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg,
                                                              **kwd) )
        return trans.fill_template( '/admin/requests/reject.mako', 
                                    request=request)
    @web.expose
    @web.require_admin
    def reject(self, trans, **kwd):
        params = util.Params( kwd )
        if params.get('cancel_reject_button', False):
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              operation='show_request',
                                                              id=kwd['id']))
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(kwd['id']) )
        except:
            msg = "Invalid request ID"
            log.warn( msg )
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg,
                                                              **kwd) )
        # validate
        if not params.get('comment', ''):
            return trans.fill_template( '/admin/requests/reject.mako', 
                                        request=request, messagetype='error',
                                        msg='A comment is required for rejecting a request.')
        # create an event with state 'Rejected' for this request
        comments = util.restore_text( params.comment )
        event = trans.app.model.RequestEvent(request, request.states.REJECTED, comments)
        trans.sa_session.add( event )
        trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          status='done',
                                                          message='Request <b>%s</b> has been rejected.' % request.name) )
    
    def __request_events(self, trans, **kwd):
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( trans.security.decode_id(kwd['id']) )
        except:
            msg = "Invalid request ID"
            log.warn( msg )
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg,
                                                              **kwd) )
        events_list = []
        all_events = request.events
        for event in all_events:         
            delta = datetime.utcnow() - event.update_time
            if delta > timedelta( minutes=60 ):
                last_update = '%s hours' % int( delta.seconds / 60 / 60 )
            else:
                last_update = '%s minutes' % int( delta.seconds / 60 )
            events_list.append((event.state, last_update, event.comment))
        return trans.fill_template( '/admin/requests/events.mako', 
                                    events_list=events_list, request=request)
#
#---- Request Creation ----------------------------------------------------------
#    
    def __select_request_type(self, trans, rtid):
        requesttype_list = trans.sa_session.query( trans.app.model.RequestType )\
                                           .order_by( trans.app.model.RequestType.name.asc() )
        rt_ids = ['none']
        for rt in requesttype_list:
            if not rt.deleted:
                rt_ids.append(str(rt.id))
        select_reqtype = SelectField('select_request_type', 
                                     refresh_on_change=True, 
                                     refresh_on_change_values=rt_ids[1:])
        if rtid == 'none':
            select_reqtype.add_option('Select one', 'none', selected=True)
        else:
            select_reqtype.add_option('Select one', 'none')
        for rt in requesttype_list:
            if not rt.deleted:
                if rtid == rt.id:
                    select_reqtype.add_option(rt.name, rt.id, selected=True)
                else:
                    select_reqtype.add_option(rt.name, rt.id)
        return select_reqtype
    @web.expose
    @web.require_admin
    def new(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        if params.get('select_request_type', False) == 'True':
            return trans.fill_template( '/admin/requests/new_request.mako',
                                        select_request_type=self.__select_request_type(trans, 'none'),                                 
                                        widgets=[],                                   
                                        msg=msg,
                                        messagetype=messagetype)
        elif params.get('create', False) == 'True':
            if params.get('create_request_button', False) == 'Save' \
               or params.get('create_request_samples_button', False) == 'Add samples':
                request_type = trans.sa_session.query( trans.app.model.RequestType ).get( int( params.select_request_type ) )
                if not util.restore_text(params.get('name', '')) \
                    or util.restore_text(params.get('select_user', '')) == unicode('none'):
                    msg = 'Please enter the <b>Name</b> of the request and the <b>user</b> on behalf of whom this request will be submitted before saving this request'
                    kwd['create'] = 'True'
                    kwd['messagetype'] = 'error'
                    kwd['msg'] = msg
                    kwd['create_request_button'] = None
                    kwd['create_request_samples_button'] = None
                    return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                      action='new',
                                                                      **kwd) )
                request = self.__save_request(trans, None, **kwd)
                msg = 'The new request named %s has been created' % request.name
                if params.get('create_request_button', False) == 'Save':
                    return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                      action='list',
                                                                      message=msg ,
                                                                      status='done') )
                elif params.get('create_request_samples_button', False) == 'Add samples':
                    new_kwd = {}
                    new_kwd['id'] = trans.security.encode_id(request.id)
                    new_kwd['operation'] = 'show_request'
                    new_kwd['add_sample'] = True
                    return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                      action='list',
                                                                      message=msg ,
                                                                      status='done',
                                                                      **new_kwd) )
            else:
                return self.__show_request_form(trans, **kwd)
        elif params.get('refresh', False) == 'true':
            return self.__show_request_form(trans, **kwd)
    def __show_request_form(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        try:
            request_type = trans.sa_session.query( trans.app.model.RequestType ).get( int( params.select_request_type ) )
        except:
            return trans.fill_template( '/admin/requests/new_request.mako',
                                        select_request_type=self.__select_request_type(trans, 'none'),                                 
                                        widgets=[],                                   
                                        msg=msg,
                                        messagetype=messagetype)
        form_values = None
        select_request_type = self.__select_request_type(trans, request_type.id)
        # user
        user_id = params.get( 'select_user', 'none' )
        try:
            user = trans.sa_session.query( trans.app.model.User ).get( int( user_id ) )
        except:
            user = None
        # list of widgets to be rendered on the request form
        widgets = []
        widgets.append(dict(label='Select user',
                            widget=self.__select_user(trans, user_id),
                            helptext='The request would be submitted on behalf of this user (Required)'))
        widgets.append(dict(label='Name of the Experiment', 
                            widget=TextField('name', 40, 
                                             util.restore_text( params.get( 'name', ''  ) )), 
                            helptext='(Required)'))
        widgets.append(dict(label='Description', 
                            widget=TextField('desc', 40,
                                             util.restore_text( params.get( 'desc', ''  ) )), 
                            helptext='(Optional)'))
        # libraries selectbox
        libui = self.__library_ui(trans, user, **kwd)
        widgets = widgets + libui
        widgets = widgets + request_type.request_form.get_widgets( user, **kwd )
        return trans.fill_template( '/admin/requests/new_request.mako',
                                    select_request_type=select_request_type,
                                    request_type=request_type,                                    
                                    widgets=widgets,
                                    msg=msg,
                                    messagetype=messagetype)
    def __select_user(self, trans, userid):
        user_list = trans.sa_session.query( trans.app.model.User )\
                                    .order_by( trans.app.model.User.email.asc() )
        user_ids = ['none']
        for user in user_list:
            if not user.deleted:
                user_ids.append(str(user.id))
        select_user = SelectField('select_user', 
                                  refresh_on_change=True, 
                                  refresh_on_change_values=user_ids[1:])
        if userid == 'none':
            select_user.add_option('Select one', 'none', selected=True)
        else:
            select_user.add_option('Select one', 'none')
        for user in user_list:
            if not user.deleted:
                if userid == str(user.id):
                    select_user.add_option(user.email, user.id, selected=True)
                else:
                    select_user.add_option(user.email, user.id)
        return select_user
    def __library_ui(self, trans, user, request=None, **kwd):
        '''
        This method creates the data library & folder selectbox for new &
        editing requests. First we get a list of all the libraries accessible to
        the current user and display it in a selectbox. If the user has select an
        existing library then display all the accessible sub folders of the selected 
        data library. 
        '''
        params = util.Params( kwd )
        lib_id = params.get( 'library_id', 'none'  )
        # if editing a request and the user has already associated a library to
        # this request, then set the selected_lib to the request.library
        selected_lib = None
        if request and lib_id == 'none':
            if request.library:
                lib_id = str(request.library.id)
                selected_lib = request.library
        # if new request no user is selected initially, none of the libraries are 
        # listed in the selectfield
        if not user:
            libraries = {}
        else:
            # get all permitted libraries for this user
            all_libraries = trans.sa_session.query( trans.app.model.Library ) \
                                            .filter( trans.app.model.Library.table.c.deleted == False ) \
                                            .order_by( trans.app.model.Library.name )
            roles = user.all_roles()
            actions_to_check = [ trans.app.security_agent.permitted_actions.LIBRARY_ADD ]
            # The libraries dictionary looks like: { library : '1,2' }, library : '3' }
            # Its keys are the libraries that should be displayed for the current user and whose values are a
            # string of comma-separated folder ids, of the associated folders the should NOT be displayed.
            # The folders that should not be displayed may not be a complete list, but it is ultimately passed
            # to the calling method to keep from re-checking the same folders when the library / folder
            # select lists are rendered.
            libraries = {}
            for library in all_libraries:
                can_show, hidden_folder_ids = trans.app.security_agent.show_library_item( user, roles, library, actions_to_check )
                if can_show:
                    libraries[ library ] = hidden_folder_ids
        # create data library selectbox with refresh on change enabled
        lib_id_list = ['new'] + [str(lib.id) for lib in libraries.keys()]
        lib_list = SelectField( 'library_id', refresh_on_change=True, refresh_on_change_values=lib_id_list )
        # fill up the options in the Library selectbox
        # first option 'none' is the value for "Select one" option
        if lib_id == 'none':
            lib_list.add_option('Select one', 'none', selected=True)
        else:
            lib_list.add_option('Select one', 'none')
        # all the libraries available to the selected user
        for lib, hidden_folder_ids in libraries.items():
            if str(lib.id) == lib_id:
                lib_list.add_option(lib.name, lib.id, selected=True)
                selected_lib, selected_hidden_folder_ids = lib, hidden_folder_ids.split(',')
            else:
                lib_list.add_option(lib.name, lib.id)
            lib_list.refresh_on_change_values.append(lib.id)
        # new data library option
        if lib_id == 'new':
            lib_list.add_option('Create a new data library', 'new', selected=True)
        else:
            lib_list.add_option('Create a new data library', 'new')
        # widget
        lib_widget = dict(label='Data library', 
                          widget=lib_list, 
                          helptext='Data library where the resultant dataset will be stored.')
        # show the folder widget only if the user has selected a valid library above
        if selected_lib:
            # when editing a request, either the user has already selected a subfolder or not
            if request:
                if request.folder:
                    current_fid = request.folder.id
                else: 
                    # when a folder not yet associated with the request then the 
                    # the current folder is set to the root_folder of the 
                    # parent data library if present. 
                    if request.library:
                        current_fid = request.library.root_folder.id
                    else:
                        current_fid = params.get( 'folder_id', 'none'  )
            else:
                current_fid = params.get( 'folder_id', 'none'  )
            # create the folder selectbox
            folder_list = SelectField( 'folder_id')
            # first option
            if lib_id == 'none':
                folder_list.add_option('Select one', 'none', selected=True)
            else:
                folder_list.add_option('Select one', 'none')
            # get all show-able folders for the selected library
            showable_folders = trans.app.security_agent.get_showable_folders( user, roles, 
                                                                              selected_lib, 
                                                                              actions_to_check, 
                                                                              selected_hidden_folder_ids )
            for f in showable_folders:
                if str(f.id) == str(current_fid):
                    folder_list.add_option(f.name, f.id, selected=True)
                else:
                    folder_list.add_option(f.name, f.id)
            # folder widget
            folder_widget = dict(label='Folder', 
                                 widget=folder_list, 
                                 helptext='Folder of the selected data library where the resultant dataset will be stored.')
        if lib_id == 'new':
            new_lib = dict(label='Create a new data library', 
                           widget=TextField('new_library_name', 40,
                                     util.restore_text( params.get( 'new_library_name', ''  ) )), 
                           helptext='Enter a name here to request a new data library')
            return [lib_widget, new_lib]
        else:
            if selected_lib:
                return [lib_widget, folder_widget]
            else:
                return [lib_widget]
    def __validate(self, trans, request):
        '''
        Validates the request entered by the user 
        '''
        if not request.samples:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              operation='show_request',
                                                              message='Please add one or more samples to this request before submitting.',
                                                              status='error',
                                                              id=trans.security.encode_id(request.id)) )
        empty_fields = []
        # check rest of the fields of the form
        for index, field in enumerate(request.type.request_form.fields):
            if field['required'] == 'required' and request.values.content[index] in ['', None]:
                empty_fields.append(field['label'])
        if empty_fields:
            msg = 'Fill the following fields of the request <b>%s</b> before submitting<br/>' % request.name
            for ef in empty_fields:
                msg = msg + '<b>' +ef + '</b><br/>'
            return msg
        return None
    def __save_request(self, trans, request=None, **kwd):
        '''
        This method saves a new request if request_id is None. 
        '''
        params = util.Params( kwd )
        request_type = trans.sa_session.query( trans.app.model.RequestType ).get( int( params.select_request_type ) )
        if request:
            user = request.user
        else:
            user = trans.sa_session.query( trans.app.model.User ).get( int( params.get( 'select_user', '' ) ) )
        name = util.restore_text(params.get('name', ''))
        desc = util.restore_text(params.get('desc', ''))
        # library
        try:
            library = trans.sa_session.query( trans.app.model.Library ).get( int( params.get( 'library_id', None ) ) )
        except:
            library = None
        try:
            folder = trans.sa_session.query( trans.app.model.LibraryFolder ).get( int( params.get( 'folder_id', None ) ) )
        except:
            if library:
                folder = library.root_folder
            else:
                folder = None
        # fields
        values = []
        for index, field in enumerate(request_type.request_form.fields):
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
                    trans.sa_session.refresh( trans.user )
                    values.append(int(user_address.id))
                elif value == unicode('none'):
                    values.append('')
                else:
                    values.append(int(value))
            elif field['type'] == 'CheckboxField':
                values.append(CheckboxField.is_checked( params.get('field_%i' % index, '') )) 
            else:
                values.append(util.restore_text(params.get('field_%i' % index, '')))
        form_values = trans.app.model.FormValues(request_type.request_form, values)
        trans.sa_session.add( form_values )
        trans.sa_session.flush()
        if not request:
            request = trans.app.model.Request(name, desc, request_type, 
                                              user, form_values,
                                              library=library, folder=folder)
            trans.sa_session.add( request )
            trans.sa_session.flush()
            trans.sa_session.refresh( request )
            # create an event with state 'New' for this new request
            if request.user.email is not trans.user:
                comments = "Request created by admin (%s) on behalf of %s." % (trans.user.email, request.user.email)
            else:
                comments = "Request created."
            event = trans.app.model.RequestEvent(request, request.states.NEW, comments)
            trans.sa_session.add( event )
            trans.sa_session.flush()
        else:
            request.name = name
            request.desc = desc
            request.type = request_type
            request.user = user
            request.values = form_values
            request.library = library
            request.folder = folder
            trans.sa_session.add( request )
            trans.sa_session.flush()
        
        return request


#
#---- Request Page ----------------------------------------------------------
#    
    def __update_samples(self, request, **kwd):
        '''
        This method retrieves all the user entered sample information and
        returns an list of all the samples and their field values
        '''
        params = util.Params( kwd )
        current_samples = []
        for s in request.samples:
            current_samples.append([s.name, s.values.content])
        index = len(request.samples) 
        while True:
            if params.get( 'sample_%i_name' % index, ''  ):
                sample_index = index
                sample_name = util.restore_text( params.get( 'sample_%i_name' % sample_index, ''  ) )
                sample_values = []
                for field_index in range(len(request.type.sample_form.fields)):
                    sample_values.append(util.restore_text( params.get( 'sample_%i_field_%i' % (sample_index, field_index), ''  ) ))
                current_samples.append([sample_name, sample_values])
                index = index + 1
            else:
                break
        details = params.get( 'details', 'hide' )
        edit_mode = params.get( 'edit_mode', 'False' )
        return current_samples, details, edit_mode
    def __copy_sample(self, current_samples):
        copy_list = SelectField('copy_sample')
        copy_list.add_option('None', -1, selected=True)  
        for i, s in enumerate(current_samples):
            copy_list.add_option(s[0], i)
        return copy_list   
    @web.expose
    @web.require_login( "create/submit sequencing requests" )
    def show_request(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( int( params.get( 'request_id', None ) ) )
        except:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message="Invalid request ID",
                                                              **kwd) )
        # get the user entered sample details
        current_samples, details, edit_mode = self.__update_samples( request, **kwd )
        if params.get('import_samples_button', False) == 'Import samples':
            try:
                file_obj = params.get('file_data', '')
                import csv
                reader = csv.reader(file_obj.file)
                for row in reader:
                    current_samples.append([row[0], row[1:]])  
                return trans.fill_template( '/admin/requests/show_request.mako',
                                            request=request,
                                            request_details=self.request_details(trans, request.id),
                                            current_samples=current_samples,
                                            sample_copy=self.__copy_sample(current_samples), 
                                            details=details,
                                            edit_mode=edit_mode)
            except:
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='list',
                                                                  status='error',
                                                                  message='Error in importing samples file',
                                                                  **kwd))
        elif params.get('add_sample_button', False) == 'Add New':
            # add an empty or filled sample
            # if the user has selected a sample no. to copy then copy the contents 
            # of the src sample to the new sample else an empty sample
            src_sample_index = int(params.get( 'copy_sample', -1  ))
            if src_sample_index == -1:
                # empty sample
                current_samples.append(['Sample_%i' % (len(current_samples)+1),['' for field in request.type.sample_form.fields]])
            else:
                current_samples.append([current_samples[src_sample_index][0]+'_%i' % (len(current_samples)+1),
                                                                  [val for val in current_samples[src_sample_index][1]]])
            return trans.fill_template( '/admin/requests/show_request.mako',
                                        request=request,
                                        request_details=self.request_details(trans, request.id),
                                        current_samples=current_samples,
                                        sample_copy=self.__copy_sample(current_samples), 
                                        details=details,
                                        edit_mode=edit_mode)
        elif params.get('save_samples_button', False) == 'Save':
            # check for duplicate sample names
            msg = ''
            for index in range(len(current_samples)-len(request.samples)):
                sample_index = index + len(request.samples)
                sample_name = current_samples[sample_index][0]
                if not sample_name.strip():
                    msg = 'Please enter the name of sample number %i' % sample_index
                    break
                count = 0
                for i in range(len(current_samples)):
                    if sample_name == current_samples[i][0]:
                        count = count + 1
                if count > 1: 
                    msg = "This request has <b>%i</b> samples with the name <b>%s</b>.\nSamples belonging to a request must have unique names." % (count, sample_name)
                    break
            if msg:
                return trans.fill_template( '/admin/requests/show_request.mako',
                                            request=request,
                                            request_details=self.request_details(trans, request.id),
                                            current_samples = current_samples,
                                            sample_copy=self.__copy_sample(current_samples), 
                                            details=details, edit_mode=edit_mode,
                                            messagetype='error', msg=msg)
            # save all the new/unsaved samples entered by the user
            if edit_mode == 'False':
                for index in range(len(current_samples)-len(request.samples)):
                    sample_index = len(request.samples)
                    sample_name = util.restore_text( params.get( 'sample_%i_name' % sample_index, ''  ) )
                    sample_values = []
                    for field_index in range(len(request.type.sample_form.fields)):
                        sample_values.append(util.restore_text( params.get( 'sample_%i_field_%i' % (sample_index, field_index), ''  ) ))
                    form_values = trans.app.model.FormValues(request.type.sample_form, sample_values)
                    trans.sa_session.add( form_values )
                    trans.sa_session.flush()                    
                    s = trans.app.model.Sample(sample_name, '', request, form_values)
                    trans.sa_session.add( s )
                    trans.sa_session.flush()
            else:
                for index in range(len(current_samples)):
                    sample_index = index
                    sample_name = current_samples[sample_index][0]
                    new_sample_name = util.restore_text( params.get( 'sample_%i_name' % sample_index, ''  ) )
                    sample_values = []
                    for field_index in range(len(request.type.sample_form.fields)):
                        sample_values.append(util.restore_text( params.get( 'sample_%i_field_%i' % (sample_index, field_index), ''  ) ))
                    sample = request.has_sample(sample_name)
                    if sample:
                        form_values = trans.sa_session.query( trans.app.model.FormValues ).get( sample.values.id )
                        form_values.content = sample_values
                        trans.sa_session.add( form_values )
                        trans.sa_session.flush()
                        sample.name = new_sample_name
                        trans.sa_session.add( sample )
                        trans.sa_session.flush()
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          operation='show_request',
                                                          id=trans.security.encode_id(request.id)) )
        elif params.get('edit_samples_button', False) == 'Edit samples':
            edit_mode = 'True'
            return trans.fill_template( '/admin/requests/show_request.mako',
                                        request=request,
                                        request_details=self.request_details(trans, request.id),
                                        current_samples=current_samples,
                                        sample_copy=self.__copy_sample(current_samples), 
                                        details=details,
                                        edit_mode=edit_mode)
        elif params.get('cancel_changes_button', False) == 'Cancel':
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          operation='show_request',
                                                          id=trans.security.encode_id(request.id)) )

            
    @web.expose
    @web.require_login( "create/submit sequencing requests" )
    def delete_sample(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        request = trans.sa_session.query( trans.app.model.Request ).get( int( params.get( 'request_id', 0 ) ) )
        current_samples, details, edit_mode = self.__update_samples( request, **kwd )
        sample_index = int(params.get('sample_id', 0))
        sample_name = current_samples[sample_index][0]
        s = request.has_sample(sample_name)
        if s:
            trans.sa_session.delete( s )
            trans.sa_session.flush()
        del current_samples[sample_index]  
        return trans.fill_template( '/admin/requests/show_request.mako',
                                    request=request,
                                    request_details=self.request_details(trans, request.id),
                                    current_samples = current_samples,
                                    sample_copy=self.__copy_sample(current_samples), 
                                    details=details,
                                    edit_mode=edit_mode)
        
    @web.expose
    @web.require_login( "create/submit sequencing requests" )
    def toggle_request_details(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        request = trans.sa_session.query( trans.app.model.Request ).get( int( params.get( 'request_id', 0 ) ) )
        current_samples, details, edit_mode = self.__update_samples( request, **kwd )
        return trans.fill_template( '/admin/requests/show_request.mako',
                                    request=request,
                                    request_details=self.request_details(trans, request.id),
                                    current_samples = current_samples,
                                    sample_copy=self.__copy_sample(current_samples), 
                                    details=details,
                                    edit_mode=edit_mode)
    @web.expose
    @web.require_admin
    def request_details(self, trans, id):
        '''
        Shows the request details
        '''
        request = trans.sa_session.query( trans.app.model.Request ).get( id )
        # list of widgets to be rendered on the request form
        request_details = []
        # main details
        request_details.append(dict(label='User', 
                                    value=str(request.user.email), 
                                    helptext=''))
        request_details.append(dict(label='Description', 
                                    value=request.desc, 
                                    helptext=''))
        request_details.append(dict(label='Type', 
                                    value=request.type.name, 
                                    helptext=''))
        request_details.append(dict(label='State', 
                                    value=request.state(), 
                                    helptext=''))
        request_details.append(dict(label='Date created', 
                                    value=request.create_time, 
                                    helptext=''))
        # library associated
        if request.library:
			value=request.library.name
        else:
			value = None
        request_details.append(dict(label='Data library', 
                                    value=value, 
                                    helptext='Data library where the resultant dataset will be stored'))
        # folder associated
        if request.folder:
            value = request.folder.name
        else:
            value = None
        request_details.append( dict( label='Data library folder', 
                                      value=value, 
                                      helptext='Data library folder where the resultant dataset will be stored' ) )

        # form fields
        for index, field in enumerate(request.type.request_form.fields):
            if field['required']:
                req = 'Required'
            else:
                req = 'Optional'
            if field['type'] == 'AddressField':
                if request.values.content[index]:
                    request_details.append(dict(label=field['label'],
                                                value=trans.sa_session.query( trans.app.model.UserAddress ).get( int( request.values.content[index] ) ).get_html(),
                                                helptext=field['helptext']+' ('+req+')'))
                else:
                    request_details.append(dict(label=field['label'],
                                                value=None,
                                                helptext=field['helptext']+' ('+req+')'))
            else: 
                request_details.append(dict(label=field['label'],
                                            value=request.values.content[index],
                                            helptext=field['helptext']+' ('+req+')'))
        return request_details
    @web.expose
    @web.require_admin
    def bar_codes(self, trans, **kwd):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )
        request_id = params.get( 'request_id', None )
        if request_id:
            request = trans.sa_session.query( trans.app.model.Request ).get( int( request_id ))
        if not request:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message="Invalid request ID",
                                                              **kwd) )
        widgets = []
        for index, sample in enumerate(request.samples):
            if sample.bar_code:
                bc = sample.bar_code
            else:
                bc = util.restore_text(params.get('sample_%i_bar_code' % index, ''))
            widgets.append(TextField('sample_%i_bar_code' % index, 
                                     40, 
                                     bc))
        return trans.fill_template( '/admin/samples/bar_codes.mako', 
                                    samples_list=[s for s in request.samples],
                                    user=request.user, request=request, widgets=widgets, 
                                    messagetype=messagetype,
                                    msg=msg)
    @web.expose
    @web.require_admin
    def save_bar_codes(self, trans, **kwd):
        params = util.Params( kwd )
        try:
            request = trans.sa_session.query( trans.app.model.Request ).get( int( params.get( 'request_id', None ) ) )
        except:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message="Invalid request ID",
                                                              **kwd) )
        # validate 
        # bar codes need to be globally unique
        msg = ''
        for index in range(len(request.samples)):
            bar_code = util.restore_text(params.get('sample_%i_bar_code' % index, ''))
            # check for empty bar code
            if not bar_code.strip():
                msg = 'Please fill the barcode for sample <b>%s</b>.' % request.samples[index].name
                break
            # check all the unsaved bar codes
            count = 0
            for i in range(len(request.samples)):
                if bar_code == util.restore_text(params.get('sample_%i_bar_code' % i, '')):
                    count = count + 1
            if count > 1:
                msg = '''The barcode <b>%s</b> of sample <b>%s</b> belongs
                         another sample in this request. The sample barcodes must
                         be unique throughout the system''' % \
                         (bar_code, request.samples[index].name)
                break
            # check all the saved bar codes
            all_samples = trans.sa_session.query( trans.app.model.Sample )
            for sample in all_samples:
                if bar_code == sample.bar_code:
                    msg = '''The bar code <b>%s</b> of sample <b>%s</b>  
                             belongs another sample. The sample bar codes must be 
                             unique throughout the system''' % \
                             (bar_code, request.samples[index].name)
                    break
            if msg:
                break
        if msg:
            widgets = []
            for index, sample in enumerate(request.samples):
                if sample.bar_code:
                    bc = sample.bar_code
                else:
                    bc = util.restore_text(params.get('sample_%i_bar_code' % index, ''))
                widgets.append(TextField('sample_%i_bar_code' % index, 
                                         40, 
                                         util.restore_text(params.get('sample_%i_bar_code' % index, ''))))
            return trans.fill_template( '/admin/samples/bar_codes.mako', 
                                        samples_list=[s for s in request.samples],
                                        user=request.user, request=request, widgets=widgets, messagetype='error',
                                        msg=msg)
        # now save the bar codes
        for index, sample in enumerate(request.samples):
            bar_code = util.restore_text(params.get('sample_%i_bar_code' % index, ''))
            sample.bar_code = bar_code
            trans.sa_session.add( sample )
            trans.sa_session.flush()
        # change the state of all the samples to the next state
        # get the new state
        new_state = request.type.states[1]
        for s in request.samples:
            event = trans.app.model.SampleEvent(s, new_state, 'Bar code added to this sample')
            trans.sa_session.add( event )
            trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='list',
                                                          operation='show_request',
                                                          id=trans.security.encode_id(request.id),
                                                          msg='Bar codes have been saved for this request',
                                                          messagetype='done'))
    def __set_request_state( self, trans, request ):
        # check if all the samples of the current request are in the final state
        complete = True 
        for s in request.samples:
            if s.current_state().id != request.type.states[-1].id:
                complete = False
        if complete:
            # change the request state to 'Complete'
            comments = "All samples of this request are in the last sample state (%s)." % request.type.states[-1].name
            event = trans.app.model.RequestEvent(request, request.states.COMPLETE, comments)
            trans.sa_session.add( event )
            trans.sa_session.flush()
#        trans.sa_session.add( request )
#        trans.sa_session.flush()
    def change_state(self, trans, sample):
        possible_states = sample.request.type.states 
        curr_state = sample.current_state() 
        states_input = SelectField('select_state')
        for state in possible_states:
            if curr_state.name == state.name:
                states_input.add_option(state.name+' (Current)', state.id, selected=True)
            else:
                states_input.add_option(state.name, state.id)
        widgets = []
        widgets.append(('Select the new state of the sample from the list of possible state(s)',
                      states_input))
        widgets.append(('Comments', TextArea('comment')))
        title = 'Change current state'
        return widgets, title
    @web.expose
    @web.require_admin
    def save_state(self, trans, **kwd):
        params = util.Params( kwd )
        try:
            sample_id = int(params.get('sample_id', False))
            sample = trans.sa_session.query( trans.app.model.Sample ).get( sample_id )
        except:
            msg = "Invalid sample ID"
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg,
                                                              **kwd) )
        comments = util.restore_text( params.comment )
        selected_state = int( params.select_state )
        new_state = trans.sa_session.query( trans.app.model.SampleState ) \
                                    .filter( and_( trans.app.model.SampleState.table.c.request_type_id == sample.request.type.id,
                                                   trans.app.model.SampleState.table.c.id == selected_state ) ) \
                                    .first()
        event = trans.app.model.SampleEvent(sample, new_state, comments)
        trans.sa_session.add( event )
        trans.sa_session.flush()
        self.__set_request_state( trans, sample.request )
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='show_events',
                                                          sample_id=sample.id))
    @web.expose
    @web.require_admin
    def show_events(self, trans, **kwd):
        params = util.Params( kwd )
        try:
            sample_id = int(params.get('sample_id', False))
            sample = trans.sa_session.query( trans.app.model.Sample ).get( sample_id )
        except:
            msg = "Invalid sample ID"
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='list',
                                                              status='error',
                                                              message=msg,
                                                              **kwd) )
        events_list = []
        all_events = sample.events
        for event in all_events:         
            delta = datetime.utcnow() - event.update_time
            if delta > timedelta( minutes=60 ):
                last_update = '%s hours' % int( delta.seconds / 60 / 60 )
            else:
                last_update = '%s minutes' % int( delta.seconds / 60 )
            events_list.append((event.state.name, event.state.desc, last_update, event.comment))
        widgets, title = self.change_state(trans, sample)
        return trans.fill_template( '/admin/samples/events.mako', 
                                    events_list=events_list,
                                    sample=sample, widgets=widgets, title=title)
    
##
#### Request Type Stuff ###################################################
##
    @web.expose
    @web.require_admin
    def manage_request_types( self, trans, **kwd ):
        if 'operation' in kwd:
            operation = kwd['operation'].lower()
            if not kwd.get( 'id', None ):
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='manage_request_types',
                                                                  status='error',
                                                                  message="Invalid requesttype ID") )
            if operation == "view":
                return self.__view_request_type( trans, **kwd )
            elif operation == "view_form":
                return self.__view_form( trans, **kwd )
            elif operation == "delete":
                return self.__delete_request_type( trans, **kwd )
            elif operation == "undelete":
                return self.__undelete_request_type( trans, **kwd )
#            elif operation == "update":
#                return self.__edit_request( trans, **kwd )
        # Render the grid view
        return self.requesttype_grid( trans, **kwd )
    def __view_request_type(self, trans, **kwd):
        try:
            rt = trans.sa_session.query( trans.app.model.RequestType ).get( trans.security.decode_id(kwd['id']) )
        except:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='manage_request_types',
                                                              status='error',
                                                              message="Invalid requesttype ID") )
        return trans.fill_template( '/admin/requests/view_request_type.mako', 
                                    request_type=rt,
                                    forms=get_all_forms( trans ),
                                    states_list=rt.states )
    def __view_form(self, trans, **kwd):
        try:
            fd = trans.sa_session.query( trans.app.model.FormDefinition ).get( trans.security.decode_id(kwd['id']) )
        except:
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='manage_request_types',
                                                              status='error',
                                                              message="Invalid form ID") )
        return trans.fill_template( '/admin/forms/show_form_read_only.mako',
                                    form=fd )

    @web.expose
    @web.require_admin
    def create_request_type( self, trans, **kwd ):
        params = util.Params( kwd )
        msg = util.restore_text( params.get( 'msg', ''  ) )
        messagetype = params.get( 'messagetype', 'done' )   
        if params.get( 'add_state_button', False ):
            rt_info, rt_states = self.__create_request_type_form(trans, **kwd)
            rt_states.append(("", ""))
            return trans.fill_template( '/admin/requests/create_request_type.mako', 
                                        rt_info_widgets=rt_info,
                                        rt_states_widgets=rt_states,
                                        msg=msg,
                                        messagetype=messagetype)
        elif params.get( 'remove_state_button', False ):
            rt_info, rt_states = self.__create_request_type_form(trans, **kwd)
            index = int(params.get( 'remove_state_button', '' ).split(" ")[2])
            del rt_states[index-1]
            return trans.fill_template( '/admin/requests/create_request_type.mako', 
                                        rt_info_widgets=rt_info,
                                        rt_states_widgets=rt_states,
                                        msg=msg,
                                        messagetype=messagetype)
        elif params.get( 'save_request_type', False ):
            st, msg = self.__save_request_type(trans, **kwd)
            if not st:
                return trans.fill_template( '/admin/requests/create_request_type.mako', 
                                            forms=get_all_forms( trans ),
                                            msg=msg,
                                            messagetype='error')
            return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                              action='manage_request_types',
                                                              message='Request type <b>%s</b> has been created' % st.name,
                                                              status='done') )
        else:
            rt_info, rt_states = self.__create_request_type_form(trans, **kwd)
            return trans.fill_template( '/admin/requests/create_request_type.mako',
                                        rt_info_widgets=rt_info,
                                        rt_states_widgets=rt_states,
                                        msg=msg,
                                        messagetype=messagetype)
    def __create_request_type_form(self, trans, **kwd):
        request_forms=get_all_forms( trans, 
                                     filter=dict(deleted=False),
                                     form_type=trans.app.model.FormDefinition.types.REQUEST )
        sample_forms=get_all_forms( trans, 
                                    filter=dict(deleted=False),
                                    form_type=trans.app.model.FormDefinition.types.SAMPLE )
        if not len(request_forms) or not len(sample_forms):
            return [],[]
        params = util.Params( kwd )
        rt_info = []
        rt_info.append(dict(label='Name', 
                            widget=TextField('name', 40, util.restore_text( params.get( 'name', ''  ) ) ) ))
        rt_info.append(dict(label='Description', 
                            widget=TextField('desc', 40, util.restore_text( params.get( 'desc', ''  ) ) ) ))

        rf_selectbox = SelectField('request_form_id')
        for fd in request_forms:
            if str(fd.id) == params.get( 'request_form_id', ''  ):
                rf_selectbox.add_option(fd.name, fd.id, selected=True)
            else:
                rf_selectbox.add_option(fd.name, fd.id)
        rt_info.append(dict(label='Request form', 
                            widget=rf_selectbox ))

        sf_selectbox = SelectField('sample_form_id')
        for fd in sample_forms:
            if str(fd.id) == params.get( 'sample_form_id', ''  ):
                sf_selectbox.add_option(fd.name, fd.id, selected=True)
            else:
                sf_selectbox.add_option(fd.name, fd.id)
        rt_info.append(dict(label='Sample form', 
                            widget=sf_selectbox ))
        # possible sample states
        rt_states = []
        i=0
        while True:
            if kwd.has_key( 'state_name_%i' % i ):
                rt_states.append((params.get( 'state_name_%i' % i, ''  ), 
                                  params.get( 'state_desc_%i' % i, ''  )))
                i=i+1
            else:
                break
        return rt_info, rt_states
    
    def __save_request_type(self, trans, **kwd):
        params = util.Params( kwd )
        rt = trans.app.model.RequestType() 
        rt.name = util.restore_text( params.get( 'name', ''  ) ) 
        rt.desc = util.restore_text( params.get( 'desc', '' ) )
        rt.request_form = trans.sa_session.query( trans.app.model.FormDefinition ).get( int( params.request_form_id ) )
        rt.sample_form = trans.sa_session.query( trans.app.model.FormDefinition ).get( int( params.sample_form_id ) )
        trans.sa_session.add( rt )
        trans.sa_session.flush()
        # set sample states
        ss_list = trans.sa_session.query( trans.app.model.SampleState ).filter( trans.app.model.SampleState.table.c.request_type_id == rt.id )
        for ss in ss_list:
            trans.sa_session.delete( ss )
            trans.sa_session.flush()
        i=0
        while True:
            if kwd.has_key( 'state_name_%i' % i ):
                name = util.restore_text( params.get( 'state_name_%i' % i, None ))
                desc = util.restore_text( params.get( 'state_desc_%i' % i, None ))
                ss = trans.app.model.SampleState(name, desc, rt) 
                trans.sa_session.add( ss )
                trans.sa_session.flush()
                i = i + 1
            else:
                break
        msg = "The new request type named '%s' with %s state(s) has been created" % (rt.name, i)
        return rt, msg
    def __delete_request_type( self, trans, **kwd ):
        id_list = util.listify( kwd['id'] )
        for id in id_list:
            try:
                rt = trans.sa_session.query( trans.app.model.RequestType ).get( trans.security.decode_id(id) )
            except:
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='manage_request_types',
                                                                  msg='Invalid request type ID',
                                                                  messagetype='error') )
            rt.deleted = True
            trans.sa_session.add( rt )
            trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='manage_request_types',
                                                          msg='%i request type(s) has been deleted' % len(id_list),
                                                          messagetype='done') )
    def __undelete_request_type( self, trans, **kwd ):
        id_list = util.listify( kwd['id'] )
        for id in id_list:
            try:
                rt = trans.sa_session.query( trans.app.model.RequestType ).get( trans.security.decode_id(id) )
            except:
                return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                                  action='manage_request_types',
                                                                  msg='Invalid request type ID',
                                                                  messagetype='error') )
            rt.deleted = False
            trans.sa_session.add( rt )
            trans.sa_session.flush()
        return trans.response.send_redirect( web.url_for( controller='requests_admin',
                                                          action='manage_request_types',
                                                          msg='%i request type(s) has been undeleted' % len(id_list),
                                                          messagetype='done') )
