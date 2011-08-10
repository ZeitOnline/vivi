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

        for (var n in def) {
            var item = def[n];
            if (item instanceof Function) item.$ = superClass;
            proto[n] = item;
        }

        classDef.prototype = proto;

        //Give this new class the same static extend method
        classDef.extend = this.extend;
        return classDef;
    };

})();


Class = gocept.Class;

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
        connect(window, 'onunload', function(event) {
            othis.rememberScrollState();
        });
        connect(this.content_element, 'initialload', function(event) {
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
  cookie = name + "=" + val +
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
    if (begin != 0) return null;
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
    console.trace();
    console.error(real_error.name + ': ' + real_error.message);
    return err;
};


zeit.cms._imported = {};
zeit.cms.import = function(src) {
    var d = new MochiKit.Async.Deferred();
    var ident = null;
    logDebug('Importing', src);
    if (MochiKit.Base.isUndefined(zeit.cms._imported[src])) {
        var head = document.getElementsByTagName('head')[0];
        if (!isNull(src.match(/\.js$/))) {
            var node = MochiKit.DOM.createDOM('SCRIPT', {
                type: 'text/javascript',
                src: src
            });
            ident = MochiKit.Signal.connect(node, 'onload', function() {
                MochiKit.Signal.disconnect(ident);
                d.callback();
            });
        } else if (!isNull(src.match(/\.css$/))) {
            var node = MochiKit.DOM.createDOM('LINK', {
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
