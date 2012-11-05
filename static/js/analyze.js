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

function plot_lines(nodeid, data) {
  $.plot($(nodeid), [data],
         {
           xaxis: {
             mode: "time",
             tickLength: 5
           },
           legend: {
             show: false
           }
         }
        );
};

function flot_series(orig) {
  var ret = [];
  $.each(orig, function(key, val)
         {
           ret.push({'label': key, 'data': val});
         }
        );
  return ret;
};

function flot_array(orig) {
  var ret = [];
  $.each(orig, function(key, val)
         {
           ret.push([key, val]);
         }
        );
  return ret;
};

$(document).ready(
  function()
  {
    plot_lines("#series", flot_array(stats.event_series));

    plot_pie("#weekdays", flot_series(stats.event_days));

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
