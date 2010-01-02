<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />

<%def name="title()">${_('Edit Dataset Attributes')}</%def>

<%def name="stylesheets()">
    ${h.css( "base", "autocomplete_tagging" )}
</%def>
<% user, user_roles = trans.get_user_and_roles() %>

<%def name="javascripts()">
    ${parent.javascripts()}
    ${h.js( "galaxy.base", "jquery.autocomplete", "autocomplete_tagging" )}
    <script type="text/javascript">
        $(document).ready(function() 
        {
            replace_dbkey_select('${data.dbkey}');
        });
    </script>
</%def>

<%def name="datatype( dataset, datatypes )">
    <select name="datatype">
        %for ext in datatypes:
            %if dataset.ext == ext:
                <option value="${ext}" selected="yes">${_(ext)}</option>
            %else:
                <option value="${ext}">${_(ext)}</option>
            %endif
        %endfor
    </select>
</%def>

<div class="toolForm">
    <div class="toolFormTitle">${_('Edit Attributes')}</div>
    <div class="toolFormBody">
        <form name="edit_attributes" action="${h.url_for( controller='root', action='edit' )}" method="post">
            <input type="hidden" name="id" value="${data.id}"/>
            <div class="form-row">
                <label>
                    Name:
                </label>
                <div style="float: left; width: 250px; margin-right: 10px;">
                    <input type="text" name="name" value="${data.get_display_name()}" size="40"/>
                </div>
                <div style="clear: both"></div>
            </div>
            <div class="form-row">
                <label>
                    Info:
                </label>
                <div style="float: left; width: 250px; margin-right: 10px;">
                    <input type="text" name="info" value="${data.info}" size="40"/>
                </div>
                <div style="clear: both"></div>
            </div>
            %if trans.get_user() is not None:
			<%namespace file="../tagging_common.mako" import="render_tagging_element" />
            <div class="form-row">
                <label>
                    Tags:
                </label>
                <div style="float: left; width: 295px; margin-right: 10px; border-style: inset; border-width: 1px">
                    <style>
                        .tag-area {
                            border: none;
                        }
                    </style>
                      ${render_tagging_element(data, "edit_attributes.mako", use_toggle_link=False, in_form=True, input_size="30")}
                </div>
                <div style="clear: both"></div>
            </div>
            %endif
            %for name, spec in data.metadata.spec.items():
                %if spec.visible:
                    <div class="form-row">
                        <label>
                            ${spec.desc}:
                        </label>
                        <div style="float: left; width: 250px; margin-right: 10px;">
                            ${data.metadata.get_html_by_name( name, trans=trans )}
                        </div>
                        <div style="clear: both"></div>
                    </div>
                %endif
            %endfor
            <div class="form-row">
                <input type="submit" name="save" value="${_('Save')}"/>
            </div>
        </form>
        <form name="auto_detect" action="${h.url_for( controller='root', action='edit' )}" method="post">
            <input type="hidden" name="id" value="${data.id}"/>
            <div style="float: left; width: 250px; margin-right: 10px;">
                <input type="submit" name="detect" value="${_('Auto-detect')}"/>
            </div>
            <div class="toolParamHelp" style="clear: both;">
                This will inspect the dataset and attempt to correct the above column values if they are not accurate.
            </div>
        </form>
        %if data.missing_meta():
            <div class="errormessagesmall">${_('Required metadata values are missing. Some of these values may not be editable by the user. Selecting "Auto-detect" will attempt to fix these values.')}</div>
        %endif
    </div>
</div>
<p />
<% converters = data.get_converter_types() %>
%if len( converters ) > 0:
    <div class="toolForm">
        <div class="toolFormTitle">${_('Convert to new format')}</div>
        <div class="toolFormBody">
            <form name="convert_data" action="${h.url_for( controller='root', action='edit' )}" method="post">
                <input type="hidden" name="id" value="${data.id}"/>
                <div class="form-row">
                    <div style="float: left; width: 250px; margin-right: 10px;">
                        <select name="target_type">
                            %for key, value in converters.items():
                                <option value="${key}">${value.name}</option>
                            %endfor
                        </select>
                    </div>
                    <div class="toolParamHelp" style="clear: both;">
                        This will create a new dataset with the contents of this dataset converted to a new format. 
                    </div>
                    <div style="clear: both"></div>
                </div>
                <div class="form-row">
                    <input type="submit" name="convert_data" value="${_('Convert')}"/>
                </div>
            </form>
        </div>
    </div>
    <p />
%endif

<div class="toolForm">
    <div class="toolFormTitle">${_('Change data type')}</div>
    <div class="toolFormBody">
        %if data.datatype.allow_datatype_change:
            <form name="change_datatype" action="${h.url_for( controller='root', action='edit' )}" method="post">
                <input type="hidden" name="id" value="${data.id}"/>
                <div class="form-row">
                    <label>
                        ${_('New Type')}:
                    </label>
                    <div style="float: left; width: 250px; margin-right: 10px;">
                        ${datatype( data, datatypes )}
                    </div>
                    <div class="toolParamHelp" style="clear: both;">
                        ${_('This will change the datatype of the existing dataset but <i>not</i> modify its contents. Use this if Galaxy has incorrectly guessed the type of your dataset.')}
                    </div>
                    <div style="clear: both"></div>
                </div>
                <div class="form-row">
                    <input type="submit" name="change" value="${_('Save')}"/>
                </div>
            </form>
        %else:
            <div class="form-row">
                <div class="warningmessagesmall">${_('Changing the datatype of this dataset is not allowed.')}</div>
            </div>
        %endif
    </div>
</div>
<p />

%if trans.app.security_agent.can_manage_dataset( user_roles, data.dataset ):
    <%namespace file="/dataset/security_common.mako" import="render_permission_form" />
    ${render_permission_form( data.dataset, data.get_display_name(), h.url_for( controller='root', action='edit', id=data.id ), user_roles )}
%elif trans.user:
    <div class="toolForm">
        <div class="toolFormTitle">View Permissions</div>
        <div class="toolFormBody">
            <div class="form-row">
                %if data.dataset.actions:
                    <ul>
                        %for action, roles in trans.app.security_agent.get_dataset_permissions( data.dataset ).items():
                            %if roles:
                                <li>${action.description}</li>
                                <ul>
                                    %for role in roles:
                                        <li>${role.name}</li>
                                    %endfor
                                </ul>
                            %endif
                        %endfor
                    </ul>
                %else:
                    <p>This dataset is accessible by everyone (it is public).</p>
                %endif
            </div>
        </div>
    </div>
%endif
<p/>
<div class="toolForm">
    <div class="toolFormTitle">Copy History Item</div>
        <div class="toolFormBody">
            <form name="copy_hda" action="${h.url_for( controller='dataset', action='copy_datasets', source_dataset_ids=data.id, target_history_ids=data.history_id )}" method="post">
                <div class="form-row">
                    <input type="submit" name="change" value="Copy history item"/>
                </div>
                <div class="toolParamHelp" style="clear: both;">
                    Make a copy of this history item in your current history or any of your active histories.
                </div>
            </form>
        </div>
    </div>
</div>
