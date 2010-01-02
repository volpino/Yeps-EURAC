from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381897.152997
_template_filename=u'templates/root/history_common.mako'
_template_uri=u'root/history_common.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['render_dataset']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        n_ = context.get('n_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        _=n_ 
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['_'] if __M_key in __M_locals_builtin()]))
        __M_writer(u'\n')
        # SOURCE LINE 136
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_dataset(context,data,hid,show_deleted_on_refresh=False,user_owns_dataset=True):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        app = context.get('app', UNDEFINED)
        def render_dataset(data,hid,show_deleted_on_refresh=False,user_owns_dataset=True):
            return render_render_dataset(context,data,hid,show_deleted_on_refresh,user_owns_dataset)
        request = context.get('request', UNDEFINED)
        len = context.get('len', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n    <a name="')
        # SOURCE LINE 4
        __M_writer(unicode(trans.security.encode_id( data.id )))
        __M_writer(u'"></a>\n    ')
        # SOURCE LINE 5

        if data.state in ['no state','',None]:
            data_state = "queued"
        else:
            data_state = data.state
        user, roles = trans.get_user_and_roles()
            
        
        # SOURCE LINE 11
        __M_writer(u'\n')
        # SOURCE LINE 12
        if not trans.user_is_admin() and not trans.app.security_agent.can_access_dataset( roles, data.dataset ):
            # SOURCE LINE 13
            __M_writer(u'        <div class="historyItemWrapper historyItem historyItem-')
            __M_writer(unicode(data_state))
            __M_writer(u' historyItem-noPermission" id="historyItem-')
            __M_writer(unicode(data.id))
            __M_writer(u'">\n')
            # SOURCE LINE 14
        else:
            # SOURCE LINE 15
            __M_writer(u'        <div class="historyItemWrapper historyItem historyItem-')
            __M_writer(unicode(data_state))
            __M_writer(u'" id="historyItem-')
            __M_writer(unicode(data.id))
            __M_writer(u'">\n')
        # SOURCE LINE 17
        __M_writer(u'        \n')
        # SOURCE LINE 18
        if data.deleted:
            # SOURCE LINE 19
            __M_writer(u'        <div class="warningmessagesmall">\n            <strong>This dataset has been deleted. Click <a href="')
            # SOURCE LINE 20
            __M_writer(unicode(h.url_for( controller='dataset', action='undelete', id=data.id )))
            __M_writer(u'" class="historyItemUndelete" id="historyItemUndeleter-')
            __M_writer(unicode(data.id))
            __M_writer(u'" target="galaxy_history">here</a> to undelete.</strong>\n        </div>\n')
        # SOURCE LINE 23
        __M_writer(u'\n')
        # SOURCE LINE 25
        __M_writer(u'\t<div style="overflow: hidden;" class="historyItemTitleBar">\t\t\n\t    <div class="historyItemButtons">\n')
        # SOURCE LINE 27
        if data_state == "upload":
            # SOURCE LINE 31
            __M_writer(u'    \t        <img src="')
            __M_writer(unicode(h.url_for('/static/images/eye_icon_grey.png')))
            __M_writer(u'" width=\'16\' height=\'16\' alt=\'display data\' title=\'display data\' class=\'button display\' border=\'0\'>\n')
            # SOURCE LINE 32
            if user_owns_dataset:
                # SOURCE LINE 33
                __M_writer(u'    \t            <img src="')
                __M_writer(unicode(h.url_for('/static/images/pencil_icon_grey.png')))
                __M_writer(u'" width=\'16\' height=\'16\' alt=\'edit attributes\' title=\'edit attributes\' class=\'button edit\' border=\'0\'>\n')
            # SOURCE LINE 35
        else:
            # SOURCE LINE 36
            __M_writer(u'    \t        <a class="icon-button display" title="display data" href="')
            __M_writer(unicode(h.url_for( controller='dataset', action='display', dataset_id=trans.security.encode_id( data.id ), preview=True, filename='' )))
            __M_writer(u'" target="galaxy_main"></a>\n')
            # SOURCE LINE 37
            if user_owns_dataset:
                # SOURCE LINE 38
                __M_writer(u'    \t            <a class="icon-button edit" title="edit attributes" href="')
                __M_writer(unicode(h.url_for( controller='root', action='edit', id=data.id )))
                __M_writer(u'" target="galaxy_main"></a>\n')
        # SOURCE LINE 41
        if user_owns_dataset:
            # SOURCE LINE 42
            __M_writer(u'\t            <a class="icon-button delete" title="delete" href="')
            __M_writer(unicode(h.url_for( action='delete', id=data.id, show_deleted_on_refresh=show_deleted_on_refresh )))
            __M_writer(u'" id="historyItemDeleter-')
            __M_writer(unicode(data.id))
            __M_writer(u'"></a>\n')
        # SOURCE LINE 44
        __M_writer(u'\t    </div>\n\t    <span class="state-icon"></span>\n\t    <span class="historyItemTitle"><b>')
        # SOURCE LINE 46
        __M_writer(unicode(hid))
        __M_writer(u': ')
        __M_writer(unicode(data.display_name()))
        __M_writer(u'</b></span>\n\t</div>\n        \n')
        # SOURCE LINE 50
        __M_writer(u'        \n        <div id="info')
        # SOURCE LINE 51
        __M_writer(unicode(data.id))
        __M_writer(u'" class="historyItemBody">\n')
        # SOURCE LINE 52
        if not trans.user_is_admin() and not trans.app.security_agent.can_access_dataset( roles, data.dataset ):
            # SOURCE LINE 53
            __M_writer(u'                <div>You do not have permission to view this dataset.</div>\n')
            # SOURCE LINE 54
        elif data_state == "upload":
            # SOURCE LINE 55
            __M_writer(u'                <div>Dataset is uploading</div>\n')
            # SOURCE LINE 56
        elif data_state == "queued":
            # SOURCE LINE 57
            __M_writer(u'                <div>')
            __M_writer(unicode(_('Job is waiting to run')))
            __M_writer(u'</div>\n')
            # SOURCE LINE 58
        elif data_state == "running":
            # SOURCE LINE 59
            __M_writer(u'                <div>')
            __M_writer(unicode(_('Job is currently running')))
            __M_writer(u'</div>\n')
            # SOURCE LINE 60
        elif data_state == "error":
            # SOURCE LINE 61
            __M_writer(u'                <div>\n                    An error occurred running this job: <i>')
            # SOURCE LINE 62
            __M_writer(unicode(data.display_info().strip()))
            __M_writer(u'</i>\n                </div>\n\t\t<div>\n\t\t    <a href="')
            # SOURCE LINE 65
            __M_writer(unicode(h.url_for( controller='dataset', action='errors', id=data.id )))
            __M_writer(u'" target="galaxy_main">report this error</a>\n\t\t    | <a href="')
            # SOURCE LINE 66
            __M_writer(unicode(h.url_for( controller='tool_runner', action='rerun', id=data.id )))
            __M_writer(u'" target="galaxy_main">rerun</a>\n\t\t</div>\n')
            # SOURCE LINE 68
        elif data_state == "discarded":
            # SOURCE LINE 69
            __M_writer(u'                <div>\n                    The job creating this dataset was cancelled before completion.\n                </div>\n')
            # SOURCE LINE 72
        elif data_state == 'setting_metadata':
            # SOURCE LINE 73
            __M_writer(u'                <div>')
            __M_writer(unicode(_('Metadata is being Auto-Detected.')))
            __M_writer(u'</div>\n')
            # SOURCE LINE 74
        elif data_state == "empty":
            # SOURCE LINE 75
            __M_writer(u'                <div>')
            __M_writer(unicode(_('No data: ')))
            __M_writer(u'<i>')
            __M_writer(unicode(data.display_info()))
            __M_writer(u'</i></div>\n')
            # SOURCE LINE 76
        elif data_state == "ok":
            # SOURCE LINE 77
            __M_writer(u'                <div>\n                    ')
            # SOURCE LINE 78
            __M_writer(unicode(data.blurb))
            __M_writer(u',\n                    format: <span class="')
            # SOURCE LINE 79
            __M_writer(unicode(data.ext))
            __M_writer(u'">')
            __M_writer(unicode(data.ext))
            __M_writer(u'</span>, \n                    database:\n')
            # SOURCE LINE 81
            if data.dbkey == '?':
                # SOURCE LINE 82
                __M_writer(u'                        <a href="')
                __M_writer(unicode(h.url_for( controller='root', action='edit', id=data.id )))
                __M_writer(u'" target="galaxy_main">')
                __M_writer(unicode(_(data.dbkey)))
                __M_writer(u'</a>\n')
                # SOURCE LINE 83
            else:
                # SOURCE LINE 84
                __M_writer(u'                        <span class="')
                __M_writer(unicode(data.dbkey))
                __M_writer(u'">')
                __M_writer(unicode(_(data.dbkey)))
                __M_writer(u'</span>\n')
            # SOURCE LINE 86
            __M_writer(u'                </div>\n                <div class="info">')
            # SOURCE LINE 87
            __M_writer(unicode(_('Info: ')))
            __M_writer(unicode(data.display_info()))
            __M_writer(u'</div>\n                <div> \n')
            # SOURCE LINE 89
            if data.has_data:
                # SOURCE LINE 90
                __M_writer(u'                        <a href="')
                __M_writer(unicode(h.url_for( controller='dataset', action='display', dataset_id=trans.security.encode_id( data.id ), to_ext=data.ext )))
                __M_writer(u'">save</a>\n')
                # SOURCE LINE 91
                if user_owns_dataset:
                    # SOURCE LINE 92
                    __M_writer(u'\t\t\t                | <a href="')
                    __M_writer(unicode(h.url_for( controller='tool_runner', action='rerun', id=data.id )))
                    __M_writer(u'" target="galaxy_main">rerun</a>\n')
                # SOURCE LINE 94
                for display_app in data.datatype.get_display_types():
                    # SOURCE LINE 95
                    __M_writer(u'                            ')
                    target_frame, display_links = data.datatype.get_display_links( data, display_app, app, request.base ) 
                    
                    __M_writer(u'\n')
                    # SOURCE LINE 96
                    if len( display_links ) > 0:
                        # SOURCE LINE 97
                        __M_writer(u'                                | ')
                        __M_writer(unicode(data.datatype.get_display_label(display_app)))
                        __M_writer(u'\n')
                        # SOURCE LINE 98
                        for display_name, display_link in display_links:
                            # SOURCE LINE 99
                            __M_writer(u'\t\t\t\t    <a target="')
                            __M_writer(unicode(target_frame))
                            __M_writer(u'" href="')
                            __M_writer(unicode(display_link))
                            __M_writer(u'">')
                            __M_writer(unicode(_(display_name)))
                            __M_writer(u'</a> \n')
            # SOURCE LINE 104
            __M_writer(u'                </div>\n')
            # SOURCE LINE 105
            if data.peek != "no peek":
                # SOURCE LINE 106
                __M_writer(u'                    <div><pre id="peek')
                __M_writer(unicode(data.id))
                __M_writer(u'" class="peek">')
                __M_writer(unicode(_(data.display_peek())))
                __M_writer(u'</pre></div>\n')
            # SOURCE LINE 108
        else:
            # SOURCE LINE 109
            __M_writer(u'\t\t<div>')
            __M_writer(unicode(_('Error: unknown dataset state "%s".') % data_state))
            __M_writer(u'</div>\n')
        # SOURCE LINE 111
        __M_writer(u'               \n')
        # SOURCE LINE 113
        __M_writer(u'                              \n')
        # SOURCE LINE 114
        if len( data.children ) > 0:
            # SOURCE LINE 117
            __M_writer(u'                ')

            children = []
            for child in data.children:
                if child.visible:
                    children.append( child )
            
            
            # SOURCE LINE 122
            __M_writer(u'\n')
            # SOURCE LINE 123
            if len( children ) > 0:
                # SOURCE LINE 124
                __M_writer(u'                    <div>\n                        There are ')
                # SOURCE LINE 125
                __M_writer(unicode(len( children )))
                __M_writer(u' secondary datasets.\n')
                # SOURCE LINE 126
                for idx, child in enumerate(children):
                    # SOURCE LINE 127
                    __M_writer(u'                            ')
                    __M_writer(unicode(render_dataset( child, idx + 1, show_deleted_on_refresh = show_deleted_on_refresh )))
                    __M_writer(u'\n')
                # SOURCE LINE 129
                __M_writer(u'                    </div>\n')
        # SOURCE LINE 132
        __M_writer(u'\n        </div>\n    </div>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


