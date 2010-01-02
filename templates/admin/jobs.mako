<%inherit file="/base.mako"/>
<%namespace file="/message.mako" import="render_msg" />

<%def name="title()">Jobs</%def>

<h2>Jobs</h2>

%if msg:
    ${render_msg( msg, messagetype )}
%endif

<p>
    All unfinished jobs are displayed here.  To display only jobs that have not
    had their job state updated recently, set a cutoff value in the 'cutoff'
    box below.
</p>
<p>
    If any jobs are displayed, you may choose to stop them.  Your stop message
    will be displayed to the user as: "This job was stopped by an
    administrator: <b>&lt;YOUR MESSAGE&gt;</b>  For more information or help,
    report this error".
</p>

<form name="jobs" action="${h.url_for()}" method="POST">

<p/>

%if jobs:
    <table class="manage-table colored" border="0" cellspacing="0" cellpadding="0" width="100%">
        <tr class="header">
            <td>&nbsp;</td>
            <td>Job ID</td>
            <td>User</td>
            <td>Last Update</td>
            <td>Tool</td>
            <td>State</td>
            <td>Command Line</td>
            <td>Job Runner</td>
            <td>PID/Cluster ID</td>
        </tr>
        %for job in jobs:
                <td>
                    %if job.state == 'upload':
                        &nbsp;
                    %else:
                        <input type="checkbox" name="stop" value="${job.id}"/>
                    %endif
                </td>
                <td>${job.id}</td>
                %if job.history.user:
                    <td>${job.history.user.email}</td>
                %else:
                    <td>anonymous</td>
                %endif
                <td>${last_updated[job.id]} ago</td>
                <td>${job.tool_id}</td>
                <td>${job.state}</td>
                <td>${job.command_line}</td>
                <td>${job.job_runner_name}</td>
                <td>${job.job_runner_external_id}</td>
            </tr>
        %endfor
    </table>
    <p/>
    <div class="toolForm">
        <div class="toolFormTitle">
            Stop Jobs
        </div>
        <div class="toolFormBody">
            <div class="form-row">
                <label>
                    Stop message:
                </label>
                <div class="form-row-input">
                    <input type="text" name="stop_msg" size="40"/>
                </div>
                <div class="toolParamHelp" style="clear: both;">
                    to be displayed to the user
                </div>
            </div>
            <div class="form-row">
                <input type="submit" class="primary-button" name="submit" value="Submit">
            </div>
        </div>
    </div>
    <p/>
%else:
    <div class="infomessage">There are no unfinished jobs to show with current cutoff time.</div>
    <p/>
%endif
    <div class="toolForm">
        <div class="toolFormTitle">
            Update Jobs
        </div>
        <div class="toolFormBody">

            <div class="form-row">
                <label>
                    Cutoff:
                </label>
                <div class="form-row-input">
                    <input type="text" name="cutoff" size="4" value="${cutoff}"/>
                </div>
                <div class="toolParamHelp" style="clear: both;">
                    In seconds
                </div>
            </div>
            <div class="form-row">
                <input type="submit" class="primary-button" name="submit" value="Refresh">
            </div>
        </div>
    </div>

</form>
