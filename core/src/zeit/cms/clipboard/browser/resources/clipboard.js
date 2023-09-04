// $Id$

zeit.cms.Clipboard = Class.extend({

    construct: function(base_url, tree_url, clipboard_id) {
        this.base_url = base_url;
        this.contentElement = getElement(clipboard_id);
        this.tree = new Tree(tree_url, clipboard_id);
        this.dragging = false;

        connect(
            this.tree, 'zeit.cms.BeforeTreeChangeEvent',
            this, 'handleBeforeTreeChange');
        connect(
            this.tree, 'zeit.cms.TreeChangedEvent',
            this, 'handleTreeChanged');

        MochiKit.Position.includeScrollOffsets = true;

        // Removing
        connect(clipboard_id, 'onclick', this, 'removeClip');
    },

    enableAdding: function() {
        // Adding
        connect('clip-add-folder-link', 'onclick', this, 'showAddBox');
        connect('clip-add-folder-submit', 'onclick', this, 'addClip');
        connect('clip-add-folder-cancel', 'onclick', this, 'hideAddBox');
    },

    connectDNDHandlers: function() {
        var elements = this.contentElement.getElementsByTagName('li');
        var dnd = this;
        forEach(elements, function(node) {
            new MochiKit.DragAndDrop.Droppable(node, {
                hoverclass: 'TreeHover',
                ondrop: function(element, last_active_element, event) {
                            dnd.handleDrop(
                                node.getAttribute('uniqueid'), element);
                    },
            });
            if (node.getAttribute('uniqueid')) {
                zeit.cms.createDraggableContentObject(node);
            }
        });

        // Disable click event while dragging.
        MochiKit.Signal.connect(
            this.contentElement, 'onclick', function(event) {
                if (event.target().nodeName == 'A' && dnd.dragging == true) {
                    event.stop();
                }
        });
    },

    handleDrop: function(dropped_on, element) {
        this.dragging = true;
        var url;
        var dnd = this;
        var options = {}

        var source_element = element.source_element;
        if (isUndefinedOrNull(source_element)) {
            return;
        }

        var panel = null;
        panel = MochiKit.DOM.getFirstParentByTagAndClassName(
            source_element, 'div', 'panel');
        if (!isNull(panel) && panel.id == 'ClipboardPanel') {
            url = '/@@moveContent';
            options['object_path'] = source_element.getAttribute('uniqueid');
        } else {
            url = '/@@addContent';
            options['unique_id'] = element.uniqueId;
        }

        if (isEmpty(MochiKit.Base.items(options))) {
            return
        }
        options['add_to'] = dropped_on;
        log(repr(MochiKit.Base.items(options)));

        element.drag_successful = true;
        var d = doSimpleXMLHttpRequest(this.base_url + url, options);
        d.addCallbacks(
            function(result) {
                dnd.dragging = false;
                dnd.tree.replaceTree(result.responseText);
            },
            function(error) {
                alert("Could not finish drop: " + repr(MochiKit.Base.items(error.req)))
                return error
            });

    },

    handleBeforeTreeChange: function(event) {
        signal('sidebar', 'zeit.cms.RememberScrollStateEvent');
    },

    handleTreeChanged: function(event) {
        this.connectDNDHandlers();
        signal('sidebar', 'zeit.cms.RestoreScrollState');
        signal('sidebar', 'panel-content-changed');
    },

    // Adding

    showAddBox: function(event) {
        hideElement('clip-add-folder-link');
        showElement('clip-add-folder-box');
        signal('sidebar', 'panel-content-changed');
    },

    hideAddBox: function(event) {
        hideElement('clip-add-folder-box');
        showElement('clip-add-folder-link');
        signal('sidebar', 'panel-content-changed');
    },

    addClip: function(event) {
        var dnd = this;
        var title = getElement('clip-add-folder-title').value;
        if (!title.match(/\w.+/))
            return

        signal('sidebar', 'zeit.cms.RememberScrollStateEvent');
        var d = doSimpleXMLHttpRequest(
            this.base_url + '/@@addContainer', {
                'title': title});
        d.addCallbacks(
            function(result) {
                dnd.tree.replaceTree(result.responseText);
                dnd.hideAddBox();
                signal('sidebar', 'zeit.cms.RestoreScrollState');
            },
            alert
        );
        event.stop();
    },

    removeClip: function(event) {
        var element = event.target();
        var dnd = this;
        if (element == undefined) return;
        try {
            var anchor = getFirstParentByTagAndClassName(element, 'a');
        } catch(e) {
            return
        }

        if (hasElementClass(anchor, 'deleteLink')) {
            event.stop();
            signal('sidebar', 'zeit.cms.RememberScrollStateEvent');
            var url = anchor.getAttribute('href')
            var d = doSimpleXMLHttpRequest(url);
            d.addCallbacks(
                function(result) {
                    dnd.tree.replaceTree(result.responseText);
                    signal('sidebar', 'zeit.cms.RestoreScrollState');
                });
        }
    },
});


zeit.cms.CopyFromClipboard = Class.extend({

    construct: function(clipboard, copy_url, form) {
        this.clipboard = clipboard;
        this.copy_url = copy_url;

        connect(this.clipboard.contentElement, 'onclick',
                this, 'handleClick');
    },

    handleClick: function(event) {
        var othis = this;
        if (event.target().nodeName == 'A') {
            event.stop();
            var url = event.target().href;
            var d = this.getUniqueId(url);
            d.addCallbacks(
                function(result) {
                    var unique_id = result.responseText;
                    othis.copy(unique_id);
                },
                function(error) {
                    log(error);
                });
        }
    },

    getUniqueId: function(base_url) {
        var url = base_url + '/@@ajax.get_unique_id';
        var d = doSimpleXMLHttpRequest(url);
        return d
    },

    copy: function(unique_id) {
        var query = 'unique_id=' + encodeURIComponent(unique_id);
        var url = this.copy_url + '?' + query
        signal(window, 'zeit.cms.LightboxReload');
        window.location = url;
    },
});
