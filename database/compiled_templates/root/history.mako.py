from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262455474.663353
_template_filename='templates/root/history.mako'
_template_uri='root/history.mako'
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
    # SOURCE LINE 322
    ns = runtime.Namespace('__anon_0x42f4810', context._clean_inheritance_tokens(), templateuri=u'history_common.mako', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, '__anon_0x42f4810')] = ns

    # SOURCE LINE 321
    ns = runtime.Namespace('__anon_0x42f46d0', context._clean_inheritance_tokens(), templateuri=u'../tagging_common.mako', callables=None, calling_uri=_template_uri, module=None)
    context.namespaces[(__name__, '__anon_0x42f46d0')] = ns

def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        _import_ns = {}
        _mako_get_namespace(context, '__anon_0x42f4810')._populate(_import_ns, [u'render_dataset'])
        _mako_get_namespace(context, '__anon_0x42f46d0')._populate(_import_ns, [u'render_tagging_element'])
        map = _import_ns.get('map', context.get('map', UNDEFINED))
        datasets = _import_ns.get('datasets', context.get('datasets', UNDEFINED))
        show_deleted = _import_ns.get('show_deleted', context.get('show_deleted', UNDEFINED))
        render_tagging_element = _import_ns.get('render_tagging_element', context.get('render_tagging_element', UNDEFINED))
        h = _import_ns.get('h', context.get('h', UNDEFINED))
        reversed = _import_ns.get('reversed', context.get('reversed', UNDEFINED))
        render_dataset = _import_ns.get('render_dataset', context.get('render_dataset', UNDEFINED))
        bool = _import_ns.get('bool', context.get('bool', UNDEFINED))
        n_ = _import_ns.get('n_', context.get('n_', UNDEFINED))
        hda_id = _import_ns.get('hda_id', context.get('hda_id', UNDEFINED))
        trans = _import_ns.get('trans', context.get('trans', UNDEFINED))
        history = _import_ns.get('history', context.get('history', UNDEFINED))
        __M_writer = context.writer()
        # SOURCE LINE 1
        _=n_ 
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['_'] if __M_key in __M_locals_builtin()]))
        __M_writer(u'\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n\n<html>\n\n<head>\n<title>')
        # SOURCE LINE 7
        __M_writer(unicode(_('Galaxy History')))
        __M_writer(u'</title>\n\n')
        # SOURCE LINE 10
        if bool( [ data for data in history.active_datasets if data.state in ['running', 'queued', '', None ] ] ):
            # SOURCE LINE 11
            __M_writer(u'<!-- running: do not change this comment, used by TwillTestCase.wait -->\n')
        # SOURCE LINE 13
        __M_writer(u'\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<meta http-equiv="Pragma" content="no-cache">\n\n')
        # SOURCE LINE 17
        __M_writer(unicode(h.css( "base", "history", "autocomplete_tagging" )))
        __M_writer(u'\n')
        # SOURCE LINE 18
        __M_writer(unicode(h.js( "jquery", "json2", "jquery.jstore-all", "jquery.autocomplete", "autocomplete_tagging" )))
        __M_writer(u'\n\n<script type="text/javascript">\n$(function() {\n    // Load jStore for local storage\n    $.extend(jQuery.jStore.defaults, { project: \'galaxy\', flash: \'/static/jStore.Flash.html\' })\n    $.jStore.load(); // Auto-select best storage\n\n    $.jStore.ready(function(engine) {\n        engine.ready(function() {\n            // Init stuff that requires the local storage to be running\n            initShowHide();\n            setupHistoryItem( $("div.historyItemWrapper") ); \n        });\n    });\n    \n    // Generate \'collapse all\' link\n    $("#top-links").append( "|&nbsp;" ).append( $("<a href=\'#\'>')
        # SOURCE LINE 35
        __M_writer(unicode(_('collapse all')))
        __M_writer(u'</a>").click( function() {\n        $( "div.historyItemBody:visible" ).each( function() {\n            if ( $.browser.mozilla ) {\n                $(this).find( "pre.peek" ).css( "overflow", "hidden" );\n            }\n            $(this).slideUp( "fast" );\n        });\n        $.jStore.remove("history_expand_state");\n    }));\n    \n    $("#history-rename").click( function() {\n        var old_name = $("#history-name").text()\n        var t = $("<input type=\'text\' value=\'" + old_name + "\'></input>" );\n        t.blur( function() {\n            $(this).remove();\n            $("#history-name").show();\n        });\n        t.keyup( function( e ) {\n            if ( e.keyCode == 27 ) {\n                // Escape key\n                $(this).trigger( "blur" );\n            } else if ( e.keyCode == 13 ) {\n                // Enter key\n                new_value = this.value;\n                $(this).trigger( "blur" );\n                $.ajax({\n                    url: "')
        # SOURCE LINE 61
        __M_writer(unicode(h.url_for( controller='history', action='rename_async', id=history.id )))
        __M_writer(u'",\n                    data: { "_": true, new_name: new_value },\n                    error: function() { alert( "Rename failed" ) },\n                    success: function() {\n                        $("#history-name").text( new_value );\n                    }\n                });\n            }\n        });\n        $("#history-name").hide();\n        $("#history-name-area").append( t );\n        t.focus();\n        return false;\n    });\n    // Updater\n    updater({\n        ')
        # SOURCE LINE 77
        updateable = [data for data in reversed( datasets ) if data.visible and data.state not in [ "deleted", "empty", "error", "ok" ]] 
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['updateable','data'] if __M_key in __M_locals_builtin()]))
        __M_writer(u'\n        ')
        # SOURCE LINE 78
        __M_writer(unicode( ",".join( map(lambda data: "\"%s\" : \"%s\"" % (data.id, data.state), updateable) ) ))
        __M_writer(u'\n    });\n    \n    // Navigate to a dataset.\n')
        # SOURCE LINE 82
        if hda_id:
            # SOURCE LINE 83
            __M_writer(u'        self.location = "#')
            __M_writer(unicode(hda_id))
            __M_writer(u'";\n')
        # SOURCE LINE 85
        __M_writer(u'});\n// Functionized so AJAX\'d datasets can call them\nfunction initShowHide() {\n\n    // Load saved state and show as necessary\n    try {\n        var stored = $.jStore.store("history_expand_state");\n        if (stored) {\n            var st = JSON.parse(stored);\n            for (var id in st) {\n                $("#" + id + " div.historyItemBody" ).show();\n            }\n        }\n    } catch(err) {\n        // Something was wrong with values in storage, so clear storage\n        $.jStore.remove("history_expand_state");\n    }\n\n    // If Mozilla, hide scrollbars in hidden items since they cause animation bugs\n    if ( $.browser.mozilla ) {\n        $( "div.historyItemBody" ).each( function() {\n            if ( ! $(this).is( ":visible" ) ) $(this).find( "pre.peek" ).css( "overflow", "hidden" );\n        })\n    }\n}\n// Add show/hide link and delete link to a history item\nfunction setupHistoryItem( query ) {\n    query.each( function() {\n        var id = this.id;\n        var body = $(this).children( "div.historyItemBody" );\n        var peek = body.find( "pre.peek" )\n        $(this).children( ".historyItemTitleBar" ).find( ".historyItemTitle" ).wrap( "<a href=\'#\'></a>" ).click( function() {\n            if ( body.is(":visible") ) {\n                // Hiding stuff here\n                if ( $.browser.mozilla ) { peek.css( "overflow", "hidden" ) }\n                body.slideUp( "fast" );\n                \n                // Save setting\n                var stored = $.jStore.store("history_expand_state")\n                var prefs = stored ? JSON.parse(stored) : null\n                if (prefs) {\n                    delete prefs[id];\n                    $.jStore.store("history_expand_state", JSON.stringify(prefs));\n                }\n            } else {\n                // Showing stuff here\n                body.slideDown( "fast", function() { \n                    if ( $.browser.mozilla ) { peek.css( "overflow", "auto" ); } \n                });\n                \n                // Save setting\n                var stored = $.jStore.store("history_expand_state")\n                var prefs = stored ? JSON.parse(stored) : new Object;\n                prefs[id] = true;\n                $.jStore.store("history_expand_state", JSON.stringify(prefs));\n            }\n            return false;\n        });\n        // Delete link\n        $(this).find( "div.historyItemButtons > .delete" ).each( function() {\n            var data_id = this.id.split( "-" )[1];\n            $(this).click( function() {\n                $( \'#historyItem-\' + data_id + "> div.historyItemTitleBar" ).addClass( "spinner" );\n                $.ajax({\n                    url: "')
        # SOURCE LINE 149
        __M_writer(unicode(h.url_for( action='delete_async', id='XXX' )))
        __M_writer(u'".replace( \'XXX\', data_id ),\n                    error: function() { alert( "Delete failed" ) },\n                    success: function() {\n')
        # SOURCE LINE 152
        if show_deleted:
            # SOURCE LINE 153
            __M_writer(u'                        var to_update = {};\n                        to_update[data_id] = "none";\n                        updater( to_update );\n')
            # SOURCE LINE 156
        else:
            # SOURCE LINE 157
            __M_writer(u'                        $( "#historyItem-" + data_id ).fadeOut( "fast", function() {\n                            $( "#historyItemContainer-" + data_id ).remove();\n                            if ( $( "div.historyItemContainer" ).length < 1 ) {\n                                $( "#emptyHistoryMessage" ).show();\n                            }\n                        });\n')
        # SOURCE LINE 164
        __M_writer(u'                    }\n                });\n                return false;\n            });\n        });\n        // Undelete link\n        $(this).find( "a.historyItemUndelete" ).each( function() {\n            var data_id = this.id.split( "-" )[1];\n            $(this).click( function() {\n                $( \'#historyItem-\' + data_id + " > div.historyItemTitleBar" ).addClass( "spinner" );\n                $.ajax({\n                    url: "')
        # SOURCE LINE 175
        __M_writer(unicode(h.url_for( controller='dataset', action='undelete_async', id='XXX' )))
        __M_writer(u'".replace( \'XXX\', data_id ),\n                    error: function() { alert( "Undelete failed" ) },\n                    success: function() {\n                        var to_update = {};\n                        to_update[data_id] = "none";\n                        updater( to_update );\n                    }\n                });\n                return false;\n            });\n        });\n    });\n};\n// Looks for changes in dataset state using an async request. Keeps\n// calling itself (via setTimeout) until all datasets are in a terminal\n// state.\nvar updater = function ( tracked_datasets ) {\n    // Check if there are any items left to track\n    var empty = true;\n    for ( i in tracked_datasets ) {\n        empty = false;\n        break;\n    }\n    if ( ! empty ) {\n        // console.log( "Updater running in 3 seconds" );\n        setTimeout( function() { updater_callback( tracked_datasets ) }, 3000 );\n    } else {\n        // console.log( "Updater finished" );\n    }\n};\nvar updater_callback = function ( tracked_datasets ) {\n    // Build request data\n    var ids = []\n    var states = []\n    var force_history_refresh = false\n    $.each( tracked_datasets, function ( id, state ) {\n        ids.push( id );\n        states.push( state );\n    });\n    // Make ajax call\n    $.ajax( {\n        type: "POST",\n        url: "')
        # SOURCE LINE 217
        __M_writer(unicode(h.url_for( controller='root', action='history_item_updates' )))
        __M_writer(u'",\n        dataType: "json",\n        data: { ids: ids.join( "," ), states: states.join( "," ) },\n        success : function ( data ) {\n            $.each( data, function( id, val ) {\n                // Replace HTML\n                var container = $("#historyItemContainer-" + id);\n                container.html( val.html );\n                setupHistoryItem( container.children( ".historyItemWrapper" ) );\n                initShowHide();\n                // If new state was terminal, stop tracking\n                if (( val.state == "ok") || ( val.state == "error") || ( val.state == "empty") || ( val.state == "deleted" ) || ( val.state == "discarded" )) {\n                    if ( val.force_history_refresh ){\n                        force_history_refresh = true;\n                    }\n                    delete tracked_datasets[ parseInt(id) ];\n                } else {\n                    tracked_datasets[ parseInt(id) ] = val.state;\n                }\n            });\n            if ( force_history_refresh ) {\n                parent.frames.galaxy_history.location.reload();\n            } else {\n                // Keep going (if there are still any items to track)\n                updater( tracked_datasets ); \n            }\n        },\n        error: function() {\n            // Just retry, like the old method, should try to be smarter\n            updater( tracked_datasets );\n        }\n    });\n};\n\n    //TODO: this function is a duplicate of array_length defined in galaxy.base.js ; not sure why it needs to be redefined here (due to streaming?).\n    // Returns the number of keys (elements) in an array/dictionary.\n    var array_length = function(an_array)\n    {\n        if (an_array.length)\n            return an_array.length;\n\n        var count = 0;\n        for (element in an_array)   \n            count++;\n        return count;\n    };\n \n    //\n    // Function provides text for tagging toggle link.\n    //\n    var get_toggle_link_text = function(tags)\n    {\n        var text = "";\n        var num_tags = array_length(tags);\n        if (num_tags != 0)\n          {\n            text = num_tags + (num_tags != 1 ? " Tags" : " Tag");\n          }\n        else\n          {\n            // No tags.\n            text = "Add tags to history";\n          }\n        return text;\n    };\n</script>\n\n<style>\n.historyItemBody {\n    display: none;\n}\n</style>\n\n<noscript>\n<style>\n.historyItemBody {\n    display: block;\n}\n</style>\n</noscript>\n\n</head>\n\n<body class="historyPage">\n    \n<div id="top-links" class="historyLinks">\n    <a href="')
        # SOURCE LINE 303
        __M_writer(unicode(h.url_for('history', show_deleted=show_deleted)))
        __M_writer(u'">')
        __M_writer(unicode(_('refresh')))
        __M_writer(u'</a> \n')
        # SOURCE LINE 304
        if show_deleted:
            # SOURCE LINE 305
            __M_writer(u'    | <a href="')
            __M_writer(unicode(h.url_for('history', show_deleted=False)))
            __M_writer(u'">')
            __M_writer(unicode(_('hide deleted')))
            __M_writer(u'</a> \n')
        # SOURCE LINE 307
        __M_writer(u'</div>\n    \n<div id="history-name-area" class="historyLinks" style="color: gray; font-weight: bold;">\n    <div style="float: right"><a id="history-rename" title="Rename" class="icon-button edit" target="galaxy_main" href="')
        # SOURCE LINE 310
        __M_writer(unicode(h.url_for( controller='history', action='rename' )))
        __M_writer(u'"></a></div>\n    <div id="history-name">')
        # SOURCE LINE 311
        __M_writer(unicode(history.get_display_name()))
        __M_writer(u'</div>\n</div>\n\n')
        # SOURCE LINE 314
        if history.deleted:
            # SOURCE LINE 315
            __M_writer(u'    <div class="warningmessagesmall">\n        ')
            # SOURCE LINE 316
            __M_writer(unicode(_('You are currently viewing a deleted history!')))
            __M_writer(u'\n    </div>\n    <p></p>\n')
        # SOURCE LINE 320
        __M_writer(u'\n')
        # SOURCE LINE 321
        __M_writer(u'\n')
        # SOURCE LINE 322
        __M_writer(u'\n\n')
        # SOURCE LINE 324
        if trans.get_user() is not None:
            # SOURCE LINE 325
            __M_writer(u'    <style>\n        .tag-element {\n            margin-bottom: 0.5em;\n        }\n    </style>\n    ')
            # SOURCE LINE 330
            __M_writer(unicode(render_tagging_element( tagged_item=history, elt_context='history.mako', get_toggle_link_text_fn='get_toggle_link_text' )))
            __M_writer(u'\n')
        # SOURCE LINE 332
        __M_writer(u'\n')
        # SOURCE LINE 333
        if not datasets:
            # SOURCE LINE 334
            __M_writer(u'\n    <div class="infomessagesmall" id="emptyHistoryMessage">\n\n')
            # SOURCE LINE 337
        else:    
            # SOURCE LINE 338
            __M_writer(u'\n')
            # SOURCE LINE 340
            for data in reversed( datasets ):
                # SOURCE LINE 341
                if data.visible:
                    # SOURCE LINE 342
                    __M_writer(u'            <div class="historyItemContainer" id="historyItemContainer-')
                    __M_writer(unicode(data.id))
                    __M_writer(u'">\n                ')
                    # SOURCE LINE 343
                    __M_writer(unicode(render_dataset( data, data.hid, show_deleted_on_refresh = show_deleted, user_owns_dataset = True )))
                    __M_writer(u'\n            </div>\n')
            # SOURCE LINE 347
            __M_writer(u'\n    <div class="infomessagesmall" id="emptyHistoryMessage" style="display:none;">\n')
        # SOURCE LINE 350
        __M_writer(u'        ')
        __M_writer(unicode(_("Your history is empty. Click 'Get Data' on the left pane to start")))
        __M_writer(u'\n    </div>\n\n</body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


