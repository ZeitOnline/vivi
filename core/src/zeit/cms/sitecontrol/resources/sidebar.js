zeit.cms.sitecontrol = {};

zeit.cms.sitecontrol.Sidebar = gocept.Class.extend({

    construct: function(view_url) {
        var self = this;
        self.view_url = view_url;
        self.container = $('zeit.cms.sitecontrol.panelcontent');
        self.load();
    },

    load: function() {
        var self = this;
        MochiKit.DOM.addElementClass(self.container, 'busy');
        var d = MochiKit.Async.doSimpleXMLHttpRequest(self.view_url);
        d.addCallback(function(result) {
            self.replace(result.responseText);
        });
    },

    replace: function(html) {
        var self = this;
        self.container.innerHTML = html;
        MochiKit.Signal.signal('sidebar', 'panel-content-changed');
        self.select = MochiKit.DOM.getFirstElementByTagAndClassName(
            'select', null, self.container);
        var button = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', null, self.container);
        MochiKit.Signal.connect(self.select, 'onchange', self, self.goto);
        MochiKit.Signal.connect(button, 'onclick', self, self.goto);
        self.highlight();
        MochiKit.DOM.removeElementClass(self.container, 'busy');
    },

    highlight: function() {
        var self = this;
        for (var i=0; i<self.select.options.length; i++) {
            var option = self.select.options[i];
            if (!option.value) {
                continue
            }
            var index = option.value.lastIndexOf('index');
            if (index >= 0) {
                var folder_url = option.value.slice(0, index);
            } else {
                folder_url = option.value;
            }
            if (document.location.href.indexOf(folder_url) == 0) {
                self.select.selectedIndex = i;
            }
        }
    },

    goto: function() {
        var self = this;
        var url =  self.select.value;
        if (url) {
            document.location.href = url;
        }
    },
});
