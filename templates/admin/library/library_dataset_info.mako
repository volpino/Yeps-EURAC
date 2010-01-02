<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />
<%namespace file="/admin/library/common.mako" import="render_template_info" />

%if library_dataset == library_dataset.library_dataset_dataset_association.library_dataset:
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

<div class="toolForm">
    <div class="toolFormTitle">Edit attributes of ${library_dataset.name}</div>
    <div class="toolFormBody">
        <form name="edit_attributes" action="${h.url_for( controller='library_admin', action='library_dataset' )}" method="post">
            <input type="hidden" name="obj_id" value="${library_dataset.id}"/>
            <div class="form-row">
                <label>Name:</label>
                <div style="float: left; width: 250px; margin-right: 10px;">
                    <input type="text" name="name" value="${library_dataset.name}" size="40"/>
                </div>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <label>Info:</label>
                <div style="float: left; width: 250px; margin-right: 10px;">
                    <input type="text" name="info" value="${library_dataset.info}" size="40"/>
                </div>
                <div style="clear: both"></div>
            </div> 
            <div class="form-row">
                <input type="submit" name="edit_attributes_button" value="Save"/>
            </div>
        </form>
    </div>
</div>

%if widgets:
    ${render_template_info( library_dataset, library.id, '', widgets )}
%endif
