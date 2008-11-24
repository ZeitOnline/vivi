if (typeof(zeit) == 'undefined') {
    zeit = {};
}

if (typeof(zeit.cms) == 'undefined') {
    zeit.cms = {};
}


zeit.cms.ScrollStateRestorer = Class.extend({

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

    rememberScrollState: function(content_element) {
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
    },

});


zeit.cms.setCookie = function(name, value, expires, path, domain, secure) {   
  var val = escape(value);
  cookie = name + "=" + val +
    ((expires) ? "; expires=" + expires.toGMTString() : "") +
    ((path) ? "; path=" + path : "") +
    ((domain) ? "; domain=" + domain : "") +
    ((secure) ? "; secure" : "");
  document.cookie = cookie;
}

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
}


