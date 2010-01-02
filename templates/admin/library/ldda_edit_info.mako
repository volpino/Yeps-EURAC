<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />
<%namespace file="/admin/library/common.mako" import="render_template_info" />
<% from galaxy import util %>

<%def name="javascripts()">
   ${parent.javascripts()}
   ${h.js("jquery.autocomplete", "autocomplete_tagging" )}
    ## Script to replace dbkey select with select+search.
   <script type="text/javascript">
       // Replace dbkey select with search+select.
       jQuery(document).ready( function() {
           replace_dbkey_select();
       });
   </script>
</%def>

<%def name="stylesheets()">
    ${parent.stylesheets()}
    ${h.css( "autocomplete_tagging" )}
</%def>

%if ldda == ldda.library_dataset.library_dataset_dataset_association:
    <b><i>This is the latest version of this library dataset</i></b>
%else:
    <font color="red"><b><i>This is an expired version of this library dataset</i></b></font>
%endif
<p/>

<ul class="manage-table-actions">
    <li>
        <a class="action-button" href="${h.url_for( controller='library_admin', action='browse_library', obj_id=library_id )}"><span>Browse this data library</span></a>
    </li>
</ul>

%if msg:
    ${render_msg( msg, messagetype )}
%endif

<%def name="datatype( ldda, file_formats )">
    <select name="datatype">
        %for ext in file_formats:
            %if ldda.ext == ext:
                <option value="${ext}" selected="yes">${ext}</option>
            %else:
                <option value="${ext}">${ext}</option>
            %endif
        %endfor
    </select>
</%def>

<div class="toolForm">
    <div class="toolFormTitle">Edit attributes of ${ldda.name}</div>
    <div class="toolFormBody">
        <form name="edit_attributes" action="${h.url_for( controller='library_admin', action='ldda_edit_info', library_id=library_id, folder_id=ldda.library_dataset.folder.id )}" method="post">
            <input type="hidden" name="obj_id" value="${ldda.id}"/>
            <br/>
            <div class="form-row">
                <label>Name:</label>
                <input type="text" name="name" value="${ldda.name}" size="40"/>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <label>Info:</label>
                <input type="text" name="info" value="${ldda.info}" size="40"/>
                <div style="clear: both"></div>
            </div> 
            <div class="form-row">
                <label>Message:</label>
                %if ldda.message:
                    <textarea name="message" rows="3" cols="35">${ldda.message}</textarea>
                %else:
                    <textarea name="message" rows="3" cols="35"></textarea>
                %endif
                <div class="toolParamHelp" style="clear: both;">
                    This information will be displayed in the library browser
                </div>
                <div style="clear: both"></div>
            </div>
            %for name, spec in ldda.metadata.spec.items():
                %if spec.visible:
                    <div class="form-row">
                        <label>${spec.desc}:</label>
                        ${ldda.metadata.get_html_by_name( name, trans=trans )}
                        <div style="clear: both"></div>
                    </div>
                %endif
            %endfor
            <div class="form-row">
                <input type="submit" name="save" value="Save"/>
            </div>
        </form>
        <form name="auto_detect" action="${h.url_for( controller='library_admin', action='ldda_edit_info', library_id=library_id, folder_id=ldda.library_dataset.folder.id )}" method="post">
            <div class="form-row">
                <input type="hidden" name="obj_id" value="${ldda.id}"/>
                <input type="submit" name="detect" value="Auto-detect"/>
                <div class="toolParamHelp" style="clear: both;">
                    This will inspect the dataset and attempt to correct the above column values if they are not accurate.
                </div>
            </div>
        </form>
    </div>
</div>
<p/>
<div class="toolForm">
    <div class="toolFormTitle">Change data type of ${ldda.name}</div>
    <div class="toolFormBody">
        %if ldda.datatype.allow_datatype_change:
            <form name="change_datatype" action="${h.url_for( controller='library_admin', action='ldda_edit_info', library_id=library_id, folder_id=ldda.library_dataset.folder.id )}" method="post">
                <input type="hidden" name="obj_id" value="${ldda.id}"/>
                <div class="form-row">
                    <label>New Type:</label>
                    ${datatype( ldda, file_formats )}
                    <div class="toolParamHelp" style="clear: both;">
                        This will change the datatype of the existing dataset
                        but <i>not</i> modify its contents. Use this if Galaxy
                        has incorrectly guessed the type of your dataset.
                    </div>
                    <div style="clear: both"></div>
                </div>
                <div class="form-row">
                    <input type="submit" name="change" value="Save"/>
                </div>
            </form>
        %else:
            <div class="form-row">
                <div class="warningmessagesmall">${_('Changing the datatype of this dataset is not allowed.')}</div>
            </div>
        %endif
    </div>
</div>

%if widgets:
    ${render_template_info( ldda, library_id, 'ldda_edit_info', widgets )}
%endif
