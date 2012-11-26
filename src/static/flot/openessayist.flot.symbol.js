/*
Flot plugin that adds some extra symbols for plotting points.

The symbols are accessed as strings through the standard symbol
choice:

  series: {
      points: {
          symbol: "square" // or "diamond", "triangle", "cross"
      }
  }

*/

(function ($) {
    function processRawData(plot, series, datapoints) {
        // we normalize the area of each symbol so it is approximately the
        // same as a circle of the given radius

        var handlers = {
            stick: function (ctx, x, y, radius, shadow) {
                // pi * r^2 = (2s)^2  =>  s = r * sqrt(pi)/2
                var size = radius * Math.sqrt(Math.PI) / 2;
                ctx.moveTo(x, y - size);
                ctx.lineTo(x, y + size);
            }
        }

        var s = series.points.symbol;
        if (handlers[s])
            series.points.symbol = handlers[s];
    }
    
    function init(plot) {
        plot.hooks.processDatapoints.push(processRawData);
    }
    
    $.plot.plugins.push({
        init: init,
        name: 'extrasymbol',
        version: '1.0'
    });
})(jQuery);
