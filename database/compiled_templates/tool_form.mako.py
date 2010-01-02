from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381904.6984329
_template_filename='templates/tool_form.mako'
_template_uri='tool_form.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['do_inputs', 'row_for_param']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        add_frame = context.get('add_frame', UNDEFINED)
        errors = context.get('errors', UNDEFINED)
        h = context.get('h', UNDEFINED)
        app = context.get('app', UNDEFINED)
        def do_inputs(inputs,tool_state,errors,prefix,other_values=None):
            return render_do_inputs(context.locals_(__M_locals),inputs,tool_state,errors,prefix,other_values)
        util = context.get('util', UNDEFINED)
        unicode = context.get('unicode', UNDEFINED)
        tool_state = context.get('tool_state', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        type = context.get('type', UNDEFINED)
        tool = context.get('tool', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<!-- -->\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n\n')
        # SOURCE LINE 4

        from galaxy.util.expressions import ExpressionContext 
        
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['ExpressionContext'] if __M_key in __M_locals_builtin()]))
        # SOURCE LINE 6
        __M_writer(u'\n\n<html>\n\n<head>\n<title>Galaxy</title>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n')
        # SOURCE LINE 13
        __M_writer(unicode(h.css( "base", "autocomplete_tagging" )))
        __M_writer(u'\n')
        # SOURCE LINE 14
        __M_writer(unicode(h.js( "jquery", "galaxy.base", "jquery.autocomplete" )))
        __M_writer(u'\n<script type="text/javascript">\n$( function() {\n    $( "select[refresh_on_change=\'true\']").change( function() {\n        var refresh = false;\n        var refresh_on_change_values = $( this )[0].attributes.getNamedItem( \'refresh_on_change_values\' )\n        if ( refresh_on_change_values ) {\n            refresh_on_change_values = refresh_on_change_values.value.split( \',\' );\n            var last_selected_value = $( this )[0].attributes.getNamedItem( \'last_selected_value\' );\n            for( i= 0; i < refresh_on_change_values.length; i++ ) {\n                if ( $( this )[0].value == refresh_on_change_values[i] || ( last_selected_value && last_selected_value.value == refresh_on_change_values[i] ) ){\n                    refresh = true;\n                    break;\n                }\n            }\n        }\n        else {\n            refresh = true;\n        }\n        if ( refresh ){\n            $( \':file\' ).each( function() {\n                var file_value = $( this )[0].value;\n                if ( file_value ) {\n                    //disable file input, since we don\'t want to upload the file on refresh\n                    var file_name = $( this )[0].name;\n                    $( this )[0].name = \'replaced_file_input_\' + file_name\n                    $( this )[0].disable = true;\n                    //create a new hidden field which stores the filename and has the original name of the file input\n                    var new_file_input = document.createElement( \'input\' );\n                    new_file_input.type = \'hidden\';\n                    new_file_input.value = file_value;\n                    new_file_input.name = file_name;\n                    document.getElementById( \'tool_form\' ).appendChild( new_file_input );\n                }\n            } );\n            $( "#tool_form" ).submit();\n        }\n    });\n    \n    // Replace dbkey select with search+select.\n    replace_dbkey_select();\n});\n')
        # SOURCE LINE 56
        if not add_frame.debug:
            # SOURCE LINE 57
            __M_writer(u'    if( window.name != "galaxy_main" ) {\n        location.replace( \'')
            # SOURCE LINE 58
            __M_writer(unicode(h.url_for( controller='root', action='index', tool_id=tool.id )))
            __M_writer(u"' );\n    }\n")
        # SOURCE LINE 61
        __M_writer(u'function checkUncheckAll( name, check )\n{\n    if ( check == 0 )\n    {\n        $("input[name=" + name + "][type=\'checkbox\']").attr(\'checked\', false);\n    }\n    else\n    {\n        $("input[name=" + name + "][type=\'checkbox\']").attr(\'checked\', true );\n    }\n}\n\n</script>\n</head>\n\n<body>\n    ')
        # SOURCE LINE 147
        __M_writer(u'\n    \n    ')
        # SOURCE LINE 183
        __M_writer(u'\n    \n')
        # SOURCE LINE 185
        if add_frame.from_noframe:
            # SOURCE LINE 186
            __M_writer(u'        <div class="warningmessage">\n        <strong>Welcome to Galaxy</strong>\n        <hr/>\n        It appears that you found this tool from a link outside of Galaxy.\n        If you\'re not familiar with Galaxy, please consider visiting the\n        <a href="')
            # SOURCE LINE 191
            __M_writer(unicode(h.url_for( controller='root' )))
            __M_writer(u'" target="_top">welcome page</a>.\n        To learn more about what Galaxy is and what it can do for you, please visit\n        the <a href="$add_frame.wiki_url" target="_top">Galaxy wiki</a>.\n        </div>\n        <br/>\n')
        # SOURCE LINE 197
        __M_writer(u'    \n    <div class="toolForm" id="')
        # SOURCE LINE 198
        __M_writer(unicode(tool.id))
        __M_writer(u'">\n')
        # SOURCE LINE 199
        if tool.has_multiple_pages:
            # SOURCE LINE 200
            __M_writer(u'            <div class="toolFormTitle">')
            __M_writer(unicode(tool.name))
            __M_writer(u' (step ')
            __M_writer(unicode(tool_state.page+1))
            __M_writer(u' of ')
            __M_writer(unicode(tool.npages))
            __M_writer(u')</div>\n')
            # SOURCE LINE 201
        else:
            # SOURCE LINE 202
            __M_writer(u'            <div class="toolFormTitle">')
            __M_writer(unicode(tool.name))
            __M_writer(u'</div>\n')
        # SOURCE LINE 204
        __M_writer(u'        <div class="toolFormBody">\n            <form id="tool_form" name="tool_form" action="')
        # SOURCE LINE 205
        __M_writer(unicode(h.url_for( tool.action )))
        __M_writer(u'" enctype="')
        __M_writer(unicode(tool.enctype))
        __M_writer(u'" target="')
        __M_writer(unicode(tool.target))
        __M_writer(u'" method="')
        __M_writer(unicode(tool.method))
        __M_writer(u'">\n                <input type="hidden" name="tool_id" value="')
        # SOURCE LINE 206
        __M_writer(unicode(tool.id))
        __M_writer(u'">\n                <input type="hidden" name="tool_state" value="')
        # SOURCE LINE 207
        __M_writer(unicode(util.object_to_string( tool_state.encode( tool, app ) )))
        __M_writer(u'">\n')
        # SOURCE LINE 208
        if tool.display_by_page[tool_state.page]:
            # SOURCE LINE 209
            __M_writer(u'                    ')
            __M_writer(unicode(trans.fill_template_string( tool.display_by_page[tool_state.page], context=tool.get_param_html_map( trans, tool_state.page, tool_state.inputs ) )))
            __M_writer(u'\n                    <input type="submit" class="primary-button" name="runtool_btn" value="Execute">\n')
            # SOURCE LINE 211
        else:
            # SOURCE LINE 212
            __M_writer(u'                    ')
            __M_writer(unicode(do_inputs( tool.inputs_by_page[ tool_state.page ], tool_state.inputs, errors, "" )))
            __M_writer(u'\n                    <div class="form-row">\n')
            # SOURCE LINE 214
            if tool_state.page == tool.last_page:
                # SOURCE LINE 215
                __M_writer(u'                            <input type="submit" class="primary-button" name="runtool_btn" value="Execute">\n')
                # SOURCE LINE 216
            else:
                # SOURCE LINE 217
                __M_writer(u'                            <input type="submit" class="primary-button" name="runtool_btn" value="Next step">\n')
            # SOURCE LINE 219
            __M_writer(u'                    </div>\n')
        # SOURCE LINE 221
        __M_writer(u'            </form>\n        </div>\n    </div>\n')
        # SOURCE LINE 224
        if tool.help:
            # SOURCE LINE 225
            __M_writer(u'        <div class="toolHelp">\n            <div class="toolHelpBody">\n                ')
            # SOURCE LINE 227

            if tool.has_multiple_pages:
                tool_help = tool.help_by_page[tool_state.page]
            else:
                tool_help = tool.help
            
            # Convert to unicode to display non-ascii characters.
            if type( tool_help ) is not unicode:
                tool_help = unicode( tool_help, 'utf-8')
                            
            
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['tool_help'] if __M_key in __M_locals_builtin()]))
            # SOURCE LINE 236
            __M_writer(u'\n                ')
            # SOURCE LINE 237
            __M_writer(unicode(tool_help))
            __M_writer(u'\n            </div>        \n        </div>\n')
        # SOURCE LINE 241
        __M_writer(u'</body>\n\n<script type="text/javascript">\n')
        # SOURCE LINE 245
        __M_writer(u"   $( function() {\n       $( 'li > ul' ).each( function( i ) {\n           if ( $( this )[0].className == 'toolParameterExpandableCollapsable' )\n           {\n               var parent_li = $( this ).parent( 'li' );\n               var sub_ul = $( this ).remove();\n               parent_li.find( 'span' ).wrapInner( '<a/>' ).find( 'a' ).click( function() {\n                 sub_ul.toggle();\n                 $( this )[0].innerHTML = ( sub_ul[0].style.display=='none' ) ? '[+]' : '[-]';\n               });\n               parent_li.append( sub_ul );\n           }\n       });\n       $( 'ul ul' ).each( function(i) {\n           if ( $( this )[0].className == 'toolParameterExpandableCollapsable' && this.attributes.getNamedItem( 'default_state' ).value == 'collapsed' )\n           {\n               $( this ).hide();\n           }\n       });\n   });\n\n")
        # SOURCE LINE 267
        __M_writer(u'$( function() {\n    $("div.checkUncheckAllPlaceholder").each( function( i ) {\n        $( this )[0].innerHTML = \'<a class="action-button" onclick="checkUncheckAll( \\\'\' + this.attributes.getNamedItem( \'checkbox_name\' ).value + \'\\\', 1 );"><span>Select All</span></a> <a class="action-button" onclick="checkUncheckAll( \\\'\' + this.attributes.getNamedItem( \'checkbox_name\' ).value + \'\\\', 0 );"><span>Unselect All</span></a>\';\n    });\n});\n\n</script>\n\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_do_inputs(context,inputs,tool_state,errors,prefix,other_values=None):
    context.caller_stack._push_frame()
    try:
        def row_for_param(prefix,param,parent_state,parent_errors,other_values):
            return render_row_for_param(context,prefix,param,parent_state,parent_errors,other_values)
        def do_inputs(inputs,tool_state,errors,prefix,other_values=None):
            return render_do_inputs(context,inputs,tool_state,errors,prefix,other_values)
        len = context.get('len', UNDEFINED)
        range = context.get('range', UNDEFINED)
        dict = context.get('dict', UNDEFINED)
        str = context.get('str', UNDEFINED)
        enumerate = context.get('enumerate', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        ExpressionContext = context.get('ExpressionContext', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 77
        __M_writer(u'\n      ')
        # SOURCE LINE 78
        other_values = ExpressionContext( tool_state, other_values ) 
        
        __M_writer(u'\n')
        # SOURCE LINE 79
        for input_index, input in enumerate( inputs.itervalues() ):
            # SOURCE LINE 80
            if input.type == "repeat":
                # SOURCE LINE 81
                __M_writer(u'              <div class="repeat-group">\n                  <div class="form-title-row"><b>')
                # SOURCE LINE 82
                __M_writer(unicode(input.title_plural))
                __M_writer(u'</b></div>\n                  ')
                # SOURCE LINE 83
                repeat_state = tool_state[input.name] 
                
                __M_writer(u'\n')
                # SOURCE LINE 84
                for i in range( len( repeat_state ) ):
                    # SOURCE LINE 85
                    __M_writer(u'                    <div class="repeat-group-item">\n                    ')
                    # SOURCE LINE 86

                    if input.name in errors:
                        rep_errors = errors[input.name][i]
                    else:
                        rep_errors = dict()
                    index = repeat_state[i]['__index__']
                    
                    
                    # SOURCE LINE 92
                    __M_writer(u'\n                    <div class="form-title-row"><b>')
                    # SOURCE LINE 93
                    __M_writer(unicode(input.title))
                    __M_writer(u' ')
                    __M_writer(unicode(i + 1))
                    __M_writer(u'</b></div>\n                    ')
                    # SOURCE LINE 94
                    __M_writer(unicode(do_inputs( input.inputs, repeat_state[i], rep_errors, prefix + input.name + "_" + str(index) + "|", other_values )))
                    __M_writer(u'\n                    <div class="form-row"><input type="submit" name="')
                    # SOURCE LINE 95
                    __M_writer(unicode(prefix))
                    __M_writer(unicode(input.name))
                    __M_writer(u'_')
                    __M_writer(unicode(index))
                    __M_writer(u'_remove" value="Remove ')
                    __M_writer(unicode(input.title))
                    __M_writer(u' ')
                    __M_writer(unicode(i+1))
                    __M_writer(u'"></div>\n                    </div>\n')
                # SOURCE LINE 98
                __M_writer(u'                  <div class="form-row"><input type="submit" name="')
                __M_writer(unicode(prefix))
                __M_writer(unicode(input.name))
                __M_writer(u'_add" value="Add new ')
                __M_writer(unicode(input.title))
                __M_writer(u'"></div>\n              </div>\n')
                # SOURCE LINE 100
            elif input.type == "conditional":
                # SOURCE LINE 101
                __M_writer(u'                ')

                group_state = tool_state[input.name]
                group_errors = errors.get( input.name, {} )
                current_case = group_state['__current_case__']
                group_prefix = prefix + input.name + "|"
                
                
                # SOURCE LINE 106
                __M_writer(u'\n')
                # SOURCE LINE 107
                if input.value_ref_in_group:
                    # SOURCE LINE 108
                    __M_writer(u'                    ')
                    __M_writer(unicode(row_for_param( group_prefix, input.test_param, group_state, group_errors, other_values )))
                    __M_writer(u'\n')
                # SOURCE LINE 110
                __M_writer(u'                ')
                __M_writer(unicode(do_inputs( input.cases[current_case].inputs, group_state, group_errors, group_prefix, other_values )))
                __M_writer(u'\n')
                # SOURCE LINE 111
            elif input.type == "upload_dataset":
                # SOURCE LINE 112
                if input.get_datatype( trans, other_values ).composite_type is None: #have non-composite upload appear as before
                    # SOURCE LINE 113
                    __M_writer(u'                    ')

                    if input.name in errors:
                        rep_errors = errors[input.name][0]
                    else:
                        rep_errors = dict()
                    
                    
                    # SOURCE LINE 118
                    __M_writer(u'\n                  ')
                    # SOURCE LINE 119
                    __M_writer(unicode(do_inputs( input.inputs, tool_state[input.name][0], rep_errors, prefix + input.name + "_" + str( 0 ) + "|", other_values )))
                    __M_writer(u'\n')
                    # SOURCE LINE 120
                else:
                    # SOURCE LINE 121
                    __M_writer(u'                    <div class="repeat-group">\n                        <div class="form-title-row"><b>')
                    # SOURCE LINE 122
                    __M_writer(unicode(input.group_title( other_values )))
                    __M_writer(u'</b></div>\n                        ')
                    # SOURCE LINE 123
 
                    repeat_state = tool_state[input.name] 
                    
                    
                    # SOURCE LINE 125
                    __M_writer(u'\n')
                    # SOURCE LINE 126
                    for i in range( len( repeat_state ) ):
                        # SOURCE LINE 127
                        __M_writer(u'                          <div class="repeat-group-item">\n                          ')
                        # SOURCE LINE 128

                        if input.name in errors:
                            rep_errors = errors[input.name][i]
                        else:
                            rep_errors = dict()
                        index = repeat_state[i]['__index__']
                        
                        
                        # SOURCE LINE 134
                        __M_writer(u'\n                          <div class="form-title-row"><b>File Contents for ')
                        # SOURCE LINE 135
                        __M_writer(unicode(input.title_by_index( trans, i, other_values )))
                        __M_writer(u'</b></div>\n                          ')
                        # SOURCE LINE 136
                        __M_writer(unicode(do_inputs( input.inputs, repeat_state[i], rep_errors, prefix + input.name + "_" + str(index) + "|", other_values )))
                        __M_writer(u'\n')
                        # SOURCE LINE 138
                        __M_writer(u'                          </div>\n')
                    # SOURCE LINE 141
                    __M_writer(u'                    </div>\n')
                # SOURCE LINE 143
            else:
                # SOURCE LINE 144
                __M_writer(u'                ')
                __M_writer(unicode(row_for_param( prefix, input, tool_state, errors, other_values )))
                __M_writer(u'\n')
        # SOURCE LINE 147
        __M_writer(u'    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_row_for_param(context,prefix,param,parent_state,parent_errors,other_values):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 149
        __M_writer(u'\n        ')
        # SOURCE LINE 150

        if parent_errors.has_key( param.name ):
            cls = "form-row form-row-error"
        else:
            cls = "form-row"
        
        
        # SOURCE LINE 155
        __M_writer(u'\n        <div class="')
        # SOURCE LINE 156
        __M_writer(unicode(cls))
        __M_writer(u'">\n            ')
        # SOURCE LINE 157
        label = param.get_label() 
        
        __M_writer(u'\n')
        # SOURCE LINE 158
        if label:
            # SOURCE LINE 159
            __M_writer(u'                <label>\n                    ')
            # SOURCE LINE 160
            __M_writer(unicode(label))
            __M_writer(u':\n                </label>\n')
        # SOURCE LINE 163
        __M_writer(u'            ')

        field = param.get_html_field( trans, parent_state[ param.name ], other_values )
        field.refresh_on_change = param.refresh_on_change
        
        
        # SOURCE LINE 166
        __M_writer(u'\n            <div class="form-row-input">')
        # SOURCE LINE 167
        __M_writer(unicode(field.get_html( prefix )))
        __M_writer(u'</div>\n')
        # SOURCE LINE 168
        if parent_errors.has_key( param.name ):
            # SOURCE LINE 169
            __M_writer(u'            <div class="form-row-error-message">\n                <div><img style="vertical-align: middle;" src="')
            # SOURCE LINE 170
            __M_writer(unicode(h.url_for('/static/style/error_small.png')))
            __M_writer(u'">&nbsp;<span style="vertical-align: middle;">')
            __M_writer(unicode(parent_errors[param.name]))
            __M_writer(u'</span></div>\n            </div>\n')
        # SOURCE LINE 173
        __M_writer(u'            \n')
        # SOURCE LINE 174
        if param.help:
            # SOURCE LINE 175
            __M_writer(u'            <div class="toolParamHelp" style="clear: both;">\n                ')
            # SOURCE LINE 176
            __M_writer(unicode(param.help))
            __M_writer(u'\n            </div>\n')
        # SOURCE LINE 179
        __M_writer(u'    \n            <div style="clear: both"></div>\n                    \n        </div>\n    ')
        return ''
    finally:
        context.caller_stack._pop_frame()


