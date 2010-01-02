from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381917.3943341
_template_filename='templates/root/history_item.mako'
_template_uri='root/history_item.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    # SOURCE LINE 1
    ns = runtime.Namespace('__anon_0x4c2bb10', context._clean_inheritance_tokens(), templateuri=u'history_common.mako', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, '__anon_0x4c2bb10')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        _import_ns = {}
        _mako_get_namespace(context, '__anon_0x4c2bb10')._populate(_import_ns, [u'render_dataset'])
        hid = _import_ns.get('hid', context.get('hid', UNDEFINED))
        data = _import_ns.get('data', context.get('data', UNDEFINED))
        render_dataset = _import_ns.get('render_dataset', context.get('render_dataset', UNDEFINED))
        __M_writer = context.writer()
        __M_writer(u'\n\n')
        # SOURCE LINE 3
        __M_writer(unicode(render_dataset( data, hid )))
        __M_writer(u'    \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


