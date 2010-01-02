<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />
<%namespace file="/admin/library/common.mako" import="render_template_info" />

<br/><br/>
<ul class="manage-table-actions">
    <li>
        <a class="action-button" href="${h.url_for( controller='library_admin', action='browse_library', obj_id=library.id )}"><span>Browse this data library</span></a>
    </li>
</ul>

%if msg:
    ${render_msg( msg, messagetype )}
%endif

<div class="toolForm">
    <div class="toolFormTitle">Change library name and description</div>
    <div class="toolFormBody">
        <form name="library" action="${h.url_for( controller='library_admin', action='library', information=True, obj_id=library.id )}" method="post" >
            <div class="form-row">
                <label>Name:</label>
                <div style="float: left; width: 250px; margin-right: 10px;">
                    <input type="text" name="name" value="${library.name}" size="40"/>
                </div>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <label>Description:</label>
                <div style="float: left; width: 250px; margin-right: 10px;">
                    <input type="text" name="description" value="${library.description}" size="40"/>
                </div>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <input type="submit" name="rename_library_button" value="Save"/>
            </div>
        </form>
    </div>
</div>

<%
    roles = trans.sa_session.query( trans.app.model.Role ) \
                            .filter( trans.app.model.Role.table.c.deleted==False ) \
                            .order_by( trans.app.model.Role.table.c.name )
    trans.sa_session.refresh( library )
%>

%if widgets:
    ${render_template_info( library, library.id, 'library', widgets )}
%endif
