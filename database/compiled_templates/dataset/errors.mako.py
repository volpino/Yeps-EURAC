from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 5
_modified_time = 1262381927.6520419
_template_filename='templates/dataset/errors.mako'
_template_uri='dataset/errors.mako'
_template_cache=cache.Cache(__name__, _modified_time)
_source_encoding=None
_exports = []


def render_body(context,**pageargs):
    context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        h = context.get('h', UNDEFINED)
        trans = context.get('trans', UNDEFINED)
        hda = context.get('hda', UNDEFINED)
        __M_writer = context.writer()
        # SOURCE LINE 1
        __M_writer(u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<html>\n    <head>\n        <title>Dataset generation errors</title>\n        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n        <link href="/static/style/base.css" rel="stylesheet" type="text/css" />\n        <style>\n            pre\n            {\n                background: white;\n                color: black;\n                border: dotted black 1px;\n                overflow: auto;\n                padding: 10px;\n            }\n        </style>\n    </head>\n\n    <body>\n        <h2>Dataset generation errors</h2>\n        <p><b>Dataset ')
        # SOURCE LINE 21
        __M_writer(unicode(hda.hid))
        __M_writer(u': ')
        __M_writer(unicode(hda.display_name()))
        __M_writer(u'</b></p>\n\n')
        # SOURCE LINE 23
        if hda.creating_job_associations:
            # SOURCE LINE 24
            __M_writer(u'            ')
            job = hda.creating_job_associations[0].job 
            
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['job'] if __M_key in __M_locals_builtin()]))
            __M_writer(u'\n')
            # SOURCE LINE 25
            if job.traceback:
                # SOURCE LINE 26
                __M_writer(u'                The Galaxy framework encountered the following error while attempting to run the tool:\n                <pre>')
                # SOURCE LINE 27
                __M_writer(unicode(job.traceback))
                __M_writer(u'</pre>\n')
            # SOURCE LINE 29
            if job.stderr or job.info:
                # SOURCE LINE 30
                __M_writer(u'                Tool execution generated the following error message:\n')
                # SOURCE LINE 31
                if job.stderr:
                    # SOURCE LINE 32
                    __M_writer(u'                    <pre>')
                    __M_writer(unicode(job.stderr))
                    __M_writer(u'</pre>\n')
                    # SOURCE LINE 33
                elif job.info:
                    # SOURCE LINE 34
                    __M_writer(u'                    <pre>')
                    __M_writer(unicode(job.info))
                    __M_writer(u'</pre>\n')
                # SOURCE LINE 36
            else:
                # SOURCE LINE 37
                __M_writer(u'                Tool execution did not generate any error messages.\n')
            # SOURCE LINE 39
            if job.stdout:
                # SOURCE LINE 40
                __M_writer(u'                The tool produced the following additional output:\n                <pre>')
                # SOURCE LINE 41
                __M_writer(unicode(job.stdout))
                __M_writer(u'</pre>\n')
            # SOURCE LINE 43
        else:
            # SOURCE LINE 44
            __M_writer(u'            The tool did not create any additional job / error info.\n')
        # SOURCE LINE 46
        __M_writer(u'        ')

        if trans.user:
            user_email = trans.user.email
        else:
            user_email = ''
                
        
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin()[__M_key]) for __M_key in ['user_email'] if __M_key in __M_locals_builtin()]))
        # SOURCE LINE 51
        __M_writer(u'\n        <h2>Report this error to the Galaxy Team</h2>\n        <p>\n            The Galaxy team regularly reviews errors that occur in the application. \n            However, if you would like to provide additional information (such as \n            what you were trying to do when the error occurred) and a contact e-mail\n            address, we will be better able to investigate your problem and get back\n            to you.\n        </p>\n        <div class="toolForm">\n            <div class="toolFormTitle">Error Report</div>\n            <div class="toolFormBody">\n                <form name="report_error" action="')
        # SOURCE LINE 63
        __M_writer(unicode(h.url_for( action='report_error')))
        __M_writer(u'" method="post" >\n                    <input type="hidden" name="id" value="')
        # SOURCE LINE 64
        __M_writer(unicode(hda.id))
        __M_writer(u'" />\n                    <div class="form-row">\n                        <label>Your email</label>\n                        <input type="text" name="email" size="40" value="')
        # SOURCE LINE 67
        __M_writer(unicode(user_email))
        __M_writer(u'" />\n                    </div>\n                    <div class="form-row">\n                        <label>Message</label>\n                        <textarea name="message" rows="10" cols="40"></textarea>\n                    </div>\n                    <div class="form-row">\n                        <input type="submit" value="Report"/>\n                    </div>\n                </form>\n            </div>\n      </div>\n    </body>\n</html>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


