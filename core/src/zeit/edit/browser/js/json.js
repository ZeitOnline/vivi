zeit.cms.declare_namespace('zeit.edit');


zeit.edit.makeJSONRequest = function(
    url, json, target_component, options) {
    return zeit.edit.with_lock(
        zeit.edit._locked_makeJSONRequest,
        url, json, target_component, options);
};


zeit.edit._locked_makeJSONRequest = function(
    url, json, target_component, options) {

    if (isUndefinedOrNull(target_component)) {
        target_component = zeit.edit.editor;
    }
    zeit.edit.editor.busy_until_reload_of(target_component);
    options = MochiKit.Base.setdefault(options, {
        method: 'GET'
    });

    var q_index = url.indexOf('?');
    if (q_index >= 0) {
        json = MochiKit.Base.setdefault(
            json,
            MochiKit.Base.parseQueryString(url.slice(q_index + 1)));
        url = url.slice(0, q_index);
    }

    if (!isUndefinedOrNull(json)) {
        options.method = 'POST';
        json = MochiKit.Base.serializeJSON(json);
    }
    var d = MochiKit.Async.doXHR(url, {
        method: options.method,
        sendContent: json});
    d.addCallbacks(function(result) {
        var result_obj = null;
        try {
            result_obj = MochiKit.Async.evalJSONRequest(result);
        } catch (e) {
            if (! e instanceof SyntaxError) {
                throw e;
            }
        }
        var immediate_actions = [];
        if (!isNull(result_obj)) {
            var signals = result_obj['signals'] || [];
            forEach(signals, function(signal) {
                if (isNull(signal.when)) {
                    immediate_actions.push(signal);
                } else {
                    log("Connecting "+ [target_component.__name__, signal.when, signal.name]);
                    (function() {
                        var ident = MochiKit.Signal.connect(
                            target_component, signal.when, function() {
                            log("Signalling "+ [target_component.__name__, signal.when, signal.name]);
                            MochiKit.Signal.disconnect(ident);
                            MochiKit.Signal.signal.apply(
                                this,
                                extend(
                                    [target_component, signal.name],
                                    signal.args));
                        });
                    }());
                }
            });
        }
        if (immediate_actions.length) {
            immediate_actions.reverse();
            while(immediate_actions.length) {
                var signal = immediate_actions.pop();
                MochiKit.Signal.signal.apply(
                    this,
                    extend([target_component, signal.name], signal.args));
            }
        } else {
            MochiKit.Signal.signal(target_component, 'reload');
        }
        return result;
    },
    function(error) {
        zeit.edit.handle_json_errors(error);
        MochiKit.Signal.signal(target_component, 'reload');
        return error;
    });
    return d;
};


zeit.edit.handle_json_errors = function(error) {
    zeit.cms.log_error(error);
    if (!isUndefinedOrNull(error.req)) {
        var div = DIV();
        div.innerHTML = error.req.responseText;
        var message_node = MochiKit.DOM.getFirstElementByTagAndClassName(
            'pre', null, div);
        var message;
        if (isNull(message_node)) {
            message = error.req.responseText;
        } else {
            message = message_node.textContent;
        }
        alert(message);
    }
    return error;
};
