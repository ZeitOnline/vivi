(function() {

    zeit.cms.declare_namespace('zeit.cms.logging');

    // To change at runtime:
    // MochiKit.Logging.logger.listeners["console-listener"][0] = MochiKit.Logging.logLevelAtLeast('DEBUG')
    zeit.cms.logging.CONSOLE_LEVEL = 'ERROR';
    zeit.cms.logging.XHR_LEVEL = 'ERROR';

    /* Disable default logger */
    MochiKit.Logging.logger.useNativeConsole = false;

    /* XHR logger logging errors to server error log */
    var xhr_listener = function(msg) {
        var url = window.application_url + '/@@log.json';
        var data = MochiKit.Base.serializeJSON(
          {'level': msg.level,
           'timestamp': msg.timestamp.toJSON(),
           'url': window.location.href,
           'message': msg.info});
        var d = MochiKit.Async.doXHR(url, {
            method: 'POST',
            sendContent: data});
        d.addErrback(function(e) {
            MochiKit.Logging.logger.warning(
              'Logging failed because of ' + e +
              '\n\nOriginal error which was NOT logged:\n' +
                msg.info);
        });
    };

    var FIREBUG_LOG_LEVELS = {
        'DEBUG': 'debug',
        'INFO': 'info',  // MochiKit `log()` uses level INFO
        'ERROR': 'error',
        'FATAL': 'error',
        'WARNING': 'warn'};

    /* Console logger for debug purpose */
    var console_listener = function(msg) {
        console[FIREBUG_LOG_LEVELS[msg.level]](
            msg.timestamp.toJSON() + ": "  + msg.info);
    };

    if (window.application_url) {
        MochiKit.Logging.logger.addListener(
            'xhr-listener', zeit.cms.logging.XHR_LEVEL, xhr_listener);
    } else {
        MochiKit.Logging.logger.warning(
            'No application_url defined, XHR logging disabled');
    }
    MochiKit.Logging.logger.addListener(
        'console-listener', zeit.cms.logging.CONSOLE_LEVEL, console_listener);

    window.onerror = function(message, url, line, column, error) {
      if (error) {  // parameters column and error are supported on FF>=30
          var traceback =  error.stack.slice(0, -1).replace("\n", "\n  ");
          logError(message + "\nJS-Traceback (most recent call first):\n  "
                   + traceback + "\n" + message);
      } else {
          logError(message + "\nJS-Traceback:\n  " + url + ":" + line);
      }
    };

}(jQuery));
