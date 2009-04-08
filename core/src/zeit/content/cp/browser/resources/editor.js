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
    },

    reload: function() {
        MochiKit.Signal.signal(self, 'reload');
    },

    handleContentClick: function(event) {
        var self = this;
        log("Target " + event.target().nodeName);
        var module_name = event.target().getAttribute('cms:cp-module')
        if (module_name) {
            log("Loading module " + module_name);
            event.stop();
            var module = zeit.content.cp.modules[module_name]
            new module(event.target());
        } else  {
            event.preventDefault();
        }
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


zeit.content.cp.BlockHover = gocept.Class.extend({

    construct: function() {
        var self = this;
        MochiKit.Signal.connect('cp-content', 'onmouseover', self, 'over');
        MochiKit.Signal.connect('cp-content', 'onmouseout', self, 'out');
    },

    over: function(event) {
        var self = this;
        var block = self.get_block(event.target());
        if (!isNull(block)) {
            MochiKit.DOM.addElementClass(block, 'hover');
        }
    },

    out: function(event) {
        var self = this;
        var block = self.get_block(event.target());
        if (!isNull(block)) {
            MochiKit.DOM.removeElementClass(block, 'hover');
        }
    },

    get_block: function(element) {
        var class = 'block';
        if (MochiKit.DOM.hasElementClass(element, class)) {
            return element
        }
        return MochiKit.DOM.getFirstParentByTagAndClassName(
            element, null, class);
    },
});

zeit.content.cp.ContentActionBase = gocept.Class.extend({

    construct: function() {
        var self = this;
        self.editor = document.cpeditor;
        MochiKit.Signal.connect(
            document.cpeditor, 'before-reload', self, 'disconnect');
        MochiKit.Signal.connect(
            document.cpeditor, 'after-reload', self, 'connect');
        self.dnd_objects = []
    },

    disconnect: function() {
        var self = this;
        while(self.dnd_objects.length) {
          self.dnd_objects.pop().destroy();
        }
    },

});


zeit.content.cp.ContentDropper = zeit.content.cp.ContentActionBase.extend({
    // Handle dropping of content objects.

    connect: function() {
        var self = this;
        var elements = MochiKit.Selector.findChildElements(
            self.editor.content,
            ['div.action-content-droppable']);
        forEach(elements, function(element) {
            var block = MochiKit.DOM.getFirstParentByTagAndClassName(
                element, null, 'block-inner'); 
            var url = element.getAttribute('cms:drop-url');
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Droppable(block, {
                    hoverclass: 'hover-content',
                    ondrop: function(draggable, droppable, event) {
                        self.drop(draggable, droppable, event, url);
                    },
                }));
        });
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


zeit.content.cp.TeaserBarSorter = zeit.content.cp.ContentActionBase.extend({
    // Sort the teaser bars.

    connect: function() {
        var self = this;
        var handles = MochiKit.Selector.findChildElements(
            self.editor.content,
            ['div.block.type-teaser-bar > * > div.edit > div.dragger']);
        var mosaic = $('cp-teasermosaic');
        forEach(handles, function(handle) {
            var bar = MochiKit.DOM.getFirstParentByTagAndClassName(
                handle, 'div', 'block');
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Draggable(bar, {
                    constraint: 'vertical',
                    handle: handle,
                    ghosting: false,
                    revert: true,
                    scroll: $('cp-content'),
                    selectclass: 'hover',
                    zindex: 10000,
            }));
            self.dnd_objects.push(
                new MochiKit.DragAndDrop.Droppable(bar, {
                    containment: [mosaic],
                    onhover: MochiKit.Sortable.onHover,
                    overlap: 'vertical',
           }));
        });
        MochiKit.Sortable.sortables[mosaic.id] = {
            onChange: MochiKit.Base.noop,
            onUpdate: MochiKit.Base.noop,
        }
        
    },

});

MochiKit.Signal.connect(window, 'onload', function() {
    if (isNull($('cp-content'))) {
        return
    }
    document.cpeditor = new zeit.content.cp.Editor();
    new zeit.content.cp.BlockHover();
    new zeit.content.cp.ContentDropper();
    new zeit.content.cp.TeaserBarSorter();
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
        self.block = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, 'div', 'block-inner')
        MochiKit.DOM.addElementClass(self.block, 'highlight');

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
        MochiKit.DOM.removeElementClass(self.block, 'highlight');
    },
})
