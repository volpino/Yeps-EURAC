from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381896.7957461
_template_filename='templates/root/tool_menu.mako'
_template_uri='/root/tool_menu.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['render_label', 'render_tool', 'render_workflow']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        _ = context.get('_', UNDEFINED)
        h = context.get('h', UNDEFINED)
        def render_label(label):
            return render_render_label(context.locals_(__M_locals),label)
        t = context.get('t', UNDEFINED)
        toolbox = context.get('toolbox', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        def render_tool(tool,section):
            return render_render_tool(context.locals_(__M_locals),tool,section)
        def render_workflow(key,workflow,section):
            return render_render_workflow(context.locals_(__M_locals),key,workflow,section)
        __M_writer = context.writer()
        # SOURCE LINE 25
        __M_writer(u'\n\n')
        # SOURCE LINE 37
        __M_writer(u'\n\n')
        # SOURCE LINE 44
        __M_writer(u'\n\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n    <head>\n        <title>')
        # SOURCE LINE 49
        __M_writer(unicode(_('Galaxy Tools')))
        __M_writer(u'</title>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n        <link href="')
        # SOURCE LINE 51
        __M_writer(unicode(h.url_for('/static/style/base.css')))
        __M_writer(u'" rel="stylesheet" type="text/css" />\n        <link href="')
        # SOURCE LINE 52
        __M_writer(unicode(h.url_for('/static/style/tool_menu.css')))
        __M_writer(u'" rel="stylesheet" type="text/css" />\n\n        <script type="text/javascript" src="')
        # SOURCE LINE 54
        __M_writer(unicode(h.url_for('/static/scripts/jquery.js')))
        __M_writer(u'"></script>\n\n        <script type="text/javascript">\n            var q = jQuery.noConflict();\n            q(document).ready(function() { \n                q( "div.toolSectionBody" ).hide();\n                q( "div.toolSectionTitle > span" ).wrap( "<a href=\'#\'></a>" )\n                var last_expanded = null;\n                q( "div.toolSectionTitle" ).each( function() { \n                   var body = q(this).next( "div.toolSectionBody" );\n                   q(this).click( function() {\n                       if ( body.is( ":hidden" ) ) {\n                           if ( last_expanded ) last_expanded.slideUp( "fast" );\n                           last_expanded = body;\n                           body.slideDown( "fast" );\n                       }\n                       else {\n                           body.slideUp( "fast" );\n                           last_expanded = null;\n                       }\n                       return false;\n                   });\n                });\n                q( "a[minsizehint]" ).click( function() {\n                    if ( parent.handle_minwidth_hint ) {\n                        parent.handle_minwidth_hint( q(this).attr( "minsizehint" ) );\n                    }\n                });\n            });\n        </script>\n    </head>\n\n    <body class="toolMenuPage">\n        <div class="toolMenu">\n            <div class="toolSectionList">\n                \n')
        # SOURCE LINE 90
        for key, val in toolbox.tool_panel.items():
            # SOURCE LINE 91
            if key.startswith( 'tool' ):
                # SOURCE LINE 92
                __M_writer(u'                        ')
                __M_writer(unicode(render_tool( val, False )))
                __M_writer(u'\n')
                # SOURCE LINE 93
            elif key.startswith( 'workflow' ):
                # SOURCE LINE 94
                __M_writer(u'                        ')
                __M_writer(unicode(render_workflow( key, val, False )))
                __M_writer(u'\n')
                # SOURCE LINE 95
            elif key.startswith( 'section' ):
                # SOURCE LINE 96
                __M_writer(u'                        ')
                section = val 
                
                __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['section'] if __M_key in __M_locals_builtin()]))
                __M_writer(u'\n                        <div class="toolSectionTitle" id="title_')
                # SOURCE LINE 97
                __M_writer(unicode(section.id))
                __M_writer(u'">\n                            <span>')
                # SOURCE LINE 98
                __M_writer(unicode(section.name))
                __M_writer(u'</span>\n                        </div>\n                        <div id="')
                # SOURCE LINE 100
                __M_writer(unicode(section.id))
                __M_writer(u'" class="toolSectionBody">\n                            <div class="toolSectionBg">\n')
                # SOURCE LINE 102
                for section_key, section_val in section.elems.items():
                    # SOURCE LINE 103
                    if section_key.startswith( 'tool' ):
                        # SOURCE LINE 104
                        __M_writer(u'                                        ')
                        __M_writer(unicode(render_tool( section_val, True )))
                        __M_writer(u'\n')
                        # SOURCE LINE 105
                    elif section_key.startswith( 'workflow' ):
                        # SOURCE LINE 106
                        __M_writer(u'                                        ')
                        __M_writer(unicode(render_workflow( section_key, section_val, True )))
                        __M_writer(u'\n')
                        # SOURCE LINE 107
                    elif section_key.startswith( 'label' ):
                        # SOURCE LINE 108
                        __M_writer(u'                                        ')
                        __M_writer(unicode(render_label( section_val )))
                        __M_writer(u'\n')
                # SOURCE LINE 111
                __M_writer(u'                            </div>\n                        </div>\n')
                # SOURCE LINE 113
            elif key.startswith( 'label' ):
                # SOURCE LINE 114
                __M_writer(u'                        ')
                __M_writer(unicode(render_label( val )))
                __M_writer(u'\n')
            # SOURCE LINE 116
            __M_writer(u'                    <div class="toolSectionPad"></div>\n')
        # SOURCE LINE 118
        __M_writer(u'                \n')
        # SOURCE LINE 122
        __M_writer(u'                \n')
        # SOURCE LINE 123
        if t.user:
            # SOURCE LINE 124
            __M_writer(u'                    <div class="toolSectionPad"></div>\n                    <div class="toolSectionPad"></div>\n                    <div class="toolSectionTitle" id="title_XXinternalXXworkflow">\n                      <span>Workflows</span>\n                    </div>\n                    <div id="XXinternalXXworkflow" class="toolSectionBody">\n                        <div class="toolSectionBg">\n')
            # SOURCE LINE 131
            if t.user.stored_workflow_menu_entries:
                # SOURCE LINE 132
                for m in t.user.stored_workflow_menu_entries:
                    # SOURCE LINE 133
                    __M_writer(u'                                    <div class="toolTitle">\n                                        <a href="')
                    # SOURCE LINE 134
                    __M_writer(unicode(h.url_for( controller='workflow', action='run', id=trans.security.encode_id(m.stored_workflow_id) )))
                    __M_writer(u'" target="galaxy_main">')
                    __M_writer(unicode(m.stored_workflow.name))
                    __M_writer(u'</a>\n                                    </div>\n')
            # SOURCE LINE 138
            __M_writer(u'                            <div class="toolTitle">\n                                <a href="')
            # SOURCE LINE 139
            __M_writer(unicode(h.url_for( controller='workflow', action='list_for_run')))
            __M_writer(u'" target="galaxy_main">All workflows</a>\n                            </div>\n                        </div>\n                    </div>\n')
        # SOURCE LINE 144
        __M_writer(u'                \n            </div>\n        </div>\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_label(context,label):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 40
        __M_writer(u'\n    <div class="toolPanelLabel" id="title_')
        # SOURCE LINE 41
        __M_writer(unicode(label.id))
        __M_writer(u'">\n        <span>')
        # SOURCE LINE 42
        __M_writer(unicode(label.text))
        __M_writer(u'</span>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_tool(context,tool,section):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        t = context.get('t', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'\n')
        # SOURCE LINE 3
        if not tool.hidden:
            # SOURCE LINE 4
            if section:
                # SOURCE LINE 5
                __M_writer(u'            <div class="toolTitle">\n')
                # SOURCE LINE 6
            else:
                # SOURCE LINE 7
                __M_writer(u'            <div class="toolTitleNoSection">\n')
            # SOURCE LINE 9
            __M_writer(u'            ')

            if tool.input_required:
                link = h.url_for( controller='tool_runner', tool_id=tool.id )
            else:
                link = h.url_for( tool.action, ** tool.get_static_param_values( t ) )
                        
            
            # SOURCE LINE 14
            __M_writer(u'\n')
            # SOURCE LINE 18
            if tool.name:
                # SOURCE LINE 19
                __M_writer(u'                <a id="link-')
                __M_writer(unicode(tool.id))
                __M_writer(u'" href="')
                __M_writer(unicode(link))
                __M_writer(u'" target=')
                __M_writer(unicode(tool.target))
                __M_writer(u' minsizehint="')
                __M_writer(unicode(tool.uihints.get( 'minwidth', -1 )))
                __M_writer(u'">')
                __M_writer(unicode(_(tool.name)))
                __M_writer(u'</a> ')
                __M_writer(unicode(tool.description))
                __M_writer(u' \n')
                # SOURCE LINE 20
            else:
                # SOURCE LINE 21
                __M_writer(u'                <a id="link-')
                __M_writer(unicode(tool.id))
                __M_writer(u'" href="')
                __M_writer(unicode(link))
                __M_writer(u'" target=')
                __M_writer(unicode(tool.target))
                __M_writer(u' minsizehint="')
                __M_writer(unicode(tool.uihints.get( 'minwidth', -1 )))
                __M_writer(u'">')
                __M_writer(unicode(tool.description))
                __M_writer(u'</a>\n')
            # SOURCE LINE 23
            __M_writer(u'        </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_workflow(context,key,workflow,section):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        _ = context.get('_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 28
        __M_writer(u'\n')
        # SOURCE LINE 29
        if section:
            # SOURCE LINE 30
            __M_writer(u'        <div class="toolTitle">\n')
            # SOURCE LINE 31
        else:
            # SOURCE LINE 32
            __M_writer(u'        <div class="toolTitleNoSection">\n')
        # SOURCE LINE 34
        __M_writer(u'        ')
        encoded_id = key.lstrip( 'workflow_' ) 
        
        __M_writer(u'\n        <a id="link-')
        # SOURCE LINE 35
        __M_writer(unicode(workflow.id))
        __M_writer(u'" href="')
        __M_writer(unicode( h.url_for( controller='workflow', action='run', id=encoded_id, check_user=False )))
        __M_writer(u'" target="_parent"}">')
        __M_writer(unicode(_(workflow.name)))
        __M_writer(u'</a>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


