from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262456775.1649871
_template_filename='templates/message.mako'
_template_uri='message.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['javascripts', 'render_msg']


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
    return runtime._inherit_from(context, u'/base.mako', _template_uri)
def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        message = context.get('message', UNDEFINED)
        message_type = context.get('message_type', UNDEFINED)
        n_ = context.get('n_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        _=n_ 
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['_'] if __M_key in __M_locals_builtin()]))
        __M_writer(u'\n')
        # SOURCE LINE 2
        __M_writer(u'\n\n')
        # SOURCE LINE 46
        __M_writer(u'\n\n<div class="')
        # SOURCE LINE 48
        __M_writer(unicode(message_type))
        __M_writer(u'messagelarge">')
        __M_writer(unicode(_(message)))
        __M_writer(u'</div>\n\n')
        # SOURCE LINE 54
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_javascripts(context):
    context.caller_stack._push_frame()
    try:
        parent = context.get('parent', UNDEFINED)
        int = context.get('int', UNDEFINED)
        h = context.get('h', UNDEFINED)
        app = context.get('app', UNDEFINED)
        refresh_frames = context.get('refresh_frames', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 4
        __M_writer(u'\n    ')
        # SOURCE LINE 5
        __M_writer(unicode(parent.javascripts()))
        __M_writer(u'\n    <script type="text/javascript">\n')
        # SOURCE LINE 7
        if 'masthead' in refresh_frames:
            # SOURCE LINE 14
            __M_writer(u'            \n')
            # SOURCE LINE 16
            __M_writer(u'            if ( parent.user_changed ) {\n')
            # SOURCE LINE 17
            if trans.user:
                # SOURCE LINE 18
                __M_writer(u'                    parent.user_changed( "')
                __M_writer(unicode(trans.user.email))
                __M_writer(u'", ')
                __M_writer(unicode(int( app.config.is_admin_user( trans.user ) )))
                __M_writer(u' );\n')
                # SOURCE LINE 19
            else:
                # SOURCE LINE 20
                __M_writer(u'                    parent.user_changed( null, false );\n')
            # SOURCE LINE 22
            __M_writer(u'            }\n')
        # SOURCE LINE 24
        if 'history' in refresh_frames:
            # SOURCE LINE 25
            __M_writer(u'            if ( parent.frames && parent.frames.galaxy_history ) {\n                parent.frames.galaxy_history.location.href="')
            # SOURCE LINE 26
            __M_writer(unicode(h.url_for( controller='root', action='history')))
            __M_writer(u'";\n                if ( parent.force_right_panel ) {\n                    parent.force_right_panel( \'show\' );\n                }\n            }\n')
        # SOURCE LINE 32
        if 'tools' in refresh_frames:
            # SOURCE LINE 33
            __M_writer(u'            if ( parent.frames && parent.frames.galaxy_tools ) {\n                parent.frames.galaxy_tools.location.href="')
            # SOURCE LINE 34
            __M_writer(unicode(h.url_for( controller='root', action='tool_menu')))
            __M_writer(u'";\n                if ( parent.force_left_panel ) {\n                    parent.force_left_panel( \'show\' );\n                }\n            }\n')
        # SOURCE LINE 40
        __M_writer(u'\n        if ( parent.handle_minwidth_hint )\n        {\n            parent.handle_minwidth_hint( -1 );\n        }\n    </script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_msg(context,msg,messagetype='done'):
    context.caller_stack._push_frame()
    try:
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 51
        __M_writer(u'\n    <div class="')
        # SOURCE LINE 52
        __M_writer(unicode(messagetype))
        __M_writer(u'message">')
        __M_writer(unicode(_(msg)))
        __M_writer(u'</div>\n    <br/>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


