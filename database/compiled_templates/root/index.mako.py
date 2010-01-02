from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381896.432462
_template_filename='templates/root/index.mako'
_template_uri='root/index.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['init', 'left_panel', 'center_panel', 'late_javascripts', 'right_panel']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'/base_panels.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'\n\n')
        # SOURCE LINE 48
        __M_writer(u'\n\n')
        # SOURCE LINE 68
        __M_writer(u'\n\n')
        # SOURCE LINE 77
        __M_writer(u'\n\n')
        # SOURCE LINE 99
        __M_writer(u'\n\n')
        # SOURCE LINE 113
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_init(context):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 50
        __M_writer(u'\n')
        # SOURCE LINE 51

        if trans.app.config.cloud_controller_instance:
                self.has_left_panel=False
                self.has_right_panel=False
                self.active_view="cloud"
        else:
                self.has_left_panel=True
                self.has_right_panel=True
                self.active_view="analysis"
        
        
        # SOURCE LINE 60
        __M_writer(u'\n')
        # SOURCE LINE 61
        if trans.app.config.require_login and not trans.user:
            # SOURCE LINE 62
            __M_writer(u'    <script type="text/javascript">\n        if ( window != top ) {\n            top.location.href = location.href;\n        }\n    </script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_left_panel(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        n_ = context.get('n_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 70
        __M_writer(u'\n    <div class="unified-panel-header" unselectable="on">\n        <div class=\'unified-panel-header-inner\'>')
        # SOURCE LINE 72
        __M_writer(unicode(n_('Tools')))
        __M_writer(u'</div>\n    </div>\n    <div class="unified-panel-body" style="overflow: hidden;">\n        <iframe name="galaxy_tools" src="')
        # SOURCE LINE 75
        __M_writer(unicode(h.url_for( controller='root', action='tool_menu' )))
        __M_writer(u'" frameborder="0" style="position: absolute; margin: 0; border: 0 none; height: 100%; width: 100%;"> </iframe>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_center_panel(context):
    context.caller_stack._push_frame()
    try:
        tool_id = context.get('tool_id', UNDEFINED)
        m_c = context.get('m_c', UNDEFINED)
        h = context.get('h', UNDEFINED)
        m_a = context.get('m_a', UNDEFINED)
        workflow_id = context.get('workflow_id', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 79
        __M_writer(u'\n\n')
        # SOURCE LINE 82
        __M_writer(u'    ')

        if trans.app.config.require_login and not trans.user:
            center_url = h.url_for( controller='user', action='login' )
        elif tool_id is not None:
            center_url = h.url_for( 'tool_runner', tool_id=tool_id, from_noframe=True )
        elif workflow_id is not None:
            center_url = h.url_for( controller='workflow', action='run', id=workflow_id )
        elif m_c is not None:
            center_url = h.url_for( controller=m_c, action=m_a )
        elif trans.app.config.cloud_controller_instance:
            center_url = h.url_for( controller='cloud', action='list' )
        else:
            center_url = h.url_for( '/static/welcome.html' )
        
        
        # SOURCE LINE 95
        __M_writer(u'\n    \n    <iframe name="galaxy_main" id="galaxy_main" frameborder="0" style="position: absolute; width: 100%; height: 100%;" src="')
        # SOURCE LINE 97
        __M_writer(unicode(center_url))
        __M_writer(u'"> </iframe>\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_late_javascripts(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        parent = context.get('parent', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 3
        __M_writer(u'\n    ')
        # SOURCE LINE 4
        __M_writer(unicode(parent.late_javascripts()))
        __M_writer(u'\n    <script type="text/javascript">\n    $(function(){\n        $("#history-options-button").css( "position", "relative" );\n        make_popupmenu( $("#history-options-button"), {\n            "History Lists": null,\n            "Saved Histories": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 11
        __M_writer(unicode(h.url_for( controller='history', action='list')))
        __M_writer(u'";\n            },\n            "Shared Histories": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 14
        __M_writer(unicode(h.url_for( controller='history', action='list', operation='sharing' )))
        __M_writer(u'";\n            },\n            "Histories Shared with Me": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 17
        __M_writer(unicode(h.url_for( controller='history', action='list_shared')))
        __M_writer(u'";\n            },\n            "Current History": null,\n            "Create New": function() {\n                galaxy_history.location = "')
        # SOURCE LINE 21
        __M_writer(unicode(h.url_for( controller='root', action='history_new' )))
        __M_writer(u'";\n            },\n            "Clone": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 24
        __M_writer(unicode(h.url_for( controller='history', action='clone')))
        __M_writer(u'";\n            },\n            "Share": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 27
        __M_writer(unicode(h.url_for( controller='history', action='share' )))
        __M_writer(u'";\n            },\n            "Extract Workflow": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 30
        __M_writer(unicode(h.url_for( controller='workflow', action='build_from_current_history' )))
        __M_writer(u'";\n            },\n            "Dataset Security": function() {\n                galaxy_main.location = "')
        # SOURCE LINE 33
        __M_writer(unicode(h.url_for( controller='root', action='history_set_default_permissions' )))
        __M_writer(u'";\n            },\n            "Show Deleted Datasets": function() {\n                galaxy_history.location = "')
        # SOURCE LINE 36
        __M_writer(unicode(h.url_for( controller='root', action='history', show_deleted=True)))
        __M_writer(u'";\n            },\n            "Delete": function()\n            {\n                if ( confirm( "Really delete the current history?" ) )\n                {\n                    galaxy_main.location = "')
        # SOURCE LINE 42
        __M_writer(unicode(h.url_for( controller='history', action='delete_current' )))
        __M_writer(u'";\n                }\n            }\n        });\n    });\n    </script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_right_panel(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 101
        __M_writer(u'\n    <div class="unified-panel-header" unselectable="on">\n        <div class="unified-panel-header-inner">\n            <div style="float: right">\n                <a id="history-options-button" class=\'panel-header-button popup\' href="')
        # SOURCE LINE 105
        __M_writer(unicode(h.url_for( controller='root', action='history_options' )))
        __M_writer(u'" target="galaxy_main">')
        __M_writer(unicode(_('Options')))
        __M_writer(u'</a>\n            </div>\n            <div class="panel-header-text">')
        # SOURCE LINE 107
        __M_writer(unicode(_('History')))
        __M_writer(u'</div>\n        </div>\n    </div>\n    <div class="unified-panel-body" style="overflow: hidden;">\n        <iframe name="galaxy_history" width="100%" height="100%" frameborder="0" style="position: absolute; margin: 0; border: 0 none; height: 100%;" src="')
        # SOURCE LINE 111
        __M_writer(unicode(h.url_for( controller='root', action='history' )))
        __M_writer(u'"></iframe>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


