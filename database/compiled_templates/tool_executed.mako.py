from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381913.7390771
_template_filename='templates/tool_executed.mako'
_template_uri='tool_executed.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        tool = context.get('tool', UNDEFINED)
        out_data = context.get('out_data', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n\n<head>\n<title>Galaxy</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<link href="')
        # SOURCE LINE 7
        __M_writer(unicode(h.url_for('/static/style/base.css')))
        __M_writer(u'" rel="stylesheet" type="text/css" />\n<script type="text/javascript">\n  var inside_galaxy_frameset = false;\n\n  if ( parent.frames && parent.frames.galaxy_history ) {\n      parent.frames.galaxy_history.location.href="')
        # SOURCE LINE 12
        __M_writer(unicode(h.url_for( controller='root', action='history' )))
        __M_writer(u'";\n      inside_galaxy_frameset = true;\n  }\n  \n  if ( parent.handle_minwidth_hint ) {\n      parent.handle_minwidth_hint( -1 );\n  }\n\n  function main() {\n    // If called from outside the galaxy frameset, redirect there\n')
        # SOURCE LINE 22
        if tool.options.refresh:
            # SOURCE LINE 23
            __M_writer(u'      if ( ! inside_galaxy_frameset ) {\n        setTimeout( "refresh()", 1000 );\n        document.getElementById( "refresh_message" ).style.display = "block";\n      }\n')
        # SOURCE LINE 28
        __M_writer(u"  }\n\n  function refresh() {\n    top.location.href = '")
        # SOURCE LINE 31
        __M_writer(unicode(h.url_for( "/" )))
        __M_writer(u'\';\n  }\n\n</script>\n\n</head>\n\n<body onLoad="main()">\n\n<div class="donemessagelarge">\n\n<p>The following job has been succesfully added to the queue:</p>\n\n')
        # SOURCE LINE 44
        for data in out_data.values():
            # SOURCE LINE 45
            __M_writer(u'   <div style="padding: 10px"><b> ')
            __M_writer(unicode(data.hid))
            __M_writer(u': ')
            __M_writer(unicode(data.name))
            __M_writer(u'</b></div>\n')
        # SOURCE LINE 47
        __M_writer(u"\n<p>\nYou can check the status of queued jobs and view the resulting \ndata by refreshing the <b>History</b> pane. When the job has been run\nthe status will change from 'running' to 'finished' if completed \nsuccesfully or 'error' if problems were encountered.\n</p>\n\n")
        # SOURCE LINE 55
        if tool.options.refresh:
            # SOURCE LINE 56
            __M_writer(u'<p id="refresh_message" style="display: none;">You are now being redirected back to <a href="')
            __M_writer(unicode(h.url_for( '/' )))
            __M_writer(u'">Galaxy</a></div>\n')
        # SOURCE LINE 58
        __M_writer(u'\n</div>\n\n</body>\n\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


