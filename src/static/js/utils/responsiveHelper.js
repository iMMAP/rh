/*
 * Responsive Layout helper
 */
window.ResponsiveHelper = (($) => {
  // init variables
  const handlers = [];
  let prevWinWidth;
  const win = $(window);
  let nativeMatchMedia = false;

  // detect match media support
  if (window.matchMedia) {
    if (window.Window && window.matchMedia === Window.prototype.matchMedia) {
      nativeMatchMedia = true;
    } else if (window.matchMedia.toString().indexOf('native') > -1) {
      nativeMatchMedia = true;
    }
  }

  // prepare resize handler
  function resizeHandler() {
    const winWidth = win.width();
    if (winWidth !== prevWinWidth) {
      prevWinWidth = winWidth;

      // loop through range groups
      $.each(handlers, (index, rangeObject) => {
        // disable current active area if needed
        $.each(rangeObject.data, (property, item) => {
          if (item.currentActive && !matchRange(item.range[0], item.range[1])) {
            item.currentActive = false;
            if (typeof item.disableCallback === 'function') {
              item.disableCallback();
            }
          }
        });

        // enable areas that match current width
        $.each(rangeObject.data, (property, item) => {
          if (!item.currentActive && matchRange(item.range[0], item.range[1])) {
            // make callback
            item.currentActive = true;
            if (typeof item.enableCallback === 'function') {
              item.enableCallback();
            }
          }
        });
      });
    }
  }
  win.bind('load resize orientationchange', resizeHandler);

  // test range
  function matchRange(r1, r2) {
    let mediaQueryString = '';
    if (r1 > 0) {
      mediaQueryString += `(min-width: ${r1}px)`;
    }
    if (r2 < Number.POSITIVE_INFINITY) {
      mediaQueryString += `${mediaQueryString ? ' and ' : ''}(max-width: ${r2}px)`;
    }
    return matchQuery(mediaQueryString, r1, r2);
  }

  // media query function
  function matchQuery(query, r1, r2) {
    if (window.matchMedia && nativeMatchMedia) {
      return matchMedia(query).matches;
    }if (window.styleMedia) {
      return styleMedia.matchMedium(query);
    }if (window.media) {
      return media.matchMedium(query);
    }
      return prevWinWidth >= r1 && prevWinWidth <= r2;
  }

  // range parser
  function parseRange(rangeStr) {
    const rangeData = rangeStr.split('..');
    const x1 = Number.parseInt(rangeData[0], 10) || Number.NEGATIVE_INFINITY;
    const x2 = Number.parseInt(rangeData[1], 10) || Number.POSITIVE_INFINITY;
    return [x1, x2].sort((a, b) => a - b);
  }

  // export public functions
  return {
    addRange: (ranges) => {
      // parse data and add items to collection
      const result = {data: {}};
      $.each(ranges, (property, data) => {
        result.data[property] = {
          range: parseRange(property),
          enableCallback: data.on,
          disableCallback: data.off,
        };
      });
      handlers.push(result);

      // call resizeHandler to recalculate all events
      prevWinWidth = null;
      resizeHandler();
    },
  };
})(jQuery);
