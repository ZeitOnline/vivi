// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt

function XMLEditor(base_url, element_id) {
    var editor = this;
    this.base_url = base_url + '/';
    this.contentElementId = element_id;
    var content_element = this.getContentElement();
    connect(content_element, 'onclick', this, 'showActions');
    connect(content_element, 'onclick', this, 'hideActions');
};


XMLEditor.prototype = {

    getContentElement: function() {
        // return the cnotent element
        return getElement(this.contentElementId);
    },

    replaceContent: function(content) {
        // Replace the content of the editor with `content`.
        var content_node = this.getContentElement()
        content_node.innerHTML = content;
    },



    getActionsPane: function() {
        // returns the Actions pane
        return getElement('xml-editor-actions');
    },


    hideActionsPane: function(fade_out) {
        // Hide the actions pane
        // if fade_out is true the node is faded out. It's imeadiately removed
        // otherwise.
        var actions_pane = this.getActionsPane();
        if (!actions_pane) return;
        removeElementClass(actions_pane.bound_to, 'active');
        var remove_node = function() {
          disconnectAll(actions_pane);
          var parent_node = actions_pane.parentNode;
          if (parent_node) {
            parent_node.removeChild(actions_pane);
          }
        }
        
        var options;
        if (fade_out) {
            options = {afterFinish: remove_node};
        } else {
            options = {}
        }

        signal(actions_pane, 'zeit.newactions');
        fade(actions_pane, options)
        if (!fade_out) {
            remove_node();
        } 
    },

    showActionsPane: function(where, node) {
        // Show the actions pane for `node` at position `where`
        var editor = this;
        while (true) {
            var path = node.getAttribute('path')
            if (path == null) {
                node = node.parentNode
            } else {
                break
            }
            if (node.nodeName == 'HTML') {
                break
            }
        }
        if (path == null) {
            return;
        }

        addElementClass(node, 'active');

        var actions_pane = this.getActionsPane();
        if (actions_pane != null) {
            if (actions_pane.bound_to == node)
                return;
            this.hideActionsPane()
        }

        actions_pane = this.createActionsPane(node);
        d = this.fillPane(actions_pane, 'edit_actions');
        d.addCallback(function(result) {
            var node_dim = getElementDimensions(node);
            var pane_dim = getElementDimensions(actions_pane);
            var new_width = node_dim.w - 3;
            if (new_width > pane_dim.w) {
                // We only want to make the pane larger. If it is larger than
                // the node already looks bad.
                pane_dim.w = node_dim.w - 2;
            }
            setElementDimensions(actions_pane, pane_dim);
            var pane_pos = getElementPosition(actions_pane)
            pane_pos.x -= 3;
            pane_pos.y -= pane_dim.h;
            setElementPosition(actions_pane, pane_pos);
            setStyle(actions_pane, {'opacity': '1'});
            
            return result;
        });
    
        d.addCallback(function(result) {
            var actions = getElementsByTagAndClassName('img', 'action',
                                                       actions_pane);
            forEach(actions, function(action) {
                var drop_action = action.getAttribute('drop-action');
                if (drop_action == undefined)
                    return;

                Droppable(action, {
                    ondrop: function(draggable, last_active_element, event) {
                            editor.handleDrop(drop_action, draggable);
                        },
                    hoverclass: 'droppable',
                });
            });
            return result;
        });
    },

    createActionsPane: function(node) {
        var actions_pane = document.createElement('div');
        setStyle(actions_pane, {'opacity': '0'});
        actions_pane.id = 'xml-editor-actions';

        connect(actions_pane, 'onclick', this, 'handleActionClick');
        actions_pane.bound_to = node;
        node.insertBefore(actions_pane, node.firstChild);
        return actions_pane;
    },

    // Editor pane

    getEditorPane: function(node) {
        return getElement('xml-editor-edit-pane');
    },

    getNewEditorPane: function(node) {
        var pane = this.getEditorPane();
        if (pane != null) {
            disconnectAll(pane)
            pane.parentNode.removeChild(pane);
        }
        pane = document.createElement('div');
        pane.id = 'xml-editor-edit-pane';
        pane.bound_to = node
        this.getContentElement().appendChild(pane)
        return pane
    },


    // Adding nodes

    showAppendChild: function(node, where, action) {
        var pane = this.getNewEditorPane(node);
        connect(pane, 'onclick', this, 'handleAppendChildEvent')

        var actions_pane = this.getActionsPane();
        connect(actions_pane, 'zeit.newactions',
            function() {
                fade(pane);
            });
        
        d = this.fillAndShowPane(pane, where, 'addChildView', {'action': action})
        d.addErrback(alert);
    },

    appendChild: function(node, action, tag) {
        var editor = this;
        var path = node.getAttribute('path');
        var d = doSimpleXMLHttpRequest(this.base_url + 'appendChild',
             {'path': path,
              'action': action,
              'tag': tag});
        d.addCallback(this.inspectAjaxResult);
        d.addCallbacks(
            function(result) {
                editor.handleContentReplaceResult(result)
            },
            alert);
    },

    appendChildFromDrop: function(node, action, unique_id) {
        log("Inserting", unique_id, "after", path);
        var editor = this;
        var path = node.getAttribute('path');
        var d = doSimpleXMLHttpRequest(this.base_url + 'dropAppendChild',
             {'path': path,
              'action': action,
              'unique_id': unique_id});
        d.addCallback(this.inspectAjaxResult);
        d.addCallbacks(
            function(result) {
                editor.replaceContent(result);
            },
            alert);
    },

    dropInsertAfter: function(node, unique_id) {
        this.appendChildFromDrop(node, 'insert-after', unique_id);
    },

    dropInsertBefore: function(node, unique_id) {
        this.appendChildFromDrop(node, 'insert-before', unique_id);
    },

    dropAppendChild: function(node, unique_id) {
        this.appendChildFromDrop(node, 'append-child', unique_id);
    },

    // Inline editor

    showEditText: function(node, where) {
        var pane = this.getNewEditorPane(node);
        connect(pane, 'onclick', this, 'handleEditClick')
        d = this.fillAndShowPane(pane, where, 'editNodeView')
        d.addErrback(alert);
    },


    editNodeSave: function() {
        var pane = this.getEditorPane();
        var editor = this;
        var form = getElement('zc.page.browser_form');
        var data = map(function(element) {
                return element.name + "=" + encodeURIComponent(element.value)
            }, form.elements);
        data = data.join('&');
        var d = doXHR(form.getAttribute('action'), {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded'},
            'sendContent': data});
        d.addCallbacks(
            function(result) {
                pane.innerHTML = result.responseText
                var errors = getElement('form-errors')
                if (errors != null)
                    return;
                editor.closeEditPane();
                return editor.refreshContent();
            },
            alert);
    },

    closeEditPane: function() {
        fade(this.getEditorPane());
    },


    refreshContent: function() {
        // reload the content of the editor form the server
        var d = doSimpleXMLHttpRequest(this.base_url + 'xml_source.html');
        var editor = this;
        d.addCallbacks(function(result) {
            editor.getContentElement().innerHTML = result.responseText;
            return result
            },
            alert)
        return d
    },



    // Helper

    fillPane: function(pane, remote_method, options) {
        // fill `pane` with the data returned by the server method
        // `remote_method`.

        var node = pane.bound_to;
        var path = node.getAttribute('path');
        if (options == undefined) {
            options = {};
        }
        options.path = path
        var d = doSimpleXMLHttpRequest(this.base_url + remote_method, options);
        d.addCallback(
            function(result) {
                pane.innerHTML = result.responseText;
                return result;
            });
        return d
    },

    showPane: function(pane, where) {
        // Show a fixed positioned pane *on* the  screen
        if (where != null) {
            var pane_dim = getElementDimensions(pane);
            var viewport_dim = getViewportDimensions()
            var max_x = viewport_dim.w - pane_dim.w - 10;
            if (where.x > max_x) {
                where.x = max_x;
            }
            var max_y = viewport_dim.h - pane_dim.h - 10;
            if (where.y > max_y) {
                where.y = max_y;
            }
            setElementPosition(pane, where);
        }
        setStyle(pane, {'opacity': '1'});
    },

    fillAndShowPane: function(pane, where, remote_method, options) {
        // shortcut method for fillPane and showPane
        var editor = this;
        var d = this.fillPane(pane, remote_method, options);
        d.addCallback(
            function(result) {
                editor.showPane(pane, where);
                return result;
            });
        return d

    },


    removeNode: function(node) {
        // Removing `node` from document
        var editor = this;
        var path = node.getAttribute('path')
        var d = doSimpleXMLHttpRequest(this.base_url + 'remove',
                                      {'path': path})
        d.addCallbacks(
            function(result) { 
                puff(node, {
                    afterFinish: function() {
                        editor.replaceContent(result.responseText)
                    },
                });
                return result;
                },
         alert);
    },

    // Drag and drop

    connectDraggable: function(node) {
        var path = node.getAttribute('path');
        if (!path) return;

        node.drag_pane_url = this.base_url + 'node-drag-pane.html?path=' + path;
        this.draggable = Draggable(node, {
            starteffect: function(drag_pane) {
                addElementClass(drag_pane.source_element, 'dragged');
            },
            endeffect: function(dragged_element) {
                removeElementClass(dragged_element, 'dragged');
            },
        });
    },

    /* Event Handlers */

    handleActionClick: function(event) {
        // Add child to document.
        var target = event.target();
        var action = target.getAttribute('action');
        if (action == null) {
            return;
        }
        this[action](event)
    },

    handleEditClick: function(event) {
        // Add child to document.
        var target = event.target();
        if (target.type != 'button') {
            return;
        }
        var action = target.name;
        if (action == null) {
            return;
        }
        if (action == 'form.actions.apply') {
            action = 'editNodeSave';
        }
        this[action](event)
    },

    handleRemoveNodeEvent: function(event) {
        // remove a node from the document
        this.removeNode(this.getActionsPane().bound_to);
    },

    handleShowAppendChildEvent: function(event) {
        // Show view for adding a child to document.
        this.showAppendChild(
            this.getActionsPane().bound_to,
            event.mouse().page,
            'append-child');
    },

    handleShowInsertBeforeEvent: function(event) {
        // Show view for adding a child to document.
        this.showAppendChild(
            this.getActionsPane().bound_to,
            event.mouse().page,
            'insert-before');
    },

    handleShowInsertAfterEvent: function(event) {
        // Show view for adding a child to document.
        this.showAppendChild(
            this.getActionsPane().bound_to,
            event.mouse().page,
            'insert-after');
    },

    handleShowEditTextViewEvent: function(event) {
        this.showEditText(this.getActionsPane().bound_to, event.mouse().page);
    },

    handleAppendChildEvent: function(event) {
        // Add child to document.
        var target = event.target();
        var action = target.getAttribute('action');
        if (action == null) {
            return;
        }
        var tag = target.getAttribute('xml-tag');
        var context = this.getEditorPane().bound_to;
        this.appendChild(context, action, tag);
    },

    showActions: function(event) {
        this.showActionsPane(event.mouse().page, event.target())
        this.connectDraggable(event.target());
        event.stop()
    },

    hideActions: function(event) {
        var target = event.target();
        if (target.getAttribute('id') == 'xml-editor' ||
            target.getAttribute('action') == 'hideActions')
            this.hideActionsPane(true);
    },

    handleDrop: function(drop_action, drag_pane) {
        var unique_id = getFirstElementByTagAndClassName(
            'div', 'UniqueId', drag_pane).textContent
        var target = this.getActionsPane().bound_to

        log("Dropped", unique_id, "on", drop_action, target);
        this[drop_action](target, unique_id);
    },


    inspectAjaxResult: function(result) {
        result = evalJSON(result.responseText);
        if (result['error'] == true) {
            throw result['value'];
        }
        return result['value'];
    },

    handleContentReplaceResult: function(result) {
        this.replaceContent(result['xml']);
        var node_path = result['node-path']
        var xpath = '//*[@path="' + node_path + '"]';
        log(xpath);
        var node = document.evaluate
            (xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE,
            null).singleNodeValue;
        var where = getElementPosition(node);
        this.showEditText(node, where)
        return result
    },
}

