function label_formatter(label, series) {
  var rv = '<div class="pie_label">' + label + '<br/>' + series.data[0][1] + '</div>';
  return rv;
};

function plot_pie(nodeid, data) {
  $.plot($(nodeid), data,
         {
           series: { 
             pie: {
               show: true,
               radius: 1,
               label: {
                 show: true,
                 radius: 3/4,
                 formatter: label_formatter,
                 background: { 
                   opacity: 0.5,
                   color: '#000'
                 }
               }
             }
           },
           legend: {
             show: false
           }
         }
        );
};

$(document).ready(
  function()
  {
    var event_days = [];
    $.each(stats.event_days, function(key, val)
           {
             event_days.push({'label': key, 'data': val});
           }
          );
    plot_pie("#weekdays", event_days);

    var percent_events = Math.round(stats.percent_events);
    var event_time = [
      {
        'label': 'Booked',
        'data': percent_events
      },
      {
        'label': 'Not Booked',
        'data': 100 - percent_events
      }
    ];
    plot_pie("#event_time", event_time);
  }
);
