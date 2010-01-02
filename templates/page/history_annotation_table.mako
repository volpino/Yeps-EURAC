<%namespace file="../tagging_common.mako" import="render_tagging_element_html" />
<%namespace file="../root/history_common.mako" import="render_dataset" />

<table>
    ## Table header.
    <tr>
        <th colspan='2'>History '${history.get_display_name()}'</th>
    </tr>
    <tr>
        ## Status messages and tags.
        <td colspan='2'>
            %if history.deleted:
                <div class="warningmessagesmall">
                    ${_('This is a deleted history.')}
                </div>
            %endif
            %if trans.get_user() is not None:
                Tags: ${render_tagging_element_html( tags=history.tags, editable=False, use_toggle_link=False )}
            %endif
        </td>
    </tr>
    <tr>
        <td colspan="2" class="annotation">Description of History: 
            <ol>
                <li>What was the motivation for this history?
                <li>What is the outcome of this history?
                <li>What are unresolved questions from this history?
                <li>What new questions arise from this history?
            </ol>
        </td>
    </tr>
    
    ## Table body. For each dataset, there is an area to annotate the dataset.
    %if not datasets:
        <tr>
            <td>
                <div class="infomessagesmall" id="emptyHistoryMessage">
                    ${_("Your history is empty. Click 'Get Data' on the left pane to start")}
                </div>
            </td>
        </tr>
    %else:
        ## Render requested datasets.
        %for data in datasets:
            %if data.visible:
            <tr>
                <td valign="top"><span class="annotation">Describe this step: why was it done? what data did it produce?</span></td>
                ##<td valign="top" class="annotation">Describe this step: why was it done? what data does it produce?</td>
                <td>
                    <div class="historyItemContainer" id="historyItemContainer-${data.id}">
                        ${render_dataset( data, data.hid, show_deleted_on_refresh = show_deleted, user_owns_dataset = False )}
                    </div>
                </td>
            </tr>
            %endif
        %endfor
    %endif
</table>
        