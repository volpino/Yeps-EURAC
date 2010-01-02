<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />
<%namespace file="/admin/library/common.mako" import="render_template_info" />

<br/><br/>
<ul class="manage-table-actions">
    <li>
        <a class="action-button" href="${h.url_for( controller='library_admin', action='browse_library', obj_id=library_id )}"><span>Browse this data library</span></a>
    </li>
</ul>

%if msg:
    ${render_msg( msg, messagetype )}
%endif

<div class="toolForm">
    <div class="toolFormTitle">Edit folder name and description</div>
    <div class="toolFormBody">
        <form name="folder" action="${h.url_for( controller='library_admin', action='folder', information=True, obj_id=folder.id, library_id=library_id )}" method="post" >
            <div class="form-row">
                <label>Name:</label>
                <input type="text" name="name" value="${folder.name}" size="40"/>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <label>Description:</label>
                <input type="text" name="description" value="${folder.description}" size="40"/>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <input type="submit" name="rename_folder_button" value="Save"/>
            </div>
        </form>
    </div>
</div>

%if widgets:
    ${render_template_info( folder, library_id, 'folder', widgets )}
%endif
