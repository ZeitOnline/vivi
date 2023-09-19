(function($){

zeit.cms.declare_namespace('zeit.content.article');

zeit.cms.in_article_editor = function() {
    return Boolean(jQuery('.article-editor-inner').length);
};

var invalidHosts = [
    'vivi.zeit.de', 'friedbert-preview.zeit.de', 'xml.zeit.de',
    'vivi.staging.zeit.de', 'friedbert-preview.staging.zeit.de',
    'xml.staging.zeit.de' ];


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (! zeit.cms.in_article_editor()) {
        return;
    }

    // Initialize module library
    zeit.edit.library.create(
        'article-modules', context_url + '/editable-body', 'Artikel');
    zeit.edit.library.create(
        'header-modules', context_url + '/editable-header', 'Header');

    // Update error messages and checkin button disabled status
    MochiKit.Signal.connect(window, 'changed', function() {
        var workflow_area = $('form[action$="edit.form.publish"]')[0];
        MochiKit.Async.callLater(0.25, function() {
            workflow_area.form.reload(); });

    });

    // prevent accidental "back button" events
    $(document).on('keydown', function(event) {
        if (event.which !== 8) {  // BACKSPACE
            return;
        }
        if ($(event.target).closest('#editable-body .editing').length) {
            return;
        }
        var tag = event.target.nodeName.toLowerCase();
        if ((tag === 'input' && event.target.type === 'text')
            || tag === 'textarea') {
            return;
        }
        log('preventing back button');
        event.preventDefault();
    });

    // set up "to top" links
    $('.totopclick').live("click", function() {
        $('#cp-content-inner').animate({scrollTop: 0}, 300);
    });

});


MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    if (! zeit.cms.in_article_editor()) {
        return;
    }

    zeit.edit.drop.registerHandler({
        accept: ['editable-body-module'],
        activated_by: 'action-editable-body-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type')};
        }
    });

    zeit.edit.drop.registerHandler({
        accept: ['editable-header-module'],
        activated_by: 'action-editable-header-module-droppable',
        url_attribute: 'cms:create-block-url',
        query_arguments: function(draggable) {
            return {'block_type': draggable.getAttribute('cms:block_type')};
        }
    });

    zeit.edit.drop.registerContentHandler({
        accept: ['type-audio', 'type-animation', 'type-author',
                 'type-image', 'type-image-group',
                 'type-gallery', 'type-video',
                 'type-infobox', 'type-portraitbox',
                 'type-text', 'type-embed',
                 'type-volume'],
        activated_by: 'action-article-body-content-droppable'
    });

});

(function() {
var ident = MochiKit.Signal.connect(
    window, 'script-loading-finished', function() {
        MochiKit.Signal.disconnect(ident);
        if (! zeit.cms.in_article_editor()) {
            return;
        }

        jQuery('#cp-content .action-block-sorter').each(function(i, element) {
            element.body_sorter = new zeit.edit.sortable.BlockSorter(element.id);
        });
});
}());


zeit.content.article.Editable = gocept.Class.extend({
    // Inline editing module

    autosave_interval: 10,
    editor_active_lock: new MochiKit.Async.DeferredLock(),
    unconditional_save_on_blur: false,

    construct: function(context_element, place_cursor_at_end, suppress_focus) {
        var self = this;
        self.dirty = false;
        self.block_id = MochiKit.DOM.getFirstParentByTagAndClassName(
            context_element, null, 'block').id;
        self.locked = false;
        var d = self.editor_active_lock.acquire();
        log('Waiting for lock', self.block_id);
        d.addCallback(function() {
            log('Lock acquired', self.block_id);
            var block = $('#' + self.block_id)[0];
            if (typeof block === "undefined") {
                // block vanished while waiting for lock.
                self.editor_active_lock.release();
                log('block vanished', self.block_id);
                return;
            }
            self.events = [];
            self.edited_paragraphs = [];
            self.autosave_timer = window.setInterval(
                MochiKit.Base.bind(self.autosave, self),
                self.autosave_interval*1000);
            self.initial_paragraph = jQuery('.editable > *', block)[0];
            if (window.getSelection().rangeCount) {
                var range = window.getSelection().getRangeAt(0);
                self.initial_selection_node = range.startContainer;
                self.initial_selection_offset = range.startOffset;
            }
            self.editable = self.merge(block);
            self.block = MochiKit.DOM.getFirstParentByTagAndClassName(
                self.editable, null, 'block');
            // self.block_id is the id of the the block the user clicked on.
            // Unless he clicked on the first block, the id will be wrong now.
            // Prevent anybody from using it.
            delete self.block_id;
            log('Editable block', self.block.id);
            self.editable.removeAttribute('cms:cp-module');
            self.editable.contentEditable = true;
            self.editable.editable = self; // make instance available for tests
            self.command('styleWithCSS', false, false);
            MochiKit.DOM.addElementClass(self.block, 'editing');

            // Catch the blur-signal in the capturing-phase!
            // In case you use the toolbar, the editing-mode won't be stopped.
            var handle_blur = function(e) {
                // Try to detect whether we should close the editor or not.
                var skip_event = false;
                // FocusEvent.relatedTarget = the EventTarget receiving focus (if any)
                // (FF >= 48)
                // Element.closest() returns itself or the matching ancestor.
                // If no such element exists, it returns null. (FF >= 35)
                if (e.relatedTarget) {
                    var clicked_on_block = e.relatedTarget.closest('div.block');
                    skip_event = (clicked_on_block == self.block);
                    if (!skip_event) {
                        var is_in_toolbar = e.relatedTarget.closest('div.rte-toolbar');
                        skip_event = is_in_toolbar;
                    }
                }
                log("Blur while editing:", skip_event, self.block.id);
                if (!self.unconditional_save_on_blur && (
                        skip_event || self.locked)) {
                    e.stopPropagation();
                } else {
                    self.editable.parentNode.removeEventListener(
                        "blur", handle_blur, /*use_capture=*/true);
                    self.save();
                }
            };
            self.editable.parentNode.addEventListener(
                "blur", handle_blur, /*useCapture=*/true);
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onkeydown', self, self.handle_keydown));
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onkeyup', self, self.handle_keyup));
            self.events.push(MochiKit.Signal.connect(
                self.editable, 'onpaste', self, self.handle_paste));
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
                    // something else (we scientifically chose the
                    // fulltext-search input box at random). Synthesizing a
                    // blur on self.editable or similar has no effect, and the
                    // "something else" we dash off to needs to be an <input
                    // type="text">.
                    $('#fulltext').focus();
                    $('#fulltext').blur();
                    self.save(/*supress_reload=*/true);
                }));
            self.fix_html();
            $('body').trigger('update-ads');
            self.place_cursor(place_cursor_at_end);
            if (! suppress_focus) {
                self.editable.focus();
            }
            self.init_linkbar();
            self.init_toolbar();
            self.init_shortcuts();
            self.relocate_toolbar(true);
            self.events.push(MochiKit.Signal.connect(
                window, 'before-content-drag', function(event) {
                    // XXX I guess since window is a DOM object, MochiKit
                    // treats signals differently and does not simply pass
                    // additional parameters to the connected handler?!
                    var draggable = event.event();
                    if (!self.locked) {
                        var ident = MochiKit.Signal.connect(
                            zeit.edit.editor, 'after-reload', function() {
                                MochiKit.Signal.disconnect(ident);
                                MochiKit.DragAndDrop.Droppables.prepare(
                                    draggable.element);
                        });
                        self.save();
                    }
                }));
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
        self.initialized = d;
    },

    place_cursor: function(place_cursor_at_end) {
        var self = this;
        var text_node;
        var offset;
        if (isUndefinedOrNull(place_cursor_at_end)
            && ! isUndefinedOrNull(self.initial_selection_node)) {
            text_node = self.initial_selection_node;
            if (text_node.parentNode) {
                log('Placing cursor to ', text_node.parentNode.nodeName);
            }
            offset = self.initial_selection_offset;
        } else {
            text_node = self.initial_paragraph;
            log('Placing cursor to ', text_node.nodeName);
            var direction_child;
            var direction_sibling;
            if (place_cursor_at_end)  {
                direction_child = 'lastChild';
                direction_sibling = 'previousSibling';
            } else {
                direction_child = 'firstChild';
                direction_sibling = 'nextSibling';
            }

            var child;
            while (text_node.childNodes.length) {
                child = text_node[direction_child];
                // We need to avoid placing the cursor inside a br element
                // since it is not possible to type in there and trying to do
                // so leads to funny effects (#12266). The br element is put in
                // this place in an effort to keep empty paragraphs editable
                // while editing.
                if (child.nodeName !== 'BR') {
                    text_node = child;
                    continue;
                }
                if (child[direction_sibling] !== null) {
                    text_node = child[direction_sibling];
                } else {
                    // BR is the only child so we need to refer to its parent,
                    // i.e. not descend from text_node at all.
                    break;
                }
            }

            offset = 0;
            if (place_cursor_at_end &&
                text_node.nodeType == text_node.TEXT_NODE)  {
                offset = text_node.data.length;
            }
        }
        this._set_selection_offset(text_node, offset);
    },

    _set_selection_offset: function(node, offset) {
        var self = this;
        zeit.content.article.select(node, offset, offset);
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
            jQuery('.editable > *', paragraph).each(function(i, p) {
                editable.appendChild(p);
            });
            jQuery(paragraph).next('.landing-zone').remove();
            MochiKit.DOM.removeElement(paragraph);
        });
        jQuery(paragraphs[0]).next('.landing-zone').remove();
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
        self.error_msg = SPAN({'class': 'link_input_errors', 'style': 'diplay: none;'});
        self.href_input = INPUT(
            {type: 'text', name: 'href', value: '',
             placeholder: 'Verweisziel'});
        self.mailto_input = INPUT(
            {type: 'text', name: 'mailto', value: '',
             placeholder: 'Empfängeradresse'});
        self.subject_input = INPUT(
            {type: 'text', name: 'subject', value: '',
             placeholder: 'Betreff'});
        self.service_select = SELECT(
            {name: 'service'},
            OPTION({value: 'web'}, 'Web'),
            OPTION({value: 'mail'}, 'E-Mail'));
        self.target_select = SELECT(
            {name: 'target'},
            OPTION({value: '_blank'}, 'Neues Fenster'),
            OPTION({value: ''}, 'Gleiches Fenster'),
            OPTION({value: 'colorbox'}, 'Colorbox'));
        self.nofollow_checkbox = INPUT(
            {type: 'checkbox', name: 'nofollow', value: 'nofollow'});
        self.link_input = self.editable.parentNode.insertBefore(
            DIV({'class': 'link_input hidden'},
                self.error_msg,
                self.href_input,
                self.mailto_input,
                self.subject_input,
                self.service_select,
                self.target_select,
                LABEL('', self.nofollow_checkbox, 'rel="nofollow" setzen'),
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
                        element.drag_successful = true;
                        // One could consider the replace a hack.
                        $('input[name=href]', self.link_input).val(
                            element.uniqueId.replace(
                                'http://xml.zeit.de/',
                                'http://www.zeit.de/'));
                }
            });
        self.events.push(
            MochiKit.Signal.connect(
                self.service_select, 'onchange', function(event) {
                    self.linkbar_switch_service($(self.service_select).val());
                }),
            MochiKit.Signal.connect(
            self.link_input, 'onkeydown', function(event) {
                if (event.key().string == 'KEY_ENTER') {
                    self.insert_link_ok();
                    event.stop();
                }
            }));
    },

    linkbar_switch_service: function(service) {
        var self = this;
        $(self.service_select).val(service);
        $(self.href_input).hide();
        $(self.mailto_input).hide();
        $(self.subject_input).hide();
        $(self.target_select).hide();
        $(self.nofollow_checkbox).hide();
        if (service === 'web') {
            $(self.href_input).show();
            $(self.target_select).show();
            $(self.nofollow_checkbox).show();
            self.href_input.focus();
        } else if (service === 'mail') {
            $(self.mailto_input).show();
            $(self.subject_input).show();
            self.mailto_input.focus();
        } else {
            throw new Error('Not a valid service to link to: ' + service);
        }
    },

    init_toolbar: function() {
        var self = this;
        self.toolbar = self.editable.parentNode.insertBefore(
            DIV({'class': 'rte-toolbar',
                 'style': 'display: block; opacity: 0'}),
            self.editable);
        self.toolbar.innerHTML = "\
            <a title='fett [Cmd/Strg+b]' rel='command' href='bold'>B</a>\
            <a title='kursiv [Cmd/Strg+i]' rel='command' href='italic'>I</a>\
            <a title='Zwischenüberschrift [Cmd/Strg+h]' rel='command' href='formatBlock/h3'>H3</a>\
            <a title='Link [Cmd/Strg+l]' rel='method' href='insert_link'>A</a>\
            <a title='Link entfernen [Cmd/Strg+u]' rel='command' href='unlink'>A</a>\
            <a title='Liste' rel='command' href='insertunorderedlist'>UL</a>\
            <a title='Formatierungen entfernen [Cmd/Strg+r]' rel='command' href='removeFormat'>PL</a>\
            <a title='Suchen [Cmd/Strg+F]' rel='method' href='show_find_dialog'>SEA</a>\
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
        if (isUndefinedOrNull(element)) {
            return;  // happens e.g. during initialization
        }
        if (element.nodeType == element.TEXT_NODE) {
            element = element.parentNode;
        }
        forEach(MochiKit.DOM.getElementsByTagAndClassName(
            'a', null, self.toolbar), function(action) {
            MochiKit.DOM.removeElementClass(action, 'active');
        });
        while(!isNull(element) && element != self.editable) {
            forEach(MochiKit.DOM.getElementsByTagAndClassName(
                'a', null, self.toolbar), function(action) {
                if (action.innerHTML == element.nodeName) {
                    MochiKit.DOM.addElementClass(action, 'active');
                    if (element.nodeName == 'H3' && action.innerHTML == 'H3') {
                      MochiKit.DOM.updateNodeAttributes(action, {'href': 'formatBlock/p'});
                      action.innerHTML = 'P';
                    }
                    if (element.nodeName != 'H3' && MochiKit.DOM.getNodeAttribute(action, 'href') == 'formatBlock/p') {
                      MochiKit.DOM.updateNodeAttributes(action, {'href': 'formatBlock/h3'});
                      action.innerHTML = 'H3';
                    }
                }
            });
            element = element.parentNode;
        }
    },

    relocate_toolbar: function(fast) {
        var self = this;
        var y = MochiKit.Style.getStyle(self.toolbar, 'top');
        var cursor_pos = self._get_cursor_position();
        if (cursor_pos && cursor_pos.y>0){
            y = cursor_pos.y;
        }

        var move = {
            duration: 0.5,
            mode: 'absolute',
            // By mode=absolute MochiKit means 'left' and 'top' CSS values.
            // Since they refer to the next parent with a specified 'position'
            // value, which is not necessarily self.block, we need to look at
            // the 'left' value instead of calling getElementPosition() in
            // order to retrieve the current x position (which is to be the
            // target x position, i.e. we don't want any horizontal motion).
            x: MochiKit.Style.getStyle(self.toolbar, 'left'),
            y: y
        };
        if (fast) {
            MochiKit.Style.setElementPosition(self.toolbar, move);
        } else {
            MochiKit.Visual.Move(self.toolbar, move);
        }
     },

    _get_cursor_position: function() {
        // Approach inspired by <https://stackoverflow.com/a/6847328>
        var self = this;
        var pos = {x:0,y:0};
        var selection = window.getSelection();
        if (! selection.rangeCount) {
            return null;
        }
        var range = selection.getRangeAt(0);
        var cloned_range = range.cloneRange();
        cloned_range.collapse(true);
        var cloned_collapsed_rect = cloned_range.getClientRects()[0];

        if (cloned_collapsed_rect) {
            var offset = $(".rte-toolbar").parent().offset();
            pos.y = cloned_collapsed_rect.top - offset.top;
            pos.x = cloned_collapsed_rect.left;
        } else if (range.startContainer.tagName == "P" &&
                 range.getClientRects().length==0){
            var html = '<span id="_find_cursor_position">&nbsp;</span>';
            document.execCommand('insertHTML', false, html);
            var tmp_el =  $('#_find_cursor_position');
            var tmp_pos = tmp_el.position();
            var par = tmp_el.parent();
            pos.y = tmp_pos.top;
            pos.x = tmp_pos.left;
            tmp_el.remove();
            if (par.children().length==0) {
                // Firefox requires an editable <p> to have _something_ inside
                // it, otherwise there's nowhere to place the cursor. By default
                // FF creates and deletes <br> for that purpose, so we do too.
                // Example FF behaviour:
                //  <p>asdf|</p> type 4xbackspace
                //  <p>|<br></p> type `asdf`, then enter
                //  <p>asdf</p><p><br></p> Note NO br in the first p!
                par.append('<br/>');
            }
        } else {
            return null;
        }
        return pos;
    },

    handle_click: function(event) {
        var self = this;
        self.error_msg.innerHTML = '';
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
            self.toolbar_command(action[0], action[1]);
        } else if (mode == 'method') {
            var method = argument;
            self[method]();
        }
    },

    check_dirty: function(key) {
        var self = this;
        if (self.dirty) {
            return true;
        }
        var movement_keys = ['KEY_ARROW_DOWN', 'KEY_ARROW_UP',
             'KEY_ARROW_LEFT', 'KEY_ARROW_RIGHT', 'KEY_CTRL', 'KEY_ALT',
             'KEY_SHIFT', 'KEY_PRINT_SCREEN', 'KEY_END',
             'KEY_HOME', 'KEY_PAGE_UP', 'KEY_PAGE_DOWN', 'KEY_WINDOWS_LEFT',
             'KEY_WINDOWS_RIGHT'];
        return !zeit.cms.in_array(key, movement_keys);
    },

    handle_keydown: function(event) {
        var self = this;

        self.dirty = self.check_dirty(event.key().string);

        var range = window.getSelection().getRangeAt(0);
        var container = range.commonAncestorContainer;
        // lastnode/firstnodee?
        var direction = null;
        if (event.key().string == 'KEY_ARROW_DOWN' &&
            ((container.nodeType == container.TEXT_NODE &&  // Last
            container.parentNode.nextSibling === null) ||   // node
            (container.tagName == 'P' &&            // Empty
            container.nextSibling === null)) &&     // node
            MochiKit.DOM.scrapeText(container).length == range.endOffset) {
            direction = 'nextSibling';
        } else if (
            event.key().string == 'KEY_ARROW_UP' &&
            ((container.nodeType == container.TEXT_NODE &&      // First
            container.parentNode.previousSibling === null) ||   // node
            (container.tagName == 'P' &&                // Empty
            container.previousSibling === null)) &&     // node
            range.startOffset === 0) {
            direction = 'previousSibling';
        } else if (
            event.key().string == 'KEY_ENTER') {
            setTimeout(function() {
                $('body').trigger('update-ads');
            }, 0);
        } else if (
            (event.key().string == 'KEY_BACKSPACE') ||
             event.key().string == 'KEY_DELETE') {
            // Don't remove empty paragraphs.
            if (container.tagName == 'P' &&
                container.previousSibling === null &&
                MochiKit.DOM.scrapeText(container).length === 0) {
                event.preventDefault();
            }
            setTimeout(function() {
                $('body').trigger('update-ads');
            }, 0);
        } else if (event.key().string == 'KEY_TAB') {
            // When the user presses the TAB key the next input will be focused.
            // The event system makes it impossible to detect if the new focus
            // is inside the editable or not. Thus we indicate that the editor
            // should be saved -- no matter what -- on the next blur event which
            // will be triggered after the key down event.
            self.unconditional_save_on_blur = true;
        }

        if (direction !== null) {
            if (self.activate_next_editable(direction)) {
                event.stop();
            }
        }
    },

    activate_next_editable: function(direction, wrap_around,  suppress_focus) {
        var self = this;
        var next_block = null;
        if (wrap_around) {
            var editables = $('#editable-body .block .editable');
            next_block = ((direction == 'nextSibling') ?
                          editables.first() : editables.last()
                         ).closest('.block')[0];
        } else {
            var block = self.block;
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
        }
        if (next_block === null) {
            return null;
        }
        log('Next block', next_block.id);
        // Note id as save may (or probably will) replace the element
        var next_block_id = next_block.id;
        self.save();
        var cursor_at_end = (direction == 'nextSibling') ? false : true;
        return new zeit.content.article.Editable(
            MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'editable', $('#' + next_block_id)[0]),
            cursor_at_end, suppress_focus);
    },

    handle_keyup: function(event) {
        var self = this;
        self.update_toolbar();
        self.relocate_toolbar();
        self.fix_html();
    },

    handle_paste: function() {
        var self = this;
        // Get rid of obsolete mark-up when pasting content from third party
        // software. Ensure that content is processed AFTER it has been pasted.
        setTimeout(function() {
            self.fix_html();
            $(self.editable).children().has('style').remove();
            $(self.editable).find('a').attr('target', '_blank');

            var range = window.getSelection().getRangeAt(0);
            var selection_node = range.startContainer;
            var selection_offset = range.startOffset;
            $(self.editable).find('*:not(:has(*))').each(function() {
                var text_node = this.firstChild;
                if (text_node && text_node.nodeType == text_node.TEXT_NODE) {
                    text_node.textContent = text_node.textContent.replace(
                            /[\u2028]/, '');
                }
            });
            self._set_selection_offset(selection_node, selection_offset);
        }, 0);
    },

    fix_html: function() {
        var self = this;
        self.editable.normalize();
        forEach(
            MochiKit.DOM.getElementsByTagAndClassName(
                null, null, self.editable),
            function(element) {
                if ((element.nodeName !== 'A') &&
                    !$(element).hasClass('colorbox')) {
                    element.removeAttribute('class');
                }
                element.removeAttribute('style');
                var swapped = null;
                // Yeah, I luv it!
                if (element.nodeName === 'EM') {
                    swapped = zeit.content.article.html.change_tag(element, 'I');
                } else if (element.nodeName === 'STRONG') {
                    swapped = zeit.content.article.html.change_tag(element, 'B');
                }
                if (element === self.initial_selection_node) {
                    self.initial_selection_node = swapped;
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

    autosave: function() {
        var self = this;
        if (zeit.cms.request_lock.locked) {
            log('Skipping autosave due to running other request');
            return;
        }
        if (!self.dirty) {
            log('Skipping autosave: no changes');
            return;
        }
        log('Autosaving', self.block.id);
        zeit.cms.with_lock(function() {
            var d = self.persist('/@@autosave_text');
            return d;
        });
    },

    save: function(supress_reload) {
        var self = this;
        log('Saving', self.block.id);
        window.clearInterval(self.autosave_timer);
        MochiKit.DOM.addElementClass(self.block, 'busy');
        return zeit.cms.with_lock(function() {
            while (self.events.length) {
               MochiKit.Signal.disconnect(self.events.pop());
            }
            self.link_input.dropable.destroy();
            log('disconnected event handlers');
            var ident = MochiKit.Signal.connect(
                zeit.edit.editor, 'after-reload', function() {
                    MochiKit.Signal.disconnect(ident);
                    log('Release lock', self.block.id);
                    self.editor_active_lock.release();
            });
            var d;
            if (self.dirty) {
                d = self.persist('/@@save_text');
            } else {
                log('Skipping save: no changes');
                d = new MochiKit.Async.Deferred();
                d.callback();
            }
            if (!supress_reload) {
                d.addCallback(function(result) {
                    MochiKit.Signal.signal(
                        zeit.edit.editor, 'reload', self.block.id,
                        $('#editable-body').attr('cms:url') + '/@@slice?'
                        + MochiKit.Base.queryString({
                            'start': self.edited_paragraphs[0],
                            'end': self.edited_paragraphs[
                                self.edited_paragraphs.length-1]
                        }));
                    return result;
                });
            }
            return d;
        });
    },

    persist: function(url) {
        var self = this;
        // until now, the editor can only be contained in an
        // editable-body.
        url = $('#editable-body').attr('cms:url') + url;
        var data = {paragraphs: self.edited_paragraphs,
                    text: self.get_text_list()};
        var d;
        data = MochiKit.Base.serializeJSON(data);
        d = MochiKit.Async.doXHR(url, {
            method: 'POST',
            sendContent: data});
        d.addCallback(function(result) {
            result = MochiKit.Async.evalJSONRequest(result);
            self.edited_paragraphs = result['data']['new_ids'];
            self.block.block_ids = self.edited_paragraphs;
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
        return d;
    },

    get_selected_container: function() {
        if (!window.getSelection().rangeCount) {
            return null;
        }
        var container;
        var range = window.getSelection().getRangeAt(0);
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
            var range = window.getSelection().getRangeAt(0);
            range.setStartBefore(element);
            range.setEndAfter(element);
        } catch(e) {
            if (window.console) {
                console.log(e);
            }
        }
    },

    insert_link: function() {
        $(".link_input input").val('');
        var self = this;
        if (self.locked) {
            return;
        }
        var container = self.get_selected_container();
        if (container.nodeName == 'A') {
            self.insert_link_node = $(container);
        } else {
            self.insert_link_node = $(container).parents('a');
        }
        var service = 'web';
        var href = '';
        var target = '';
        var nofollow = false;
        var mailto = '';
        var subject = '';
        if (self.insert_link_node.length) {
            self.created_link_node = false;
            href = self.insert_link_node.attr('href') || '';
            var prefix = 'mailto:';
            if (href.slice(0, prefix.length) === prefix) {
                service = 'mail';
                var q_index = href.indexOf('?');
                if (q_index == -1) {
                    mailto = href.slice(prefix.length);
                } else {
                    mailto = href.slice(prefix.length, q_index);
                    var q = '?subject=';
                    q_index = href.indexOf(q);
                    if (q_index != -1) {
                        subject = decodeURI(href.slice(q_index + q.length));
                    }
                }
                href = '';
            }
            if (self.insert_link_node.hasClass('colorbox')) {
                target = 'colorbox';
            } else {
                target = self.insert_link_node.attr('target') || '';
            }
            nofollow = self.insert_link_node.attr('rel') == 'nofollow';
        } else {
            self.toolbar_command('createLink', '#article-editor-create-link');
            self.created_link_node = true;
            self.insert_link_node = $(
                'a[href="#article-editor-create-link"]', self.editable);
        }
        self.insert_link_node.addClass('link-edit');
        if (!self.created_link_node) {
            $(self.href_input).val(href);
            $(self.target_select).val(target);
            $(self.nofollow_checkbox).prop('checked', nofollow);
            $(self.mailto_input).val(mailto);
            $(self.subject_input).val(subject);
        }
        var line_height = parseInt(
            self.insert_link_node.css('line-height').replace('px', ''));
        var position = self.insert_link_node.position();
        $(self.link_input).css('top',
            (parseInt(position.top) + line_height) + 'px');
        $(self.link_input).removeClass('hidden');
        self.linkbar_switch_service(service);
        self.locked = true;
    },

    insert_link_ok: function() {
        var self = this;
        var service = self.service_select.value;
        var href = '';
        var target = null;
        var nofollow = false;
        if (service === 'web') {
            var uri = new Uri($(self.href_input).val());
            if (invalidHosts.some(v => uri.toString().includes(v))) {
                self.error_msg.innerHTML = '<span style="color:red;display:block;">Kein gültiges Linkziel! ZEIT Inhalte müssen nach www.zeit.de verlinken.</span>';
                return;
            }
            if (uri.host() == uri.toString() && !uri.host().includes('.')) {
                self.error_msg.innerHTML = '<span style="color:red;display:block;">Kein gültiges Linkziel! Wurde Fließtext als Verlinkungsziel eingegeben?</span>';
                return;
            }
            if (!uri.protocol() && uri.host())
                uri.protocol('http');
            href = uri.toString();
            target = $(self.target_select).val();
            nofollow = $(self.nofollow_checkbox).prop('checked');
        } else {
            var mailto = $(self.mailto_input).val();
            var subject = $(self.subject_input).val();
            href = 'mailto:' + mailto;
            if (subject) {
                href = href + '?subject=' + encodeURI(subject);
            }
        }
        self.insert_link_node.attr('href', href);
        if (target === 'colorbox') {
            self.insert_link_node.attr('target', null);
            self.insert_link_node.addClass('colorbox');
        } else {
            self.insert_link_node.removeClass('colorbox');
            if (target) {
                self.insert_link_node.attr('target', target);
            } else {
                self.insert_link_node.attr('target', null);
            }
        }
        if (nofollow) {
            self.insert_link_node.attr('rel', 'nofollow');
        } else {
            self.insert_link_node.attr('rel', null);
        }
        self.dirty = true;
        self.select_container(self.insert_link_node[0]);
        self.insert_link_node.removeClass('link-edit');
        self._insert_link_finish();
    },

    insert_link_cancel: function() {
        var self = this;
        self.select_container(self.insert_link_node[0]);
        if (self.created_link_node) {
            self.insert_link_node.each(function(i, element) {
                element = $(element);
                element.contents().insertBefore(element);
                element.remove();
            });
        }
        self._insert_link_finish();
    },

    _insert_link_finish: function() {
        var self = this;
        $(self.link_input).addClass('hidden');
        self.insert_link_node = null;
        self.locked = false;
        self.editable.focus();
    },

    toolbar_command: function(command, option, refocus) {
        var self = this;
        self.dirty = true;
        return self.command(command, option, refocus);
    },

    command: function(command, option, refocus) {
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
        if (typeof refocus === 'undefined' || refocus === true) {
            self.editable.focus();
        }
        self.update_toolbar();
    },

    init_shortcuts: function() {
        var self = this;
        self.events.push(MochiKit.Signal.connect(
            $("#editable-body")[0], 'onkeydown', function(e) {
                var modifier = e.modifier();
                if (! (modifier['ctrl'] || modifier['meta'])) {
                    return;
                }

                var key = e.key()['string'];
                if (key == 'KEY_B') {
                    e.preventDefault();
                    self.toolbar_command('bold');
                } else if (key == 'KEY_F' && modifier['shift']) {
                    e.preventDefault();
                    self.show_find_dialog();
                } else if (key == 'KEY_I') {
                    e.preventDefault();
                    self.toolbar_command('italic');
                } else if (key == 'KEY_H') {
                    e.preventDefault();
                    self.toolbar_command('formatBlock', '<h3>');
                } else if (key == 'KEY_L') {
                    e.preventDefault();
                    self['insert_link']();
                } else if (key == 'KEY_U') {
                    e.preventDefault();
                    self.toolbar_command('unlink');
                } else if (key == 'KEY_R') {
                    e.preventDefault();
                    self.toolbar_command('removeFormat');
                } else if (key == 'KEY_A') {
                    if (self.get_selected_container().nodeName != 'INPUT') {
                      e.preventDefault();
                      self.selectall();
                    }
                }
        }));
    },

    selectall: function() {
      var self = this;
      $('#editable-body .block.type-p p, #editable-body .block.type-ul p, #editable-body .block.type-p li, #editable-body .block.type-p h3, #editable-body .block.type-intertitle h3, #editable-body .block.type-ul li, #editable-body .fieldname-custom_caption textarea, #form-article-content-head textarea').each(function(index, value) {
        var content = $(this).text();
        if(content !='') {
          var range = document.createRange();
          range.selectNodeContents(this);
          var sel = window.getSelection();
          sel.addRange(range);
          $('#editable-body textarea').css({'background':'#b4d5ff'});
          $('#form-article-content-head textarea').css({'background':'#b4d5ff'});
        }
      });
    },

    show_find_dialog: function() {
        var self = this;
        var dialog = new zeit.content.article.FindDialog(self);
        dialog.show();
    },

    find_and_select_next: function(
        text, direction, case_sensitive, start_selection) {
        var self = this;
        return zeit.content.article.find_next(
            self.editable, text, direction, case_sensitive, start_selection);
    },

    replace_text: function(node, start, end, replacement) {
        var self = this;
        self.dirty = true;
        node.textContent = (node.textContent.substring(0, start)
                            + replacement
                            + node.textContent.substring(end));
    },

    replace_all: function(find, replace) {
        var self = this;
        self.dirty = true;  // XXX Is this really correct?
        var d = self.save(/*supress_reload=*/true);
        d.addCallback(function() {
            return zeit.edit.makeJSONRequest(
                $('#editable-body').attr('cms:url') + '/@@replace-all',
            {'find': find, 'replace': replace});
        });
        return d;
    }

});


zeit.content.article.AppendParagraph = zeit.edit.LoadAndReload.extend({

    construct: function(context_element) {
        var self = this;
        $('.create-paragraph').first().remove();
        var ident = MochiKit.Signal.connect(
            zeit.edit.editor, 'after-reload', function() {
                MochiKit.Signal.disconnect(ident);
                var new_p = $('#editable-body .block.type-p').last()[0];
                new zeit.content.article.Editable(new_p.firstChild, true);
            });
        arguments.callee.$.construct.call(self, context_element);
    }

});
}(jQuery));
