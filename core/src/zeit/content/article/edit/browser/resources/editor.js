(function($){

zeit.cms.declare_namespace('zeit.content.article');

zeit.cms.in_article_editor = function() {
    return Boolean(jQuery('.article-editor-inner').length);
};


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    // set up "to top" links
    MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
        $('.editable-area > .block-inner').append(
            '<div class="totop"><span class="totopclick">↑</span></div>');
    });
});


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (! zeit.cms.in_article_editor()) {
        return;
    }

    // Initialize module library
    zeit.edit.library.create(
        'article-modules', context_url + '/editable-body', 'Artikel');

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

    zeit.edit.drop.registerContentHandler({
        accept: ['type-image',
                 'type-gallery', 'type-video',
                 'type-infobox', 'type-portraitbox'],
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

        forEach($$('#cp-content .action-block-sorter'), function(element) {
            element.body_sorter =
                new zeit.edit.sortable.BlockSorter(element.id);
        });
});
}());


zeit.content.article.Editable = gocept.Class.extend({
    // Inline editing module

    autosave_interval: 10,
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
            self.initial_paragraph = MochiKit.Selector.findChildElements(
                block, ['.editable > *'])[0];
            self.editable = self.merge(block);
            self.block = MochiKit.DOM.getFirstParentByTagAndClassName(
                self.editable, null, 'block');
            log('Editable block', self.block.id);
            self.editable.removeAttribute('cms:cp-module');
            self.editable.contentEditable = true;
            self.editable.editable = self; // make instance available for tests
            self.command('styleWithCSS', false, false);
            MochiKit.DOM.addElementClass(self.block, 'editing');

            // Catche the blur-signal in the capturing-phase!
            // In case you use the toolbar, the editing-mode won't be stopped.
            var handle_blur = function(e) {
                var clicked_on_block =
                    MochiKit.DOM.getFirstParentByTagAndClassName(
                       e.explicitOriginalTarget, 'div', 'block');
                var is_in_block = (clicked_on_block == self.block);
                log("Blur while editing:", is_in_block, self.block_id);
                if (is_in_block || self.locked) {
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
            $('.editable').bind('paste', function() {
                self.handle_paste();
            });
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
                    $('#fulltext').focus();
                    $('#fulltext').blur();
                    self.save(/*no_reload=*/true);
                }));
            self.fix_html();
            $('body').trigger('update-ads');
            self.place_cursor(self.initial_paragraph, place_cursor_at_end);
            self.editable.focus();
            self.init_linkbar();
            self.init_toolbar();
            self.shortcuts();
            self.relocate_toolbar(true);
            self.events.push(MochiKit.Signal.connect(
                window, 'before-content-drag', function() {
                    if (!self.locked) {
                        self.save();
                    }
                }));
        });
        d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
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
            // We need to avoid placing the cursor inside a br element since
            // it is not possible to type in there and trying to do so leads
            // to funny effects (#12266). The br element is put in this place
            // in an effort to keep empty paragraphs editable while editing.
            if (text_node[direction].nodeName === 'BR') {
                break;
            }
            text_node = text_node[direction];
        }
        var offset = 0;
        if (place_cursor_at_end &&
            text_node.nodeType == text_node.TEXT_NODE)  {
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
            jQuery(paragraph).next('.landing-zone').remove();
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
        self.link_input = self.editable.parentNode.insertBefore(
            DIV({'class': 'link_input hidden'},
                self.href_input,
                self.mailto_input,
                self.subject_input,
                self.service_select,
                self.target_select,
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
        if (service === 'web') {
            $(self.href_input).show();
            $(self.target_select).show();
            self.href_input.focus();
        } else if (service === 'mail') {
            $(self.mailto_input).show();
            $(self.subject_input).show();
            self.mailto_input.focus();
        } else {
            throw 'Not a valid service to link to: ' + service;
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
            if (par.children().length==0){
                // allow empty paragraphs while editing
                document.execCommand('insertHTML', false,'<br type="_moz" />');
            }
        } else {
            return null;
        }
        return pos;
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
            cursor_at_end = true;
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
                        'div', 'editable', $('#' + next_block_id)[0]),
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

    handle_paste: function() {
        var self = this;
        // Get rid of obsolete mark-up when pasting content from third party
        // software. Ensure that content is processed AFTER it has been pasted.
        setTimeout(function() {
            self.fix_html();
            $(self.editable).children().has('style').remove();
            $('a', self.editable).attr('target', '_blank');
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
                // Yeah, I luv it!
                if (element.nodeName === 'EM') {
                    zeit.content.article.html.change_tag(element, 'I');
                } else if (element.nodeName === 'STRONG') {
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

    autosave: function() {
        var self = this;
        if (zeit.cms.request_lock.locked) {
            log('Skipping autosave due to running other request');
            return;
        }
        log('Autosaving', self.block_id);
        zeit.cms.with_lock(function() {
            var url = $('#editable-body').attr('cms:url') +
                '/@@autosave_text';
            var data = {paragraphs: self.edited_paragraphs,
                        text: self.get_text_list()};
            data = MochiKit.Base.serializeJSON(data);
            var d = MochiKit.Async.doXHR(url, {
                method: 'POST',
                sendContent: data});
            d.addCallback(function(result) {
                result = MochiKit.Async.evalJSONRequest(result);
                self.edited_paragraphs = result['data']['new_ids'];
                self.block.block_ids = self.edited_paragraphs;
            });
            d.addErrback(function(err) {zeit.cms.log_error(err); return err;});
            return d;
        });
    },

    save: function(no_reload) {
        var self = this;
        log('Saving', self.block_id);
        MochiKit.DOM.addElementClass(self.block, 'busy');
        window.clearInterval(self.autosave_timer);
        zeit.cms.with_lock(function() {
            var d;
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
            var url = $('#editable-body').attr('cms:url') + '/@@save_text';
            var data = {paragraphs: self.edited_paragraphs,
                        text: self.get_text_list()};
            if (no_reload) {
                data = MochiKit.Base.serializeJSON(data);
                d = MochiKit.Async.doXHR(url, {
                    method: 'POST',
                    sendContent: data});
            } else {
                d = zeit.edit._locked_makeJSONRequest(url, data);
            }
            return d;
        });
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
        $(".link_input input").val('');
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
        var service = 'web';
        var href = '';
        var target = '';
        var mailto = '';
        var subject = '';
        if (self.insert_link_node) {
            href = self.insert_link_node.getAttribute('href') || '';
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
            if (MochiKit.DOM.hasElementClass(
                self.insert_link_node, 'colorbox')) {
                target = 'colorbox';
            } else {
                target = self.insert_link_node.getAttribute('target') || '';
            }
        } else {
            self.command('createLink', '#article-editor-create-link');
            self.insert_link_node = $(
                'a[href="#article-editor-create-link"]', self.editable)[0];
            self.insert_link_node._just_created = true;
        }
        $(self.insert_link_node).addClass('link-edit');
        if (!self.insert_link_node._just_created) {
            $(self.href_input).val(href);
            $(self.target_select).val(target);
            $(self.mailto_input).val(mailto);
            $(self.subject_input).val(subject);
        }
        var line_height = parseInt(
            $(self.insert_link_node).css('line-height').replace('px', ''));
        var position = $(self.insert_link_node).position();
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
        if (service === 'web') {
            href = $(self.href_input).val();
            target = $(self.target_select).val();
        } else {
            var mailto = $(self.mailto_input).val();
            var subject = $(self.subject_input).val();
            href = 'mailto:' + mailto;
            if (subject) {
                href = href + '?subject=' + encodeURI(subject);
            }
        }
        self.insert_link_node.href = href;
        if (target === 'colorbox') {
            self.insert_link_node.removeAttribute('target');
            jQuery(self.insert_link_node).addClass('colorbox');
        } else {
            jQuery(self.insert_link_node).removeClass('colorbox');
            if (target) {
                self.insert_link_node.target = target;
            } else {
                self.insert_link_node.removeAttribute('target');
            }
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
            $(self.insert_link_node).remove();
        }
        self._insert_link_finish();
    },

    _insert_link_finish: function() {
        var self = this;
        $(self.link_input).addClass('hidden');
        $(self.insert_link_node).removeClass('link-edit');
        self.insert_link_node._just_created = false;
        self.insert_link_node = null;
        self.locked = false;
        self.editable.focus();
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

    shortcuts: function() {
      var self = this;
      $("#editable-body").keydown(function(e) {
        if (e.ctrlKey || e.metaKey) {
            if (e.which == 66) {
                e.preventDefault();
                self.command('bold');
            } else if (e.which == 73) {
                e.preventDefault();
                self.command('italic');
            } else if (e.which == 72) {
                e.preventDefault();
                self.command('formatBlock', '<h3>');
            } else if (e.which == 76) {
                e.preventDefault();
                self['insert_link']();
            } else if (e.which == 85) {
                e.preventDefault();
                self.command('unlink');
            } else if (e.which == 82) {
                e.preventDefault();
                self.command('removeFormat');
            } else if (e.which == 65) {
                if (self.get_selected_container().nodeName != 'INPUT') {
                  e.preventDefault();
                  self.selectall();
                }
            }
        }
    });
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
