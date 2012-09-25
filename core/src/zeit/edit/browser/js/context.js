//
// Define context managers
//

zeit.cms.declare_namespace('zeit.edit.context');


zeit.edit.context.Base = gocept.Class.extend({

    __name__: 'zeit.edit.context.Base',

    construct: function(listener) {
        var self = this;
        log("Creating " + self.__name__ + " for " + listener.__name__);
        self.listener = listener;
        if (!isUndefinedOrNull(listener.__context__)) {
            throw new Error("Trying to add new context.");
        }
        listener.__context__ = self;
        self.events = [];

        self.init();

        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'single-context-start',
            self, self.deactivate));
        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'single-context-end',
            self, self.activate));
    },

    destroy: function() {
        var self = this;
        while(self.events.length) {
          MochiKit.Signal.disconnect(self.events.pop());
        }
        self.listener.__context__ = null;
        self.listener = null;
    },

    activate: function() {
        var self = this;
        log('Activating ' + self.listener.__name__);
        self.listener.connect.call(self.listener);
    },

    deactivate: function() {
        var self = this;
        log('Deactivating ' + self.listener.__name__);
        self.listener.disconnect.call(self.listener);
    }
});


zeit.edit.context.Editor = zeit.edit.context.Base.extend({

    __name__: 'zeit.edit.context.Editor',

    init: function() {
        var self = this;
        // Those handlers stay forever
        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'after-reload',
            self, self.activate));
        self.events.push(MochiKit.Signal.connect(
            zeit.edit.editor, 'before-reload',
            self, self.deactivate));
    }

});


zeit.edit.context.Lightbox = zeit.edit.context.Base.extend({
    // Context for a component running *in* a lightbox.
    // The component needs to declare "parent".

    __name__: 'zeit.edit.context.Lightbox',

    init: function() {
        var self = this;
        MochiKit.Signal.signal(zeit.edit.editor, 'single-context-start');
        self.activate();
        self.events.push(MochiKit.Signal.connect(
            self.listener.parent, 'before-close',
            self, self.deactivate));
        self.events.push(MochiKit.Signal.connect(
            self.listener.parent, 'before-reload',
            self, self.deactivate));
    },

    deactivate: function() {
        var self = this;
        arguments.callee.$.deactivate.call(self);
        self.destroy();
    }
});


zeit.edit.context.ContentActionBase = gocept.Class.extend({

    __name__: 'zeit.edit.ContentActionBase',
    context: null,  // define in sublcasses

    construct: function() {
        var self = this;
        self.editor = zeit.edit.editor;
        self.dnd_objects = [];
        self.events = [];
        if (isNull(self.context)) {
            log("No context for "+self.__name__);
        } else {
            new self.context(self);
        }
    },

    disconnect: function() {
        var self = this;
        while(self.dnd_objects.length) {
          self.dnd_objects.pop().destroy();
        }
        while(self.events.length) {
          MochiKit.Signal.disconnect(self.events.pop());
        }
    }

});
