from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381897.0475869
_template_filename=u'templates/tagging_common.mako'
_template_uri=u'root/../tagging_common.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['render_tagging_element_html', 'render_tagging_element', 'render_community_tagging_element']


# SOURCE LINE 1
 
from cgi import escape 
from galaxy.web.framework.helpers import iff
from random import random
from sys import maxint
from math import floor
from galaxy.tags.tag_handler import TagHandler
from galaxy.model import Tag, ItemTagAssociation

tag_handler = TagHandler()


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        in_form = context.get('in_form', UNDEFINED)
        def render_tagging_element(tagged_item=None,elt_context=None,use_toggle_link=True,in_form=False,input_size='15',tag_click_fn='default_tag_click_fn',get_toggle_link_text_fn='default_get_toggle_link_text_fn',editable=True):
            return render_render_tagging_element(context.locals_(__M_locals),tagged_item,elt_context,use_toggle_link,in_form,input_size,tag_click_fn,get_toggle_link_text_fn,editable)
        elt_context = context.get('elt_context', UNDEFINED)
        tag_click_fn = context.get('tag_click_fn', UNDEFINED)
        input_size = context.get('input_size', UNDEFINED)
        tagged_item = context.get('tagged_item', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 11
        __M_writer(u'\n\n')
        # SOURCE LINE 14
        if tagged_item is not None:
            # SOURCE LINE 15
            __M_writer(u'    ')
            __M_writer(unicode(render_tagging_element(tagged_item=tagged_item, elt_context=elt_context, in_form=in_form, input_size=input_size, tag_click_fn=tag_click_fn)))
            __M_writer(u'\n')
        # SOURCE LINE 17
        __M_writer(u'\n')
        # SOURCE LINE 78
        __M_writer(u'\n\n')
        # SOURCE LINE 93
        __M_writer(u'\n\n\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_tagging_element_html(context,elt_id=None,tags=None,editable=True,use_toggle_link=True,input_size='15',in_form=False):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        unicode = context.get('unicode', UNDEFINED)
        isinstance = context.get('isinstance', UNDEFINED)
        len = context.get('len', UNDEFINED)
        str = context.get('str', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 19
        __M_writer(u'\n')
        # SOURCE LINE 21
        __M_writer(u'    ')
 
        num_tags = len( tags )
            
        
        # SOURCE LINE 23
        __M_writer(u'\n    <div class="tag-element"\n')
        # SOURCE LINE 25
        if elt_id:
            # SOURCE LINE 26
            __M_writer(u'            id="')
            __M_writer(unicode(elt_id))
            __M_writer(u'"\n')
        # SOURCE LINE 29
        if num_tags == 0 and not editable:
            # SOURCE LINE 30
            __M_writer(u'            style="display: none"\n')
        # SOURCE LINE 32
        __M_writer(u'    >\n')
        # SOURCE LINE 33
        if use_toggle_link:
            # SOURCE LINE 34
            __M_writer(u'            <a class="toggle-link" href="#">')
            __M_writer(unicode(num_tags))
            __M_writer(u' Tags</a>\n')
        # SOURCE LINE 36
        __M_writer(u'        <div class="tag-area">\n\n')
        # SOURCE LINE 39
        for tag in tags:
            # SOURCE LINE 40
            __M_writer(u'                ')

                    ## Handle both Tag and ItemTagAssociation objects.
            if isinstance( tag, Tag ):
                tag_name = tag.name
                tag_value = None
            elif isinstance( tag, ItemTagAssociation ):
                tag_name = tag.user_tname
                tag_value = tag.user_value
            ## Convert tag name, value to unicode.
            if isinstance( tag_name, str ):
                tag_name = unicode( escape( tag_name ), 'utf-8' )
                if tag_value:
                    tag_value = unicode( escape( tag_value ), 'utf-8' )
            if tag_value:
                tag_str = tag_name + ":" + tag_value
            else:
                tag_str = tag_name
                            
            
            # SOURCE LINE 57
            __M_writer(u'\n                <span class="tag-button">\n                    <span class="tag-name">')
            # SOURCE LINE 59
            __M_writer(unicode(tag_str))
            __M_writer(u'</span>\n')
            # SOURCE LINE 60
            if editable:
                # SOURCE LINE 61
                __M_writer(u'                        <img class="delete-tag-img" src="')
                __M_writer(unicode(h.url_for('/static/images/delete_tag_icon_gray.png')))
                __M_writer(u'"/>\n')
            # SOURCE LINE 63
            __M_writer(u'                </span>\n')
        # SOURCE LINE 65
        __M_writer(u'            \n')
        # SOURCE LINE 67
        if editable:
            # SOURCE LINE 68
            if in_form:
                # SOURCE LINE 69
                __M_writer(u'                    <textarea class="tag-input" rows=\'1\' cols=\'')
                __M_writer(unicode(input_size))
                __M_writer(u"'></textarea>\n")
                # SOURCE LINE 70
            else:
                # SOURCE LINE 71
                __M_writer(u'                    <input class="tag-input" type=\'text\' size=\'')
                __M_writer(unicode(input_size))
                __M_writer(u"'></input>\n")
            # SOURCE LINE 74
            __M_writer(u"                <img src='")
            __M_writer(unicode(h.url_for('/static/images/add_icon.png')))
            __M_writer(u"' rollover='")
            __M_writer(unicode(h.url_for('/static/images/add_icon_dark.png')))
            __M_writer(u'\' class="add-tag-button"/>\n')
        # SOURCE LINE 76
        __M_writer(u'        </div>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_tagging_element(context,tagged_item=None,elt_context=None,use_toggle_link=True,in_form=False,input_size='15',tag_click_fn='default_tag_click_fn',get_toggle_link_text_fn='default_get_toggle_link_text_fn',editable=True):
    context.caller_stack._push_frame()
    try:
        isinstance = context.get('isinstance', UNDEFINED)
        str = context.get('str', UNDEFINED)
        int = context.get('int', UNDEFINED)
        h = context.get('h', UNDEFINED)
        self = context.get('self', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        unicode = context.get('unicode', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 97
        __M_writer(u'\n')
        # SOURCE LINE 99
        __M_writer(u'    ')
 
        tagged_item_id = str( trans.security.encode_id (tagged_item.id) )
        elt_id = int ( floor ( random()*maxint ) )
            
        
        # SOURCE LINE 102
        __M_writer(u'\n    \n')
        # SOURCE LINE 105
        __M_writer(u'    ')
        __M_writer(unicode(self.render_tagging_element_html(elt_id, tagged_item.tags, editable, use_toggle_link, input_size, in_form)))
        __M_writer(u'\n    \n')
        # SOURCE LINE 108
        __M_writer(u'    <script type="text/javascript">\n        //\n        // Set up autocomplete tagger.\n        //\n        ')
        # SOURCE LINE 112

            ## Build string of tag name, values.
        tag_names_and_values = dict()
        for tag in tagged_item.tags:
            tag_name = tag.user_tname
            tag_value = ""
            if tag.value is not None:
                tag_value = tag.user_value
            ## Tag names and values may be string or unicode object.
            if isinstance( tag_name, str ):
                tag_names_and_values[unicode(tag_name, 'utf-8')] = unicode(tag_value, 'utf-8')
            else: ## isInstance( tag_name, unicode ):
                tag_names_and_values[tag_name] = tag_value
                
        
        # SOURCE LINE 125
        __M_writer(u'\n    \n        //\n        // Default function get text to display on the toggle link.\n        //\n        var default_get_toggle_link_text_fn = function(tags)\n        {\n            var text = "";\n            var num_tags = array_length(tags);\n            if (num_tags != 0)\n              {\n                text = num_tags + (num_tags != 1 ? " Tags" : " Tag");\n                /*\n                // Show first N tags; hide the rest.\n                var max_to_show = 1;\n    \n                // Build tag string.\n                var tag_strs = new Array();\n                var count = 0;\n                for (tag_name in tags)\n                  {\n                    tag_value = tags[tag_name];\n                    tag_strs[tag_strs.length] = build_tag_str(tag_name, tag_value);\n                    if (++count == max_to_show)\n                      break;\n                  }\n                tag_str = tag_strs.join(", ");\n            \n                // Finalize text.\n                var num_tags_hiding = num_tags - max_to_show;\n                text = "Tags: " + tag_str + \n                  (num_tags_hiding != 0 ? " and " + num_tags_hiding + " more" : "");\n                */\n              }\n            else\n              {\n                // No tags.\n                text = "Add tags";\n              }\n            return text;\n        };\n        \n        // Default function to handle a tag click.\n        var default_tag_click_fn = function(tag_name, tag_value) { };\n        \n        var options =\n        {\n            tags : ')
        # SOURCE LINE 172
        __M_writer(unicode(h.to_json_string(tag_names_and_values)))
        __M_writer(u',\n            editable : ')
        # SOURCE LINE 173
        __M_writer(unicode(iff( editable, 'true', 'false' )))
        __M_writer(u',\n            get_toggle_link_text_fn: ')
        # SOURCE LINE 174
        __M_writer(unicode(get_toggle_link_text_fn))
        __M_writer(u',\n            tag_click_fn: ')
        # SOURCE LINE 175
        __M_writer(unicode(tag_click_fn))
        __M_writer(u',\n')
        # SOURCE LINE 177
        __M_writer(u'            ajax_autocomplete_tag_url: "')
        __M_writer(unicode(h.url_for( controller='/tag', action='tag_autocomplete_data', id=tagged_item_id, item_class=tagged_item.__class__.__name__ )))
        __M_writer(u'",\n            ajax_add_tag_url: "')
        # SOURCE LINE 178
        __M_writer(unicode(h.url_for( controller='/tag', action='add_tag_async', id=tagged_item_id, item_class=tagged_item.__class__.__name__, context=elt_context )))
        __M_writer(u'",\n            ajax_delete_tag_url: "')
        # SOURCE LINE 179
        __M_writer(unicode(h.url_for( controller='/tag', action='remove_tag_async', id=tagged_item_id, item_class=tagged_item.__class__.__name__, context=elt_context )))
        __M_writer(u'",\n            delete_tag_img: "')
        # SOURCE LINE 180
        __M_writer(unicode(h.url_for('/static/images/delete_tag_icon_gray.png')))
        __M_writer(u'",\n            delete_tag_img_rollover: "')
        # SOURCE LINE 181
        __M_writer(unicode(h.url_for('/static/images/delete_tag_icon_white.png')))
        __M_writer(u'",\n            use_toggle_link: ')
        # SOURCE LINE 182
        __M_writer(unicode(iff( use_toggle_link, 'true', 'false' )))
        __M_writer(u",\n         };\n         \n        $('#")
        # SOURCE LINE 185
        __M_writer(unicode(elt_id))
        __M_writer(u"').autocomplete_tagging(options);\n    </script>\n    \n")
        # SOURCE LINE 189
        __M_writer(u'    <style>\n    .tag-area {\n        display: ')
        # SOURCE LINE 191
        __M_writer(unicode(iff( use_toggle_link, "none", "block" )))
        __M_writer(u';\n    }\n    </style>\n\n    <noscript>\n    <style>\n    .tag-area {\n        display: block;\n    }\n    </style>\n    </noscript>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_render_community_tagging_element(context,tagged_item=None,use_toggle_link=False,tag_click_fn='default_tag_click_fn'):
    context.caller_stack._push_frame()
    try:
        int = context.get('int', UNDEFINED)
        self = context.get('self', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 81
        __M_writer(u'\n')
        # SOURCE LINE 83
        __M_writer(u'    ')
 
        elt_id = int ( floor ( random()*maxint ) ) 
        community_tags = tag_handler.get_community_tags(trans.sa_session, tagged_item, 10)
            
        
        # SOURCE LINE 86
        __M_writer(u'\n    ')
        # SOURCE LINE 87
        __M_writer(unicode(self.render_tagging_element_html(elt_id=elt_id, tags=community_tags, use_toggle_link=use_toggle_link, editable=False)))
        __M_writer(u'\n    \n')
        # SOURCE LINE 90
        __M_writer(u'    <script type="text/javascript">\n        init_tag_click_function($(\'#')
        # SOURCE LINE 91
        __M_writer(unicode(elt_id))
        __M_writer(u"'), ")
        __M_writer(unicode(tag_click_fn))
        __M_writer(u');\n    </script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


