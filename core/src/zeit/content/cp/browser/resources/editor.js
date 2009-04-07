if (isUndefinedOrNull(zeit.content)) {
    zeit.content = {}
}
zeit.content.cp = {}

zeit.content.cp.Editor = gocept.Class.extend({
    
    construct: function() {
        var self = this;
        self.content = $('cp-content');
        MochiKit.Signal.connect(
            'content', 'onclick',
            self, 'handleContentClick');
        MochiKit.Signal.connect(
            self, 'reload', self, 'reload');
        //self.connect_draggables();
    },

    reload: function() {
        MochiKit.Signal.signal(self, 'reload');
    },

    handleContentClick: function(event) {
        var self = this;
        log("Target " + event.target().nodeName);
        var module_name = event.target().getAttribute('cms:cp-module')
        log("Loading module " + module_name);
        if (module_name) {
            event.stop();
            var module = zeit.content.cp.modules[module_name]
            new module(event.target());
        } else  {
            event.preventDefault();
        }
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


zeit.content.cp.BoxHover = gocept.Class.extend({

    construct: function() {
        var self = this;
        MochiKit.Signal.connect('cp-content', 'onmouseover', self, 'over');
        MochiKit.Signal.connect('cp-content', 'onmouseout', self, 'out');
    },

    over: function(event) {
        var self = this;
        var box = self.get_box(event.target());
        if (!isNull(box)) {
            MochiKit.DOM.addElementClass(box, 'hover');
        }
    },

    out: function(event) {
        var self = this;
        var box = self.get_box(event.target());
        if (!isNull(box)) {
            MochiKit.DOM.removeElementClass(box, 'hover');
        }
    },

    get_box: function(element) {
        var class = 'box-inner';
        if (MochiKit.DOM.hasElementClass(element, class)) {
            return element
        }
        return MochiKit.DOM.getFirstParentByTagAndClassName(
            element, null, class);
    },
});

zeit.content.cp.ContentDropper = gocept.Class.extend({

    construct: function() {
        var self = this;
        self.editor = document.cpeditor;
        MochiKit.Signal.connect(
            document.cpeditor, 'before-reload', self, 'disconnect');
        MochiKit.Signal.connect(
            document.cpeditor, 'after-reload', self, 'connect');
        self.droppables = []
    },

    connect: function() {
        var self = this;
        var elements = MochiKit.Selector.findChildElements(
            self.editor.content,
            ['div.action-content-droppable'])
        forEach(elements, function(element) {
            var box = MochiKit.DOM.getFirstParentByTagAndClassName(
                element, null, 'box-inner'); 
            var url = element.getAttribute('cms:drop-url');
            self.droppables.push(
                new MochiKit.DragAndDrop.Droppable(box, {
                    hoverclass: 'hover-content',
                    ondrop: function(draggable, droppable, event) {
                        self.drop(draggable, droppable, event, url);
                    },
                }));
        });
    },

    disconnect: function() {
        var self = this;
        while(self.droppables.length) {
          self.droppables.pop().destroy();
        }
    },

    drop: function(draggable, droppable, event, url) {
        var self = this;
        var uniqueId = draggable.uniqueId;
        if (isUndefinedOrNull(uniqueId)) {
            return
        }
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            url, {'uniqueId': uniqueId});
        // XXX error handling
        d.addCallback(function(result) {
            MochiKit.Signal.signal(self.editor, 'reload');
        });
        
    },


});

MochiKit.Signal.connect(window, 'onload', function() {
    if (isNull($('cp-content'))) {
        return
    }
    document.cpeditor = new zeit.content.cp.Editor();
    new zeit.content.cp.BoxHover();
    new zeit.content.cp.ContentDropper();
    document.cpeditor.reload();
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


zeit.content.cp.modules.LoadAndReload = gocept.Class.extend({

    construct: function(context_element) {
        var url = context_element.getAttribute('href');
        var d = MochiKit.Async.doSimpleXMLHttpRequest(url);
        // XXX error handling
        d.addCallback(function(result) {
            MochiKit.Signal.signal(document.cpeditor, 'reload');
        });
    },

});


zeit.content.cp.modules.ConfirmDelete = gocept.Class.extend({

    construct: function(context_element) {
        var self = this;
        var url = context_element.getAttribute('href');
        // XXX i18n
        self.confirm = DIV(
            {'class': 'confirm-delete'},
            A({'href': url,
               'cms:cp-module': 'LoadAndReload'},
               'Remove'))
        context_element.appendChild(self.confirm);
        MochiKit.Visual.fade(self.confirm, {'from': 0, 'to': 1});
        self.box = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, 'div', 'box-inner')
        MochiKit.DOM.addElementClass(self.box, 'highlight');

        self.overlay = DIV({'id': 'confirm-delete-overlay'});
        $('body').appendChild(self.overlay);
        self.events = []
        self.events.push(
            MochiKit.Signal.connect(self.overlay, 'onclick', self, 'close'));
        self.events.push(
            MochiKit.Signal.connect(
                document.cpeditor, 'before-reload', self, 'close'))

    },

    close: function(event) {
        var self = this;
        MochiKit.Base.map(
            MochiKit.Signal.disconnect, self.events)
        self.confirm.parentNode.removeChild(self.confirm);
        self.overlay.parentNode.removeChild(self.overlay);
        MochiKit.DOM.removeElementClass(self.box, 'highlight');
    },
})
