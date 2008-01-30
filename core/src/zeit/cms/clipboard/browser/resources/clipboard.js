function Clipboard(base_url, tree_url, clipboard_id) {
    this.base_url = base_url;
    this.contentElement = getElement(clipboard_id);
    this.tree = new Tree(tree_url, clipboard_id);
    connect(this.tree, 'treeChangeEvent', this, 'handleTreeChange');
    this.connectDNDHandlers();
    var dnd = this;
    this.dragging = false;
    MochiKit.Position.includeScrollOffsets = true;

    // Adding
    connect('clip-add-folder-link', 'onclick', this, 'showAddBox');
    connect('clip-add-folder-submit', 'onclick', this, 'addClip');
    connect('clip-add-folder-cancel', 'onclick', this, 'hideAddBox');
    connect('clipboardcontents', 'onclick', this, 'removeClip');
}

Clipboard.prototype = {

    connectDNDHandlers: function() {
        var elements = this.contentElement.getElementsByTagName('li');
        var dnd = this;
        forEach(elements, function(node) {
            new Droppable(node, {
                hoverclass: 'TreeHover',
                ondrop: function(element, last_active_element, event) {
                        dnd.handleDrop(node.getAttribute('uniqueid'), element);
                    },
            });
            if (node.getAttribute('uniqueid')) {
                new Draggable(node, {
                    starteffect: null,
                    endeffect: null});
            }
        });

        forEach(this.contentElement.getElementsByTagName('a'), function(node) {
                connect(node, 'onclick', function(event) {
                    if (dnd.dragging == true) {
                        event.stop();
                    }
                });
            });
    },

    handleDrop: function(dropped_on, element) {
        this.dragging = true;
        var url;
        var unique_id;
        var dnd = this;
        var options = {'add_to': dropped_on};

        var dragged_element = element.dragged_element;
        if (dragged_element == undefined) return;

        if (dragged_element.nodeName == 'LI') {
            url = '/@@moveContent';
            options['object_path'] = dragged_element.getAttribute('uniqueid');
        } else {
            url = '/@@addContent';
            options['unique_id'] = element.uniqueId;
        }

            if (!options) return;

            var d = doSimpleXMLHttpRequest(this.base_url + url, options);
            d.addCallbacks(
                function(result) {
                    dnd.dragging = false;
                    dnd.tree.replaceTree(result.responseText);
            },
            alert
        );
    },

    handleTreeChange: function(event) {
        this.connectDNDHandlers();
    },

    // Adding

    showAddBox: function(event) {
        hideElement('clip-add-folder-link');
        showElement('clip-add-folder-box');
    },

    hideAddBox: function(event) {
        hideElement('clip-add-folder-box');
        showElement('clip-add-folder-link');
    },

    addClip: function(event) {
        var dnd = this;
        var title = getElement('clip-add-folder-title').value;
        if (!title.match(/\w.+/))
            return

        var d = doSimpleXMLHttpRequest(
            this.base_url + '/@@addContainer', {
                'title': title});
        d.addCallbacks( 
            function(result) {
                dnd.tree.replaceTree(result.responseText);
                clipboarddnd.hideAddBox();
            },
            alert
        );
        event.stop();
    },

    removeClip: function(event) {
        var element = event.target();
        if (element == undefined) return;

        var css_class = element.getAttribute('class');
        if (css_class == 'DeleteLink') {
            var url = element.getAttribute('href')
            var d = doSimpleXMLHttpRequest(url);
            d.addCallbacks(
                function(result) {
                    clipboarddnd.tree.replaceTree(result.responseText);
                });
        }

        if (element.nodeName == 'A' && !(css_class == 'DeleteLink')) return;

        event.stop();
    },
}


