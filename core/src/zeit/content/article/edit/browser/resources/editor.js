(function($){

    $.fn.limitedInput = function(limit) {
        return this.each(function() {
            var self = $(this);
            var container = self.find('.widget:first');
            var area = $('textarea', container);
            var val = area.val().length || 0;
            var span = $('<span />').addClass('charlimit').html(
                (val > 0 ? limit - val : limit) + " Zeichen");
            container.prepend(span);
            area.bind("keyup focus blur", function (e) {
                var count = limit - $(e.target).val().length;
                if (count < 21 && count > 10) {
                    span.css("color", "#900").html(count + " Zeichen");
                } else if (count < 11) {
                    span.css("color", "#ff0000").html(count + " Zeichen");
                } else {
                    span.css("color", "#777").html(count + " Zeichen");
                }
            });
        });
    };

    $.fn.createLogExpander = function() {
        var self = $(this);
        if (self.find('br').length < 5) { return; }
        var log  = self.children('.widget-outer:first')
                       .css({'max-height': '7.5em', 'overflow': 'hidden'});
        var expander = $('<button />').html('Log ausklappen').appendTo(self);
        expander.addClass('log-expander');
        expander.toggle(
            function() {
                log.css({'max-height': ''});
                expander.html('Log einklappen');
            },
            function() {
                log.css({'max-height': '7.5em'});
                expander.html('Log ausklappen');
            }
        );
    };

    $.fn.countedInput = function() {
        var self = $(this);
        var count = function() {
            var l = self.find('.editable').children().text().length || 0;
            var container = self.parent();
            container.find('.charcount').html(l + " Zeichen");
        };
        self.bind('keyup', count);
        count();
    };

    $.fn.resizeFont = function() {
        var self = $(this);
        var resize = function(size) {
            var editable = $('#editable-body .editable');
            editable.css("font-size", size);
            sessionStorage.setItem("editor-font-size", size);
        };
        var curr_size = parseFloat(sessionStorage.getItem("editor-font-size")) || 16;
        resize(curr_size);

        $('.fontbutton').live("click", function(e) {
            if ($(e.target).hasClass("fontplus") && (curr_size < 25)) {
                ++curr_size;
            } else if ($(e.target).hasClass("fontminus") && (curr_size > 11)) {
                --curr_size;
            } else if ($(e.target).hasClass("fontnormal")) {
                curr_size = 16;
            }
            resize(curr_size);
        });

        MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
            resize(curr_size);
        });
    };

}(jQuery));


(function() {

zeit.cms.declare_namespace('zeit.content.article');

// Initialize module library
MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {
    zeit.edit.library.create(
        'article-modules', context_url + '/editable-body', 'Artikel');

    var form_element = jQuery('form[action$="@@edit.form.context-action"]')[0];
    MochiKit.Signal.connect(window, 'changed', function(form) {
        if (form_element.form === form) {
            return;
        }
        MochiKit.Async.callLater(0.25, function() {
            form_element.form.reload(); });

        jQuery('#article-editor-text').countedInput();
    });

    (function($) {

        $('.editable-area > .block-inner').append('<div class="totop">↑</div>');

        $('.totop').live("click", function() {
            $('#cp-content-inner').animate({scrollTop: 0}, 300);
        });

    }(jQuery));

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
        self.block_id = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, null, 'block').id;
        self.locked = false;
        var d = self.editor_active_lock.acquire();
        log('Waiting for lock', self.block_id);
        d.addCallback(function() {
            log('Lock acquired', self.block_id);
            var block = $(self.block_id);
            if (block === null) {
                // block vanished while waiting for lock.
                self.editor_active_lock.release();
                log('block vanished', self.block_id);
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
                var is_in_block = (clicked_on_block == self.block);
                log("Blur while editing:", is_in_block, self.block_id);
                if (is_in_block || self.locked) {
                    e.stopPropagation();
                } else {
                    self.save();
                }
            }, true);
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onkeydown', self, self.handle_keydown));
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onkeyup', self, self.handle_keyup));
            // This handler is there to support saving during selenium tests as
            // it doesn't seem to be possible to synthesize an blur event which
            // triggers the capuring phase handler:
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'save', function() {self.save();}));
            self.events.push(MochiKit.Signal.connect(
                zeit.edit.editor, 'before-reload', function() {
                    // XXX giant hack around strange browser behaviour.
                    //
                    // Reproduction recipe for the bug: While a block is
                    // contentEditable, drag it around to change sorting. This
                    // will result in a blinking cursor being left somewhere on
                    // the page. In spite of investigating this at length, we
                    // have no idea what causes this, so far.
                    //
                    // To get rid of this stray cursor, we focus-then-blur
                    // something else (we scientifcally chose the
                    // fulltext-search input box at random). Synthesizing a
                    // blur on self.editable or similar has no effect, and the
                    // "something else" we dash off to needs to be an <input
                    // type="text">.
                    $('fulltext').focus();
                    $('fulltext').blur();
                    self.save(/*no_reload=*/true);
                }));
            self.fix_html();
            self.place_cursor(self.initial_paragraph, place_cursor_at_end);
            self.init_linkbar();
            self.init_toolbar();
            self.relocate_toolbar(true);
            self.events.push(MochiKit.Signal.connect(
                window, 'before-content-drag', function() {
                    if (!self.locked) {
                        self.save();
                    }
                }));
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
        paragraphs[0].block_ids = self.edited_paragraphs;
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

    init_linkbar: function() {
        var self = this;
        self.link_input = self.editable.parentNode.insertBefore(
            DIV({'class': 'link_input hidden'},
                INPUT({type: 'text', name: 'href', value: ''}),
                SELECT({name: 'target'},
                    OPTION({value: ''}, ''),
                    OPTION({value: '_blank'}, 'Neues Fenster')),
                BUTTON({name: 'insert_link_ok',
                        value: 'method'}, 'Setzen'),
                BUTTON({name: 'insert_link_cancel',
                        value: 'method'}, 'Abbrechen')),
            self.editable);
        self.link_input.dropable = new MochiKit.DragAndDrop.Droppable(
            self.link_input, {
                accept: ['content-drag-pane', 'uniqueId'],
                activeclass: 'droppable-active',
                hoverclass: 'hover-content',
                ondrop: function(element, last_active_element, event) {
                        // One could consider the replace a hack.
                        jQuery('input[name=href]', self.link_input).val(
                            element.uniqueId.replace(
                                'http://xml.zeit.de/',
                                'http://www.zeit.de/'));
                }
            });
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
            <a rel='method' href='insert_link'>A</a>\
            <a rel='command' href='unlink'>A</a>\
            ";
        self.events.push(MochiKit.Signal.connect(
            self.block, 'onclick',
            self, self.handle_click));
        MochiKit.Visual.appear(self.toolbar);
        self.update_toolbar();
    },

    update_toolbar: function() {
        var self = this;
        var element = self.get_selected_container();
        log('got', element.nodeName);
		if (element.nodeType == element.TEXT_NODE) {
            element = element.parentNode;
        }
        forEach(MochiKit.DOM.getElementsByTagAndClassName(
            'a', null, self.toolbar), function(action) {
            MochiKit.DOM.removeElementClass(action, 'active');
        });
        while(!isNull(element) && element != self.editable) {
            log('checking', element.nodeName);
            forEach(MochiKit.DOM.getElementsByTagAndClassName(
                'a', null, self.toolbar), function(action) {
                if (action.innerHTML == element.nodeName) {
                    MochiKit.DOM.addElementClass(action, 'active');
                }
            });
            element = element.parentNode;
		}

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
        };
        if (fast) {
            MochiKit.Style.setElementPosition(self.toolbar, move);
        } else {
            MochiKit.Visual.Move(self.toolbar, move);
        }
     },

    handle_click: function(event) {
        var self = this;
        var mode, argument;
        self.update_toolbar();
        self.relocate_toolbar();
        if (event.target().nodeName == 'A') {
            mode = event.target().rel;
            argument = event.target().getAttribute('href');
        } else if (event.target().nodeName == 'BUTTON') {
            mode = event.target().value;
            argument = event.target().name;
        } else {
            return;
        }
        event.stop();
        if (mode == 'command') {
            event.stop();
            var action = argument.split('/');
            self.command(action[0], action[1]);
        } else if (mode == 'method') {
            var method = argument;
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
        } else if (
            container.nodeType == container.TEXT_NODE &&
            container.parentNode.tagName == 'DIV') {
            /*
             * Currently contenteditable seems to be buggy in firefox 4.
             * While a new paragraph is created every time the return key has
             * been pressed inside a paragraph, there will be just a textnode as
             * direct child of the contenteditable, when hitting the return key
             * within any other tag (e.g. h3, li...). The following workaround
             * will wrap a p around every textnode, which is the direct child of
             * the contenteditable.
             *
             * Sometimes another paragraph is added accidentally, when pressing
             * the up and down keys within an empty p tag, so we have to get rid
             * of the previous and next empty paragraph respectively.
             */
            self.command('formatBlock', 'p');
            var next_sibling = container.parentNode.nextSibling;
            var prev_sibling = container.parentNode.previousSibling;
            if (next_sibling != null &&
                next_sibling.nodeName == 'BR') {
                jQuery(next_sibling).remove(); // Get rid of superfluous <br/>.
            } else if (
                next_sibling != null &&
                next_sibling.nodeName == 'P') {
                jQuery(next_sibling).remove(); // Get rid of empty <p/>.
            } else if (
                prev_sibling != null &&
                prev_sibling.nodeName == 'P') {
                jQuery(prev_sibling).remove(); // Get rid of empty <p/>.
            }
        }
        if (direction !== null) {
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
        self.update_toolbar();
        self.relocate_toolbar();
        self.fix_html();
    },

    fix_html: function() {
        var self = this;
        self.editable.normalize();
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
                null, null, self.editable),
            function(element) {
                element.removeAttribute('class');
                element.removeAttribute('style');
                // Yeah, I luv it!
                if (element.nodeName == 'EM') {
                    zeit.content.article.html.change_tag(element, 'I');
                } else if (element.nodeName == 'STRONG') {
                    zeit.content.article.html.change_tag(element, 'B');
                }
        });
    },

    get_text_list: function() {
        var self = this;

        self.fix_html();
        var tree = self.editable.cloneNode(/*deep=*/true);
        zeit.content.article.html.to_xml(tree);

        var result = MochiKit.Base.map(function(el) {
            return {factory: el.nodeName.toLowerCase(),
                    text: el.innerHTML};
        }, tree.childNodes);

        return result;
    },

    save: function(no_reload) {
        var self = this;
        log('Saving', self.block_id);
        MochiKit.DOM.addElementClass(self.block, 'busy');
        while (self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        }
        self.link_input.dropable.destroy();
        log('disconnected event handlers');
        var ident = MochiKit.Signal.connect(
            zeit.edit.editor, 'after-reload', function() {
            MochiKit.Signal.disconnect(ident);
            log('Release lock', self.block_id);
            self.editor_active_lock.release();
        });
        // until now, the editor can only be contained in an editable-body.
        var url = $('editable-body').getAttribute('cms:url') + '/@@save_text';
        var data = {paragraphs: self.edited_paragraphs,
                    text: self.get_text_list()};
        if (no_reload) {
            data = MochiKit.Base.serializeJSON(data);
            zeit.edit.with_lock(
                MochiKit.Async.doXHR,
                url, {method: 'POST', sendContent: data});
        } else {
            zeit.edit.makeJSONRequest(url, data);
        }
    },

    get_selected_container: function() {
        var container;
        var range = getSelection().getRangeAt(0);
        if ((range.startContainer.nodeType ==
             range.startContainer.ELEMENT_NODE) &&
            (range.startContainer == range.endContainer) &&
            (range.startOffset + 1 == range.endOffset)) {
             // There is one single element inside the range, use that.
             container = range.startContainer.childNodes[range.startOffset];
        } else {
            container = range.commonAncestorContainer;
        }
        return container;
    },

    select_container: function(element) {
        var self = this;
        try {
            var range = getSelection().getRangeAt(0);
            range.setStartBefore(element);
            range.setEndAfter(element);
        } catch(e) {
            if (window.console) {
                console.log(e);
            }
        }
    },

    insert_link: function() {
        var self = this;
        if (self.locked) {
            return;
        }
        var container = self.get_selected_container();
        if (container.nodeName == 'A') {
            self.insert_link_node = container;
        } else {
            self.insert_link_node =
                MochiKit.DOM.getFirstParentByTagAndClassName(
                    container, 'a', null);
        }
        var href = '';
        var target = '';
        if (self.insert_link_node) {
            href = self.insert_link_node.getAttribute('href') || '';
            target = self.insert_link_node.getAttribute('target') || '';
        } else {
            self.command('createLink', '#article-editor-create-link');
            self.insert_link_node = jQuery(
                'a[href="#article-editor-create-link"]', self.editable)[0];
            self.insert_link_node._just_created = true;
        }
        jQuery(self.insert_link_node).addClass('link-edit');
        jQuery('*[name=href]', self.link_input).val(href);
        jQuery('*[name=target]', self.link_input).val(target);
        var line_height = parseInt(
            jQuery(self.insert_link_node).css('line-height').replace('px', ''));
        var position = jQuery(self.insert_link_node).position();
        jQuery(self.link_input).css('top',
            (parseInt(position.top) + line_height) + 'px');
        jQuery(self.link_input).removeClass('hidden');
        jQuery('*[name=href]', self.link_input).focus();
        self.locked = true;
    },

    insert_link_ok: function() {
        var self = this;
        var href = jQuery('*[name=href]', self.link_input).val();
        var target = jQuery('*[name=target]', self.link_input).val();
        self.insert_link_node.href = href;
        if (target) {
            self.insert_link_node.target = target;
        } else {
            self.insert_link_node.removeAttribute('target');
        }
        self.select_container(self.insert_link_node);
        self._insert_link_finish();
    },

    insert_link_cancel: function() {
        var self = this;
        self.select_container(self.insert_link_node);
        if (self.insert_link_node._just_created) {
            while(!isNull(self.insert_link_node.firstChild)) {
                self.insert_link_node.parentNode.insertBefore(
                    self.insert_link_node.firstChild,
                    self.insert_link_node);
            }
            jQuery(self.insert_link_node).remove();
        }
        self._insert_link_finish();
    },

    _insert_link_finish: function() {
        var self = this;
        jQuery(self.link_input).addClass('hidden');
        jQuery(self.insert_link_node).removeClass('link-edit');
        self.insert_link_node._just_created = false;
        self.insert_link_node = null;
        self.locked = false;
        self.editable.focus();
    },

    command: function(command, option) {
        var self = this;
        if (self.locked) {
            return;
        }
        log("Executing", command, option);
        try {
            document.execCommand(command, false, option);
        } catch(e) {
            if (window.console) {
                console.log(e);
            }
	    }
        self.editable.focus();
		self.update_toolbar();
    }

});

}());
