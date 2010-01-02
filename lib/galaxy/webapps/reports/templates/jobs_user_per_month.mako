<%inherit file="/base_panels.mako"/>

<%def name="main_body()">
  <div class="reportBody">
    <h3 align="center">Jobs per month for user "${email}"</h3>
    <h4 align="center">Click Total Jobs to see the user's jobs for that month</h4>
    %if msg:
      <table align="center" width="70%" class="border" cellpadding="5" cellspacing="5">
        <tr><td class="ok_bgr">${msg}</td></tr>
      </table>
    %endif
    <table align="center" width="60%" class="colored">
      %if len( jobs ) == 0:
        <tr><td colspan="2">There are no jobs for user "${email}"</td></tr>
      %else:
        <tr class="header">
          <td>Month</td>
          <td>Total Jobs</td>
        </tr>
        <% ctr = 0 %>
        %for job in jobs:
          %if ctr % 2 == 1:
            <tr class="odd_row">
          %else:
            <tr class="tr">
          %endif
            <td>${job[2]}&nbsp;${job[3]}</td>
            <td><a href="${h.url_for( controller='jobs', action='user_for_month', email=email, month_label=job[2].strip(), year_label=job[3], month=job[0] )}">${job[1]}</a></td>
          </tr>
          <% ctr += 1 %>
        %endfor
      %endif
    </table>
  </div>
</%def>
