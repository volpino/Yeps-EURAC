from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381896.584774
_template_filename=u'templates/base_panels.mako'
_template_uri=u'/base_panels.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = ['message_box_content', 'title', 'overlay', 'late_javascripts', 'stylesheets', 'init', 'masthead', 'javascripts']


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 2
        __M_writer(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n\n')
        # SOURCE LINE 4

        self.has_left_panel=True
        self.has_right_panel=True
        self.message_box_visible=False
        self.overlay_visible=False
        self.message_box_class=""
        self.active_view=None
        self.body_class=""
        
        
        # SOURCE LINE 12
        __M_writer(u'\n    \n')
        # SOURCE LINE 16
        __M_writer(u'\n\n')
        # SOURCE LINE 19
        __M_writer(u'\n\n')
        # SOURCE LINE 40
        __M_writer(u'\n\n')
        # SOURCE LINE 48
        __M_writer(u'\n\n')
        # SOURCE LINE 133
        __M_writer(u'\n\n')
        # SOURCE LINE 274
        __M_writer(u'\n\n')
        # SOURCE LINE 309
        __M_writer(u'\n\n')
        # SOURCE LINE 313
        __M_writer(u'\n\n')
        # SOURCE LINE 316
        __M_writer(u'<html>\n    ')
        # SOURCE LINE 317
        __M_writer(unicode(self.init()))
        __M_writer(u'    \n    <head>\n    <title>')
        # SOURCE LINE 319
        __M_writer(unicode(self.title()))
        __M_writer(u'</title>\n    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n    ')
        # SOURCE LINE 321
        __M_writer(unicode(self.javascripts()))
        __M_writer(u'\n    ')
        # SOURCE LINE 322
        __M_writer(unicode(self.stylesheets()))
        __M_writer(u'\n    </head>\n    \n    <body scroll="no" class="')
        # SOURCE LINE 325
        __M_writer(unicode(self.body_class))
        __M_writer(u'">\n\t<div id="everything" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; min-width: 600px;">\n')
        # SOURCE LINE 328
        __M_writer(u'        <div id="background"></div>\n')
        # SOURCE LINE 330
        __M_writer(u'        <div id="masthead">\n            ')
        # SOURCE LINE 331
        __M_writer(unicode(self.masthead()))
        __M_writer(u'\n        </div>\n        <div id="messagebox" class="panel-')
        # SOURCE LINE 333
        __M_writer(unicode(self.message_box_class))
        __M_writer(u'-message">\n')
        # SOURCE LINE 334
        if self.message_box_visible:
            # SOURCE LINE 335
            __M_writer(u'                ')
            __M_writer(unicode(self.message_box_content()))
            __M_writer(u'\n')
        # SOURCE LINE 337
        __M_writer(u'        </div>\n    ')
        # SOURCE LINE 338
        __M_writer(unicode(self.overlay()))
        __M_writer(u'\n')
        # SOURCE LINE 339
        if self.has_left_panel:
            # SOURCE LINE 340
            __M_writer(u'            <div id="left">\n                ')
            # SOURCE LINE 341
            __M_writer(unicode(self.left_panel()))
            __M_writer(u'\n            </div>\n            <div id="left-border">\n                <div id="left-border-inner" style="display: none;"></div>\n            </div>\n')
        # SOURCE LINE 347
        __M_writer(u'        <div id="center">\n            ')
        # SOURCE LINE 348
        __M_writer(unicode(self.center_panel()))
        __M_writer(u'\n        </div>\n')
        # SOURCE LINE 350
        if self.has_right_panel:
            # SOURCE LINE 351
            __M_writer(u'            <div id="right-border"><div id="right-border-inner" style="display: none;"></div></div>\n            <div id="right">\n                ')
            # SOURCE LINE 353
            __M_writer(unicode(self.right_panel()))
            __M_writer(u'\n            </div>\n')
        # SOURCE LINE 356
        __M_writer(u'\t</div>\n')
        # SOURCE LINE 358
        __M_writer(u'    </body>\n')
        # SOURCE LINE 361
        __M_writer(u'    ')
        __M_writer(unicode(self.late_javascripts()))
        __M_writer(u'\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_message_box_content(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 312
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_title(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 19
        __M_writer(u'Galaxy')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_overlay(context,title='',content=''):
    context.caller_stack._push_frame()
    try:
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 276
        __M_writer(u'\n    ')
        # SOURCE LINE 277
        __M_writer(u'\n    ')
        # SOURCE LINE 278
        __M_writer(u'\n\n    <div id="overlay"\n')
        # SOURCE LINE 281
        if not self.overlay_visible:
            # SOURCE LINE 282
            __M_writer(u'    style="display: none;"\n')
        # SOURCE LINE 284
        __M_writer(u'    >\n')
        # SOURCE LINE 286
        __M_writer(u'    <div id="overlay-background" style="position: absolute; width: 100%; height: 100%;"></div>\n    \n')
        # SOURCE LINE 289
        __M_writer(u'    <table class="dialog-box-container" border="0" cellpadding="0" cellspacing="0"\n')
        # SOURCE LINE 290
        if not self.overlay_visible:
            # SOURCE LINE 291
            __M_writer(u'        style="display: none;"\n')
        # SOURCE LINE 293
        __M_writer(u'    ><tr><td>\n    <div class="dialog-box-wrapper">\n        <div class="dialog-box">\n        <div class="unified-panel-header">\n            <div class="unified-panel-header-inner"><span class=\'title\'>')
        # SOURCE LINE 297
        __M_writer(unicode(title))
        __M_writer(u'</span></div>\n        </div>\n        <div class="body" style="max-height: 600px; overflow: auto;">')
        # SOURCE LINE 299
        __M_writer(unicode(content))
        __M_writer(u'</div>\n        <div>\n            <div class="buttons" style="display: none; float: right;"></div>\n            <div class="extra_buttons" style="display: none; padding: 5px;"></div>\n            <div style="clear: both;"></div>\n        </div>\n        </div>\n    </div>\n    </td></tr></table>\n    </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_late_javascripts(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 51
        __M_writer(u'\n')
        # SOURCE LINE 54
        __M_writer(u'    ')
        __M_writer(unicode(h.js( 'jquery.event.drag', 'jquery.event.hover', 'jquery.form', 'galaxy.base', 'galaxy.panels' )))
        __M_writer(u'\n    <script type="text/javascript">\n        \n    ensure_dd_helper();\n        \n')
        # SOURCE LINE 59
        if self.has_left_panel:
            # SOURCE LINE 60
            __M_writer(u'            var lp = make_left_panel( $("#left"), $("#center"), $("#left-border" ) );\n            force_left_panel = lp.force_panel;\n')
        # SOURCE LINE 63
        __M_writer(u'        \n')
        # SOURCE LINE 64
        if self.has_right_panel:
            # SOURCE LINE 65
            __M_writer(u'            var rp = make_right_panel( $("#right"), $("#center"), $("#right-border" ) );\n            handle_minwidth_hint = rp.handle_minwidth_hint;\n            force_right_panel = rp.force_panel;\n')
        # SOURCE LINE 69
        __M_writer(u'    \n    </script>\n')
        # SOURCE LINE 72
        __M_writer(u'    <![if !IE]>\n    <script type="text/javascript">\n        var upload_form_error = function( msg ) {\n            if ( ! $("iframe#galaxy_main").contents().find("body").find("div[name=\'upload_error\']").size() ) {\n                $("iframe#galaxy_main").contents().find("body").prepend( \'<div class="errormessage" name="upload_error">\' + msg + \'</div><p/>\' );\n            } else {\n                $("iframe#galaxy_main").contents().find("body").find("div[name=\'upload_error\']").text( msg );\n            }\n        }\n        jQuery( function() {\n            $("iframe#galaxy_main").load( function() {\n                $(this).contents().find("form").each( function() { \n                    if ( $(this).find("input[galaxy-ajax-upload]").length > 0 ){\n                        $(this).submit( function() {\n                            // Only bother using a hidden iframe if there\'s a file (e.g. big data) upload\n                            var file_upload = false;\n                            $(this).find("input[galaxy-ajax-upload]").each( function() {\n                                if ( $(this).val() != \'\' ) {\n                                    file_upload = true;\n                                }\n                            });\n                            if ( ! file_upload ) {\n                                return true;\n                            }\n                            // Make a synchronous request to create the datasets first\n                            var async_datasets;\n                            $.ajax( {\n                                async:      false,\n                                type:       "POST",\n                                url:        "')
        # SOURCE LINE 101
        __M_writer(unicode(h.url_for(controller='tool_runner', action='upload_async_create')))
        __M_writer(u'",\n                                data:       $(this).formSerialize(),\n                                dataType:   "json",\n                                success:    function( d, s ) { async_datasets = d.join() }\n                            } );\n                            if (async_datasets == \'\') {\n                                upload_form_error( \'No data was entered in the upload form.  You may choose to upload a file, paste some data directly in the data box, or enter URL(s) to fetch from.\' );\n                                return false;\n                            } else {\n                                $(this).find("input[name=async_datasets]").val( async_datasets );\n                                $(this).append("<input type=\'hidden\' name=\'ajax_upload\' value=\'true\'>");\n                            }\n                            // iframe submit is required for nginx (otherwise the encoding is wrong)\n                            $(this).ajaxSubmit( { iframe: true } );\n                            if ( $(this).find("input[name=\'folder_id\']").val() != undefined ) {\n                                var library_id = $(this).find("input[name=\'library_id\']").val();\n                                if ( location.pathname.indexOf( \'library_admin\' ) != -1 ) {\n                                    $("iframe#galaxy_main").attr("src","')
        # SOURCE LINE 118
        __M_writer(unicode(h.url_for( controller='library_admin', action='browse_library' )))
        __M_writer(u'?obj_id=" + library_id + "&created_ldda_ids=" + async_datasets);\n                                } else {\n                                    $("iframe#galaxy_main").attr("src","')
        # SOURCE LINE 120
        __M_writer(unicode(h.url_for( controller='library', action='browse_library' )))
        __M_writer(u'?obj_id=" + library_id + "&created_ldda_ids=" + async_datasets);\n                                }\n                            } else {\n                                $("iframe#galaxy_main").attr("src","')
        # SOURCE LINE 123
        __M_writer(unicode(h.url_for(controller='tool_runner', action='upload_async_message')))
        __M_writer(u'");\n                            }\n                            return false;\n                        });\n                    }\n                });\n            });\n        });\n    </script>\n    <![endif]>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_stylesheets(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        self = context.get('self', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 22
        __M_writer(u'\n    ')
        # SOURCE LINE 23
        __M_writer(unicode(h.css('base','panel_layout')))
        __M_writer(u'\n    <style type="text/css">\n    #center {\n')
        # SOURCE LINE 26
        if not self.has_left_panel:
            # SOURCE LINE 27
            __M_writer(u'            left: 0;\n')
        # SOURCE LINE 29
        if not self.has_right_panel:
            # SOURCE LINE 30
            __M_writer(u'            right: 0;\n')
        # SOURCE LINE 32
        __M_writer(u'    }\n')
        # SOURCE LINE 33
        if self.message_box_visible:
            # SOURCE LINE 34
            __M_writer(u'        #left, #left-border, #center, #right-border, #right\n        {\n            top: 64px;\n        }\n')
        # SOURCE LINE 39
        __M_writer(u'    </style>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_init(context):
    context.caller_stack._push_frame()
    try:
        __M_writer = context.writer()
        # SOURCE LINE 14
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_masthead(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        app = context.get('app', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        self = context.get('self', UNDEFINED)
        def tab(id,display,href,target='_parent',visible=True,extra_class=''):
            context.caller_stack._push_frame()
            try:
                __M_writer = context.writer()
                # SOURCE LINE 144
                __M_writer(u'\n        ')
                # SOURCE LINE 145

                cls = "tab"
                if extra_class:
                    cls += " " + extra_class
                if self.active_view == id:
                    cls += " active"
                style = ""
                if not visible:
                    style = "display: none;"
                
                
                # SOURCE LINE 154
                __M_writer(u'\n        <td class="')
                # SOURCE LINE 155
                __M_writer(unicode(cls))
                __M_writer(u'" style="')
                __M_writer(unicode(style))
                __M_writer(u'"><a target="')
                __M_writer(unicode(target))
                __M_writer(u'" href="')
                __M_writer(unicode(href))
                __M_writer(u'">')
                __M_writer(unicode(display))
                __M_writer(u'</a></td>\n    ')
                return ''
            finally:
                context.caller_stack._pop_frame()
        __M_writer = context.writer()
        # SOURCE LINE 136
        __M_writer(u'\n\n')
        # SOURCE LINE 139
        __M_writer(u'    <div style="position: absolute; top: 0; left: 0; width: 100%; text-align: center">\n    \n    <table class="tab-group" border="0" cellspacing="0" style="margin: auto;">\n\t<tr>\n    \n    ')
        # SOURCE LINE 156
        __M_writer(u'\n    \n')
        # SOURCE LINE 158
        if app.config.cloud_controller_instance:
            # SOURCE LINE 159
            __M_writer(u'\t\t')
            __M_writer(unicode(tab( "cloud", "Cloud", h.url_for( controller='cloud', action='index' ))))
            __M_writer(u'\n')
            # SOURCE LINE 160
        else:
            # SOURCE LINE 161
            __M_writer(u'    \t')
            __M_writer(unicode(tab( "analysis", "Analyze Data", h.url_for( controller='root', action='index' ))))
            __M_writer(u'\n\t    \n\t    ')
            # SOURCE LINE 163
            __M_writer(unicode(tab( "workflow", "Workflow", h.url_for( controller='workflow', action='index' ))))
            __M_writer(u'\n\t    \n\t    ')
            # SOURCE LINE 165
            __M_writer(unicode(tab( "libraries", "Data Libraries", h.url_for( controller='library', action='index' ))))
            __M_writer(u'\n')
        # SOURCE LINE 167
        __M_writer(u'    \n')
        # SOURCE LINE 168
        if trans.user and trans.request_types():
            # SOURCE LINE 169
            __M_writer(u'        <td class="tab">\n            <a>Lab</a>\n            <div class="submenu">\n            <ul>            \n                <li><a href="')
            # SOURCE LINE 173
            __M_writer(unicode(h.url_for( controller='requests', action='index' )))
            __M_writer(u'">Sequencing Requests</a></li>\n            </ul>\n            </div>\n        </td>\n')
        # SOURCE LINE 178
        __M_writer(u'\n')
        # SOURCE LINE 179
        if app.config.get_bool( 'enable_tracks', False ):
            # SOURCE LINE 180
            __M_writer(u'    ')

            cls = "tab"
            if self.active_view == 'visualization':
                cls += " active"
            
            
            # SOURCE LINE 184
            __M_writer(u'\n    <td class="')
            # SOURCE LINE 185
            __M_writer(unicode(cls))
            __M_writer(u'">\n        Visualization\n        <div class="submenu">\n        <ul>\n            <li><a href="')
            # SOURCE LINE 189
            __M_writer(unicode(h.url_for( controller='tracks', action='index' )))
            __M_writer(u'">Build track browser</a></li>\n            <li><hr style="color: inherit; background-color: gray"/></li>\n\t    <li><a href="')
            # SOURCE LINE 191
            __M_writer(unicode(h.url_for( controller='visualization', action='index' )))
            __M_writer(u'">Stored visualizations</a></li>\n        </ul>\n        </div>\n    </td>\n')
        # SOURCE LINE 196
        __M_writer(u'\n    ')
        # SOURCE LINE 197
        __M_writer(unicode(tab( "admin", "Admin", h.url_for( controller='admin', action='index' ), extra_class="admin-only", visible=( trans.user and app.config.is_admin_user( trans.user ) ) )))
        __M_writer(u'\n    \n    <td class="tab">\n        <a>Help</a>\n        <div class="submenu">\n        <ul>            \n            <li><a href="')
        # SOURCE LINE 203
        __M_writer(unicode(app.config.get( "bugs_email", "mailto:galaxy-bugs@bx.psu.edu"  )))
        __M_writer(u'">Email comments, bug reports, or suggestions</a></li>\n            <li><a target="_blank" href="')
        # SOURCE LINE 204
        __M_writer(unicode(app.config.get( "wiki_url", "http://bitbucket.org/galaxy/galaxy-central/wiki" )))
        __M_writer(u'">Galaxy Wiki</a></li>             \n            <li><a target="_blank" href="')
        # SOURCE LINE 205
        __M_writer(unicode(app.config.get( "screencasts_url", "http://galaxycast.org" )))
        __M_writer(u'">Video tutorials (screencasts)</a></li>\n            <li><a target="_blank" href="')
        # SOURCE LINE 206
        __M_writer(unicode(app.config.get( "citation_url", "http://bitbucket.org/galaxy/galaxy-central/wiki/Citations" )))
        __M_writer(u'">How to Cite Galaxy</a></li>\n        </ul>\n        </div>\n    </td>\n    \n    <td class="tab">\n        <a>User</a>\n        ')
        # SOURCE LINE 213

        if trans.user:
            user_email = trans.user.email
            style1 = "display: none;"
            style2 = "";
        else:
            user_email = ""
            style1 = ""
            style2 = "display: none;"
        
        
        # SOURCE LINE 222
        __M_writer(u'\n        <div class="submenu">\n        <ul class="loggedout-only" style="')
        # SOURCE LINE 224
        __M_writer(unicode(style1))
        __M_writer(u'">\n            <li><a target="galaxy_main" href="')
        # SOURCE LINE 225
        __M_writer(unicode(h.url_for( controller='user', action='login' )))
        __M_writer(u'">Login</a></li>\n')
        # SOURCE LINE 226
        if app.config.allow_user_creation:
            # SOURCE LINE 227
            __M_writer(u'            <li><a target="galaxy_main" href="')
            __M_writer(unicode(h.url_for( controller='user', action='create' )))
            __M_writer(u'">Register</a></li>\n')
        # SOURCE LINE 229
        __M_writer(u'        </ul>\n        <ul class="loggedin-only" style="')
        # SOURCE LINE 230
        __M_writer(unicode(style2))
        __M_writer(u'">\n')
        # SOURCE LINE 231
        if app.config.use_remote_user:
            # SOURCE LINE 232
            if app.config.remote_user_logout_href:
                # SOURCE LINE 233
                __M_writer(u'                    <li><a href="')
                __M_writer(unicode(app.config.remote_user_logout_href))
                __M_writer(u'" target="_top">Logout</a></li>\n')
            # SOURCE LINE 235
        else:
            # SOURCE LINE 236
            __M_writer(u'                <li>Logged in as <span id="user-email">')
            __M_writer(unicode(user_email))
            __M_writer(u'</span></li>\n                <li><a target="galaxy_main" href="')
            # SOURCE LINE 237
            __M_writer(unicode(h.url_for( controller='user', action='index' )))
            __M_writer(u'">Preferences</a></li>\n                ')
            # SOURCE LINE 238

            if app.config.require_login:
                logout_target = ""
                logout_url = h.url_for( controller='root', action='index', m_c='user', m_a='logout' )
            else:
                logout_target = "galaxy_main"
                logout_url = h.url_for( controller='user', action='logout' )
                            
            
            # SOURCE LINE 245
            __M_writer(u'\n                <li><a target="')
            # SOURCE LINE 246
            __M_writer(unicode(logout_target))
            __M_writer(u'" href="')
            __M_writer(unicode(logout_url))
            __M_writer(u'">Logout</a></li>\n                <li><hr style="color: inherit; background-color: gray"/></li>\n                <li><a target="galaxy_main" href="')
            # SOURCE LINE 248
            __M_writer(unicode(h.url_for( controller='history', action='list' )))
            __M_writer(u'">Histories</a></li>\n                <li><a target="galaxy_main" href="')
            # SOURCE LINE 249
            __M_writer(unicode(h.url_for( controller='dataset', action='list' )))
            __M_writer(u'">Datasets</a></li>\n')
            # SOURCE LINE 250
            if app.config.get_bool( 'enable_pages', False ):
                # SOURCE LINE 251
                __M_writer(u'                    <li><a href="')
                __M_writer(unicode(h.url_for( controller='page' )))
                __M_writer(u'">Pages</a></li>  \n')
        # SOURCE LINE 254
        __M_writer(u'        </ul>\n        </div>\n    </td>\n    \n    </tr>\n    </table>\n    \n    </div>\n    \n')
        # SOURCE LINE 264
        __M_writer(u'    <div class="title" style="position: absolute; top: 0; left: 0;">\n        <a href="/">\n        <img border="0" src="')
        # SOURCE LINE 266
        __M_writer(unicode(h.url_for('/static/images/galaxyIcon_noText.png')))
        __M_writer(u'" style="width: 26px; vertical-align: top;">\n        Galaxy\n')
        # SOURCE LINE 268
        if app.config.brand:
            # SOURCE LINE 269
            __M_writer(u"        <span class='brand'>/")
            __M_writer(unicode(app.config.brand))
            __M_writer(u'</span>\n')
        # SOURCE LINE 271
        __M_writer(u'        </a>\n    </div>\n    \n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_javascripts(context):
    context.caller_stack._push_frame()
    try:
        h = context.get('h', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 43
        __M_writer(u'\n    <!--[if lt IE 7]>\n    ')
        # SOURCE LINE 45
        __M_writer(unicode(h.js( 'IE7', 'ie7-recalc' )))
        __M_writer(u'\n    <![endif]-->\n    ')
        # SOURCE LINE 47
        __M_writer(unicode(h.js( 'jquery' )))
        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


