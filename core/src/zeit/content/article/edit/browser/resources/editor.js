(function() {

zeit.cms.declare_namespace('zeit.content.article');

var wire_forms = function() {
    forEach($$('#article-metadata .inline-form'), function(container) {
        //XXX need to make it context aware
        var url = container.getAttribute('action');
        var form = new zeit.cms.SubPageForm(
            url, container, {save_on_change: true});
    });
};


var ident = MochiKit.Signal.connect(
    zeit.edit.editor, 'script-loading-finished',
    function() {
        MochiKit.Signal.disconnect(ident);

    zeit.content.article.body_sorter = new zeit.edit.sortable.BlockSorter(
        'editable-body');
    wire_forms();
    });

// Initialize module library
MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {
    zeit.edit.library.create(
        'article', context_url + '/editable-body', 'Artikel');
});

zeit.edit.drop.registerHandler({
    accept: ['editable-body-module'],
    activated_by: 'action-editable-body-module-droppable',
    url_attribute: 'cms:create-block-url',
    query_arguments: function(draggable) {
        return {'block_type': draggable.getAttribute('cms:block_type')};
    }
});




zeit.content.article.Editable = gocept.Class.extend({
    // Inline editing module

    editor_active_lock: new MochiKit.Async.DeferredLock(),

    construct: function(context_element, place_cursor_at_end) {
        var self = this;
        var block_id = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, null, 'block').id;
        var d = self.editor_active_lock.acquire();
        log('Waiting for lock');
        d.addCallback(function() {
            var block = $(block_id);
            if (block === null) {
                // block vanished while waiting for lock.
                return;
            }
            self.events = [];
            self.edited_paragraphs = [];
            self.initial_paragraph = MochiKit.Selector.findChildElements(
                block, ['.editable > *'])[0];
            self.editable = self.merge(block);
            self.block = MochiKit.DOM.getFirstParentByTagAndClassName(
                self.editable, null, 'block');
            log('Editable block', self.block.id);
            self.editable.removeAttribute('cms:cp-module');
            self.editable.contentEditable = true;
            self.editable.focus();
            self.command('styleWithCSS', false);
            MochiKit.DOM.addElementClass(self.block, 'editing');
            
            // This catches the blur-signal in the capturing-phase!
            // In case you use the toolbar, the editing-mode won't be stopped.
            self.editable.parentNode.addEventListener("blur", function(e) {
                var clicked_on_block = 
                    MochiKit.DOM.getFirstParentByTagAndClassName(
                       e.explicitOriginalTarget, 'div', 'block');
                is_in_block = (clicked_on_block == self.block);
                log("Blur while editing:", is_in_block);
                if (is_in_block) {
                    e.stopPropagation();
                } else {
                    self.save();
                }
            }, true);
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onkeydown', self, self.handle_keydown));
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onkeyup', self, self.handle_keyup));
            self.place_cursor(self.initial_paragraph, place_cursor_at_end);
            self.init_toolbar();
            self.relocate_toolbar(true);
        });
    },
    
    place_cursor: function(element, place_cursor_at_end) {
        // Place cursor to the beginnning of element
        log('Placing cursor to', element.nodeName);
        var range = getSelection().getRangeAt(0);
        var direction;
        if (place_cursor_at_end)  {
            direction = 'lastChild';
        } else {
            direction = 'firstChild';
        }

        var text_node = element;
        while (text_node[direction] !== null) {
            text_node = text_node[direction];
        }
        var select_node = text_node.parentNode;
        var offset = 0;
        if (place_cursor_at_end)  {
            offset = text_node.data.length;
        }
        range.setStart(text_node, offset);
        range.setEnd(text_node, offset);
    },

    is_block_editable: function(block) {
        return !isNull(
            MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'editable', block));
    },

    merge: function(block) {
        var self = this;
        var blocks = MochiKit.DOM.getElementsByTagAndClassName(
            null, 'block', block.parentNode);
        var i = blocks.indexOf(block);
        var paragraphs = [];
        // XXX remove code duplication
        while (i > 0) {
            i -= 1;
            if (self.is_block_editable(blocks[i])) {
                paragraphs.push(blocks[i]);
            } else {
                break;
            }
        }
        paragraphs.reverse();
        paragraphs.push(block);
        i = blocks.indexOf(block);
        while (i < blocks.length-1) {
            i += 1;
            if (self.is_block_editable(blocks[i])) {
                paragraphs.push(blocks[i]);
            } else {
                break;
            }
        }
        self.edited_paragraphs = MochiKit.Base.map(
            function(element) { return element.id; },
            paragraphs);
        var editable = MochiKit.DOM.getFirstElementByTagAndClassName(
            null, 'editable', paragraphs[0]);
        forEach(paragraphs.slice(1), function(paragraph) {
            forEach(MochiKit.Selector.findChildElements(
                paragraph, ['.editable > *']), function(p) {
                editable.appendChild(p);
            });
            MochiKit.DOM.removeElement(paragraph);
        });
        // Clear out all non element nodes
        forEach(editable.childNodes, function(child) {
            if (child.nodeType != child.ELEMENT_NODE) {
                editable.removeChild(child);
            }
        });
        return editable;
    },

    init_toolbar: function() {
        var self = this;
        self.toolbar = self.editable.parentNode.insertBefore(
            DIV({'class': 'rte-toolbar',
                 'style': 'display: block; opacity: 0'}),
            self.editable);
        self.toolbar.innerHTML = "\
            <a rel='command' href='bold'>B</a>\
            <a rel='command' href='italic'>I</a>\
            <a rel='command' href='insertunorderedlist'>UL</a>\
            <a rel='command' href='insertorderedlist'>OL</a>\
            <a rel='command' href='formatBlock/h3'>T</a>\
            <a rel='command' href='formatBlock/p'>P</a>\
            <a href='#' class='rteButton link'>A</a>\
            <a rel='method' href='save' class='rteButton'>save</a>\
            ";
        self.events.push(MochiKit.Signal.connect(
            self.block, 'onclick',
            self, self.handle_click));
        MochiKit.Visual.appear(self.toolbar);
    },

    relocate_toolbar: function(fast) {
        var self = this;
        var range = getSelection().getRangeAt(0);
        var container = range.commonAncestorContainer;
        while (container.nodeType != container.ELEMENT_NODE) {
            container = container.parentNode;
        }
        var move = {
            duration: 0.5,
            mode: 'absolute',
            x: MochiKit.Style.getElementPosition(self.toolbar, self.block).x,
            y: MochiKit.Style.getElementPosition(container, self.block).y
        }
        if (fast) {
            MochiKit.Style.setElementPosition(self.toolbar, move);
        } else {
            MochiKit.Visual.Move(self.toolbar, move);
        }
    },

    handle_click: function(event) {
        var self = this;
        self.relocate_toolbar();
        if (event.target().nodeName != 'A') {
            return;
        }
        event.stop();
        if (event.target().rel == 'command') {
            event.stop();
            var action = event.target().getAttribute('href').split('/');
            self.command(action[0], action[1]);
        } else if (event.target().rel == 'method') {
            var method = event.target().getAttribute('href');
            self[method]();
        }
    },

    handle_keydown: function(event) {
        var self = this;

        var range = getSelection().getRangeAt(0);
        var container = range.commonAncestorContainer;
        // lastnode/firstnodee?
        var direction = null;
        var cursor_at_end = false;
        if (event.key().string == 'KEY_ARROW_DOWN' &&
            container.nodeType == container.TEXT_NODE &&  // Last
            container.parentNode.nextSibling === null &&  // node
            MochiKit.DOM.scrapeText(container).length == range.endOffset) {
            direction = 'nextSibling';
        } else if (
            event.key().string == 'KEY_ARROW_UP' &&
            container.nodeType == container.TEXT_NODE &&      // First
            container.parentNode.previousSibling === null &&  // node
            range.startOffset === 0) {
            direction = 'previousSibling';
            cursor_at_end = true;
        }
        if (direction !== null) {
            var blocks = MochiKit.Selector.findChildElements(
                self.block.parentNode, ['.block']);
            var block = self.block;
            var next_block = null;
            while (block[direction] !== null) {
                block = block[direction];
                if (block.nodeType != block.ELEMENT_NODE) {
                    continue;
                }
                if (MochiKit.DOM.hasElementClass(block, 'block') && 
                    self.is_block_editable(block)) {
                    next_block = block;
                    break;
                }
            }
            if (next_block !== null) {
                log('Next block', next_block.id);
                // Note id as save may (or probably will) replace the element
                var next_block_id = next_block.id;
                self.save();
                new zeit.content.article.Editable(
                    MochiKit.DOM.getFirstElementByTagAndClassName(
                        'div', 'editable', $(next_block_id)),
                    cursor_at_end);
                event.stop();
            }

        }
    },

    handle_keyup: function(event) {
        var self = this;
        self.relocate_toolbar();
    },

    get_text_list: function() {
        var self = this;
        var result = [];
        forEach(self.editable.childNodes, function(element) {
            if (element.nodeType == element.ELEMENT_NODE) {
                result.push({factory: element.nodeName.toLowerCase(),
                             text: element.innerHTML});
            }
        });
        return result;
    },

    save: function() {
        var self = this;
        log('Saving');
        MochiKit.DOM.addElementClass(self.block, 'busy');
        while (self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        }
        // until now, the editor can only be contained in an editable-body.
        var url = $('editable-body').getAttribute('cms:url') + '/@@save_text';
        zeit.edit.makeJSONRequest(url, {
            paragraphs: self.edited_paragraphs,
            text: self.get_text_list()});
        var ident = MochiKit.Signal.connect(
            zeit.edit.editor, 'after-reload', function() {
            MochiKit.Signal.disconnect(ident);
            self.editor_active_lock.release();
        });
    },

    command: function(command, option) {
        var self = this;
        log("Executing", command, option);
        try {
            document.execCommand(command, false, option);
        } catch(e) {
            window.console && console.log(e);
		}
		//this._updateToolbar();
    }

});

})();
