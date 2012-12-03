(function() {
    var declare_namespace = function(namespace) {
        var obj = window;
        forEach(namespace.split('.'), function(name) {
            if (isUndefined(obj[name])) {
                obj[name] = {};
            }
            obj = obj[name];
        });
    };
    declare_namespace('zeit.cms');
    declare_namespace('gocept');
    zeit.cms.declare_namespace = declare_namespace;

    gocept.Class = function() {};
    gocept.Class.prototype.construct = function() {};
    gocept.Class.extend = function(def) {
        var classDef = function() {
            if (arguments[0] !== gocept.Class) {
                this.construct.apply(this, arguments); }
            };

        var proto = new this(gocept.Class);
        var superClass = this.prototype;

        var n;
        for (n in def) {
            var item = def[n];
            if (item instanceof Function) {
                item.$ = superClass;
            }
            proto[n] = item;
        }

        classDef.prototype = proto;

        //Give this new class the same static extend method
        classDef.extend = this.extend;
        return classDef;
    };

}());


window.Class = gocept.Class;

zeit.cms.resolveDottedName = function(name) {
    // Resolve *absolute* dotted name
    var obj = window;
    forEach(name.split('.'), function(step) {
        obj = obj[step];
    });
    return obj;
};


zeit.cms.ScrollStateRestorer = gocept.Class.extend({

    construct: function(content_element) {
        this.content_element = $(content_element);
    },

    connectWindowHandlers: function() {
        var othis = this;
        this.restoreScrollState();
        MochiKit.Signal.connect(window, 'onunload', function(event) {
            othis.rememberScrollState();
        });
        MochiKit.Signal.connect(
            this.content_element, 'initialload', function(event) {
            if (event.src() == othis.content_element) {
                othis.restoreScrollState();
            }
        });
    },

    rememberScrollState: function() {
        var position = this.content_element.scrollTop;
        var id = this.content_element.id;
        if (!id) {
            return;
        }
        zeit.cms.setCookie(id, position.toString(), null, '/');
     },

    restoreScrollState: function() {
        var id = this.content_element.id;
        if (!id) {
            return;
        }
        var position = zeit.cms.getCookie(id);
        this.content_element.scrollTop = position;
    }

});


zeit.cms.setCookie = function(name, value, expires, path, domain, secure) {
  var val = escape(value);
  var cookie = name + "=" + val +
    ((expires) ? "; expires=" + expires.toGMTString() : "") +
    ((path) ? "; path=" + path : "") +
    ((domain) ? "; domain=" + domain : "") +
    ((secure) ? "; secure" : "");
  document.cookie = cookie;
};

zeit.cms.getCookie = function(name) {
  var dc = document.cookie;
  var prefix = name + "=";
  var begin = dc.indexOf("; " + prefix);
  if (begin == -1) {
    begin = dc.indexOf(prefix);
    if (begin != 0) {
        return null;
    }
  } else {
    begin += 2;
  }
  var end = document.cookie.indexOf(";", begin);
  if (end == -1) {
    end = dc.length;
  }
  return unescape(dc.substring(begin + prefix.length, end));
};



zeit.cms.ClickOnceAction = gocept.Class.extend({

    construct: function(element) {
        var self = this;
        self.element = $(element);

        self.event_id = MochiKit.Signal.connect(
            self.element, 'onclick', self, 'disable');
    },

    disable: function() {
        var self = this;
        MochiKit.Signal.disconnect(self.event_id);
        MochiKit.Signal.connect(self.element, 'onclick', self, 'stop');
    },

    stop: function(event) {
        event.stop();
    }
});


zeit.cms.log_error = function(err) {
    /* the error can be either a normal error or wrapped
       by MochiKit in a GenericError in which case the message
       is the real error. We check whether the message is the real
       error first by checking whether its information is undefined.
       If it is undefined, we fall back on the outer error and display
       information about that */
    var real_error = err.message;
    if (isUndefinedOrNull(real_error.message)) {
        real_error = err;
    }
    console.exception(real_error);
    console.error(real_error.stack);
    return err;
};


zeit.cms._imported = {};
zeit.cms.import = function(src) {
    var d = new MochiKit.Async.Deferred();
    var ident = null;
    var node;
    logDebug('Importing', src);
    if (MochiKit.Base.isUndefined(zeit.cms._imported[src])) {
        var head = document.getElementsByTagName('head')[0];
        if (!isNull(src.match(/\.js$/))) {
            node = MochiKit.DOM.createDOM('SCRIPT', {
                type: 'text/javascript',
                src: src
            });
            ident = MochiKit.Signal.connect(node, 'onload', function() {
                MochiKit.Signal.disconnect(ident);
                d.callback();
            });
        } else if (!isNull(src.match(/\.css$/))) {
            node = MochiKit.DOM.createDOM('LINK', {
                href: src,
                rel: 'stylesheet',
                type: 'text/css'
            });
        } else {
            throw Error("Don't know how to load: " + src);
        }
        head.appendChild(node);
        zeit.cms._imported[src] = true;
    }
    if (ident === null) {
        d.callback();
    }
    return d;
};

(function($) {
zeit.cms.evaluate_js_and_css = function(element, eval_function) {
    // XXX this is needed to support SubPageForm evaluating script tags
    // in the context of themselves. Unfortunately, `eval` does not behave
    // like normal JS functions, i.e. you can't change `this` via
    // eval.call(other_context), thus we need to use a closure for that
    // purpose. *sigh*
    if (isUndefined(eval_function)) {
        eval_function = $.globalEval;
    }

    var loading = [];
    $('script', element).each(function(i, script) {
        script = $(script);
        var src = script.attr('src');
        if (src) {
            loading.push(zeit.cms.import(src));
            script.remove();
        } else {
            if (script.attr('cms:evaluated') !== 'true') {
                eval_function(script.text());
                script.attr('cms:evaluated', 'true');
            }
        }
    });

    $('link', element).each(function(i, link) {
        link = $(link);
        if (link.attr('rel') === 'stylesheet') {
            loading.push(zeit.cms.import(link.attr('href')));
            link.remove();
        }
    });

    $('style', element).each(function(i, style) {
        $('head').append(style);
    });

    return new MochiKit.Async.DeferredList(loading);
};
}(jQuery));


zeit.cms.get_application_url = function() {
    var current = window;
    var application_url = current.application_url;
    while (current !== window.top && isUndefined(application_url)) {
        current = current.parent;
        application_url = current.application_url;
    }
    return application_url;

};


zeit.cms.get_datetime_close = function(id) {
    var closer = function(cal) {
        cal.hide();
        $(id).focus();
        MochiKit.Signal.signal(id, 'onchange', {target: $(id)});
    };
    return closer;
};


zeit.cms.in_array = function(needle, haystack) {
    return MochiKit.Base.findValue(haystack, needle) != -1;
};

MochiKit.Signal.connect(window, 'script-loading-finished', function() {
(function($) {
  $('form input.checkboxType[disabled="disabled"]').parent().addClass('checkboxdisabled');
  $('form input:checked.checkboxType[disabled="disabled"]').parent().addClass('checkboxchecked');
}(jQuery));
});
