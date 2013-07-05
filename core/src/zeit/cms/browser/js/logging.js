(function() {

    zeit.cms.declare_namespace('zeit.cms.logging');

    zeit.cms.logging.CONSOLE_LEVEL = 'DEBUG';
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
            alert(
              'Logging failed because of ' + e +
              '\n\nOriginal error which was NOT logged:\n' +
                msg.info);
        });
    };

    var FIREBUG_LOG_LEVELS = {
        'DEBUG': 'debug',
        'INFO': 'info',
        'ERROR': 'error',
        'FATAL': 'error',
        'WARNING': 'warn'};

    /* Console logger for debug purpose */
    var console_listener = function(msg) {
        console[FIREBUG_LOG_LEVELS[msg.level]](
            msg.timestamp.toJSON() + ": "  + msg.info);
    };

    MochiKit.Logging.logger.addListener(
        'xhr-listener', zeit.cms.logging.XHR_LEVEL, xhr_listener);
    MochiKit.Logging.logger.addListener(
        'console-listener', zeit.cms.logging.CONSOLE_LEVEL, console_listener);

    window.onerror = function(err, url, line) {
      logError(url + " line " + line + ": " + err);
    };

}(jQuery));
