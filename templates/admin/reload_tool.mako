<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />

%if msg:
    ${render_msg( msg, messagetype )}
%endif

<div class="toolForm">
    <div class="toolFormTitle">Reload Tool</div>
    <div class="toolFormBody">
    <form name="tool_reload" action="${h.url_for( controller='admin', action='tool_reload' )}" method="post" >
        <div class="form-row">
            <label>
                Tool to reload:
            </label>
            <select name="tool_id">
                %for key, val in toolbox.tool_panel.items():
                    %if key.startswith( 'tool' ):
                        <option value="${val.id}">${val.name}</option>
                    %elif key.startswith( 'section' ):
                        <optgroup label="${val.name}">
                        <% section = val %>
                        %for section_key, section_val in section.elems.items():
                            %if section_key.startswith( 'tool' ):
                                <option value="${section_val.id}">${section_val.name}</option>
                            %endif
                        %endfor
                    %endif
                %endfor
            </select>
        </div>
        <div class="form-row">
            <input type="submit" name="action" value="Reload"/>
        </div>
    </form>
    </div>
</div>
