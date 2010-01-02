from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262456775.314405
_template_filename=u'templates/base.mako'
_template_uri=u'/base.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['stylesheets', 'javascripts', 'title']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        next = context.get('next', UNDEFINED)
        n_ = context.get('n_', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        _=n_ 
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['_'] if __M_key in __M_locals_builtin()]))
        __M_writer(u'\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n\n<head>\n<title>')
        # SOURCE LINE 6
        __M_writer(unicode(self.title()))
        __M_writer(u'</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n')
        # SOURCE LINE 8
        __M_writer(unicode(self.stylesheets()))
        __M_writer(u'\n')
        # SOURCE LINE 9
        __M_writer(unicode(self.javascripts()))
        __M_writer(u'\n</head>\n\n    <body>\n        ')
        # SOURCE LINE 13
        __M_writer(unicode(next.body()))
        __M_writer(u'\n    </body>\n</html>\n\n')
        # SOURCE LINE 18
        __M_writer(u'\n\n')
        # SOURCE LINE 23
        __M_writer(u'\n\n')
        # SOURCE LINE 31
        __M_writer(u'\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_stylesheets(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 21
        __M_writer(u'\n    ')
        # SOURCE LINE 22
        __M_writer(unicode(h.css('base')))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_javascripts(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 26
        __M_writer(u'\n')
        # SOURCE LINE 30
        __M_writer(u'  ')
        __M_writer(unicode(h.js( "jquery", "galaxy.base" )))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        return ''
    finally:
        context.caller_stack._pop_frame()


