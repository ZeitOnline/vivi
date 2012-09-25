/**
 * A Context associates lifecycle events with a listener.
 *
 * Listeners need to implement methods ``connect`` and ``disconnect``, and can
 * then instantiate a Context, passing themselves to it.
 * The Context then calls listener.connect/disconnect at the appropriate times.
 *
 * XXX The naming of activate/deactivate which call connect/disconnect is
 * confusing.
 *
 * XXX This reminds me of listeners in Java AWT, whose API is much cleaner:
 * my_window.addListener(foo) means, my_window will call methods like
 * onMaximize, onClose on foo at appropriate times.
 * I realize that determining the source object is half the purpose here (e.g.
 * in the lightbox context case), but I feel this whole business here has too
 * much, overly complicated mechanics.
 */

zeit.cms.declare_namespace('zeit.edit.context');


/**
 * The Context's API consist of
 *
 * - init(): register additional event handlers
 * - activate(): call listener.connect
 * - deactivate(): call listener.deconnect
 * - destroy(): tear down our event handlers
 */
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

    init: function() {
        // may be defined in subclass
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
    // Context for a listener running *in* a lightbox.
    // The listener needs to declare "parent".

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


/**
 * Helper class that instantiates a context automatically, from the
 * class name given in self.context.
 */
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

    connect: function() {
        // define in subclass
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
