<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />
<%namespace file="/dataset/security_common.mako" import="render_permission_form" />

%if library_dataset == library_dataset.library_dataset_dataset_association:
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

<%
    roles = trans.sa_session.query( trans.app.model.Role ) \
                            .filter( trans.app.model.Role.table.c.deleted==False ) \
                            .order_by( trans.app.model.Role.table.c.name )
%>

${render_permission_form( library_dataset, library_dataset.name, h.url_for( controller='library_admin', action='library_dataset', obj_id=library_dataset.id, library_id=library_id, permissions=True ), roles )}
