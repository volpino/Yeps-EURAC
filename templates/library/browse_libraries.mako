<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />

<%def name="title()">Browse Data Libraries</%def>

<h2>Data Libraries</h2>

%if msg:
    ${render_msg( msg, messagetype )}
%endif

%if not libraries:
    You are not authorized to access any libraries
%else:
    <table class="grid">
        <thead>
            <tr>
                <th>Name</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            %for library, hidden_folder_ids in libraries.items():    
                <tr class="libraryRow libraryOrFolderRow" id="libraryRow">
                    <td><a href="${h.url_for( controller='library', action='browse_library', obj_id=library.id, hidden_folder_ids=hidden_folder_ids )}">${library.name}</a></td>
                    <td><i>${library.description}</i></td>
                </tr>             
            %endfor
        </tbody>
    </table>
%endif
