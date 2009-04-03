if (isUndefinedOrNull(zeit.content)) {
    zeit.content = {}
}
zeit.content.cp = {}

zeit.content.cp.Editor = Class.extend({
    
    construct: function() {
        var self = this;
        self.content = $('cp-content');
        MochiKit.Signal.connect(
            'content', 'onclick',
            self, 'handleContentClick');
        MochiKit.Signal.connect(
            self, 'reload', self, 'reload');
        MochiKit.Signal.signal(self, 'reload');
        //self.connect_draggables();
    },

    handleContentClick: function(event) {
        var self = this;
        var module_name = event.target().getAttribute('cms:cp-module')
        log("Loading module " + module_name);
        if (!module_name) {
            return
        }
        event.stop();
        var module = zeit.content.cp.modules[module_name]
        new module(event.target());
    },
    
    connect_draggables: function() {
        var self = this;
        MochiKit.Sortable.create($('cp-content'), {
            constraint: null,
            only: ['box'],
            tag: 'div',
            tree: true,
        });
        MochiKig.Signal.connect(self, 'before-reload', function() {
            MochiKit.Sortable.destroy($('cp-content'));
        });
        /*var boxes = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'box', $('cp-content'));
        forEach(boxes, function(box) {
            new MochiKit.DragAndDrop.Draggable(box);
        });
        */
    },

    reload: function() {
        var self = this;
        MochiKit.Signal.signal(self, 'before-reload');
        var url = context_url + '/contents';
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            self.content.innerHTML = result.responseText;
            MochiKit.Signal.signal(self, 'after-reload');
        });
    },
});


zeit.content.cp.BoxHover = Class.extend({

    construct: function() {
        var self = this;
        // doesn't look good, yet
        return
        MochiKit.Signal.connect('cp-content', 'onmouseover', self, 'over');
        MochiKit.Signal.connect('cp-content', 'onmouseout', self, 'out');
    },

    over: function(event) {
        MochiKit.DOM.addElementClass(event.target(), 'hover');
    },

    out: function(event) {
        MochiKit.DOM.removeElementClass(event.target(), 'hover');
    },
});

MochiKit.Signal.connect(window, 'onload', function() {
    if (isNull($('cp-content'))) {
        return
    }
    document.cpeditor = new zeit.content.cp.Editor();
    new zeit.content.cp.BoxHover();
});


/* modules */
zeit.content.cp.modules = {}

zeit.content.cp.modules.LightBoxForm = zeit.cms.LightboxForm.extend({

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        arguments.callee.$.construct.call(self, url, $('content'));
        self.events.push(MochiKit.Signal.connect(
           document.cpeditor, 'before-reload',
           self, 'close'));
    },

    handle_submit: function(action) {
        var self = this;
        var d = arguments.callee.$.handle_submit.call(self, action)
        d.addCallback(function(result) {
            if (isNull(result)) {
                return null;
            }
            var summary = MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'summary', self.form);
            if (isNull(summary)) {
                return result;
            }
            self.close();
            MochiKit.Signal.signal(document.cpeditor, 'reload');
        });
    },
});


zeit.content.cp.modules.LoadAndReload = Class.extend({

    construct: function(context_element) {
        var url = context_element.getAttribute('href');
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            MochiKit.Signal.signal(document.cpeditor, 'reload');
        });
    },

});


zeit.content.cp.modules.ConfirmDelete = Class.extend({

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        // XXX i18n
        var confirm = DIV(
            {'class': 'confirm-delete'},
            A({'href': url,
               'cms:module': 'LoadAndReload'},
               'Remove'));
        context_element.appendChild(confirm);
        var position = MochiKit.Style.getElementPosition(confirm);
        //position.x -= 30;
        MochiKit.Style.setElementPosition(confirm, position);
        
    },
})
