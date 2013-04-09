// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt


zeit.cms.ObjectReferenceWidget = gocept.Class.extend({
    // Widget for referencing one object via unique id.
    //
    // This is also thought to be used multiple times in one formlib field,
    // e.g. for Tuple fields.

    construct: function(element, default_browsing_url, type_filter,
                        add_view, show_popup, parent_component) {
        var self = this;
        self.events = [];

        self.element = $(element);
        self.default_browsing_url = default_browsing_url;
        self.type_filter = type_filter;
        self.add_view = add_view;
        self.input = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', 'object-reference', self.element);
        self.input.object_reference_widget = self;
        self.changed = false;
        self.parent_component = parent_component;

        self.droppable = new zeit.cms.ContentDroppable(self.element, {
            accept: ['content-drag-pane', 'uniqueId'],
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                    self.handleDrop(element);
            }
        });

        self.events.push(
            MochiKit.Signal.connect(
                element, 'onclick', self, self.handleClick));
        self.events.push(
            MochiKit.Signal.connect(self.input, 'onchange', function(event) {
                self.changed = true;
        }));

        self.tooltip = new zeit.cms.ToolTip(element, function() {
            return self.getToolTipURL();
        });

        var addbutton = MochiKit.DOM.getFirstElementByTagAndClassName(
            'input', 'add-object', self.element);
        if (isUndefinedOrNull(self.add_view)) {
            MochiKit.DOM.hideElement(addbutton);
        } else {
            MochiKit.DOM.addElementClass(self.element, 'add-button');
        }

        // self saves a click and shows the object browser initially
        if (show_popup && isUndefinedOrNull(parent_component)) {
            // Defer popup loading until page is completed to allow others to
            // set a unique id.
            self.events.push(MochiKit.Signal.connect(
                window, 'onload', function() {
                    if (!self.input.value) {
                        self.browseObjects();
                    }
            }));
        }

        if (!isUndefinedOrNull(parent_component)) {
            self.events.push(MochiKit.Signal.connect(
                parent_component, 'close', self, self.destruct));
        }
    },

    destruct: function() {
        var self = this;
        self.tooltip.destruct();
        self.droppable.destroy();
        while (self.events.length) {
            MochiKit.Signal.disconnect(self.events.pop());
        }
    },

    handleDrop: function(element) {
        this.selectObject(element.uniqueId);
    },

    handleClick: function(event) {
        var target = event.target();
        var action = null;
        if (target.nodeName == 'INPUT' && target.type == 'button') {
            event.stop();
            action = target.getAttribute('name');
            var func = MochiKit.Base.bind(action, this);
            func(event);
        }
    },

    handleObjectSelected: function(unique_id, element) {
        var self = this;
        if (isUndefinedOrNull(element)) {
            self.lightbox.close();
            self.lightbox = null;
            self.selectObject(unique_id);
        } else {
            MochiKit.Style.makePositioned(element);
            var pos = MochiKit.Style.getElementPosition(element);
            var cloned_element = element.cloneNode(true);
            jQuery('body').append(cloned_element);
            MochiKit.Style.setElementPosition(cloned_element, pos);
            MochiKit.Style.makeClipping(cloned_element);
            self.lightbox.close();
            self.lightbox = null;
            // Visual candy
            pos = MochiKit.Style.getElementPosition(self.input);
            var move = new MochiKit.Visual.Move(cloned_element, {
                mode: 'absolute',
                sync: true,
                x: pos.x,
                y: pos.y
            });
            var shrink = MochiKit.Visual.Scale(cloned_element, 0, {
                sync: true
            });
            new MochiKit.Visual.Parallel([move, shrink], {
                afterFinish: function() {
                    self.selectObject(unique_id);
                    cloned_element.parentNode.removeChild(cloned_element);
                }
            });
        }
    },

    browseObjects: function(event) {
        var self = this;
        if (zeit.cms.activate_objectbrowser()) {
            return;
        }
        var url = self.default_browsing_url;
        if (url.indexOf('@@') == -1) {
            url += '/@@get_object_browser';
        }
        url += '?' + MochiKit.Base.queryString(
            {type_filter: this.type_filter});
        self.lightbox = new zeit.cms.LightboxForm(url, jQuery('body')[0]);
        self.lightbox.events.push(MochiKit.Signal.connect(
            self.lightbox, 'zeit.cms.ObjectReferenceWidget.selected',
            self, self.handleObjectSelected));

    },

    addObject: function(event) {
        var self = this;
        var url = self.default_browsing_url + '/@@' + self.add_view;
        self.lightbox = new zeit.cms.ObjectAddForm(url, jQuery('body')[0]);
        self.lightbox.events.push(MochiKit.Signal.connect(
            self.lightbox, 'zeit.cms.ObjectReferenceWidget.selected',
            self, self.handleObjectSelected));
    },

    showReferencedObject: function(event) {
        var new_window = event.modifier().any;
        var unique_id = this.getObject();
        if (!unique_id) {
            return;
        }
        // XXX i18n
        var msg = 'Your changes have not been saved, yet. Continue?';
        if (this.changed && !confirm(msg)) {
            return;
        }
        var qs = MochiKit.Base.queryString({
            'unique_id': unique_id});
        var url = application_url + '/redirect_to?' + qs;
        if (new_window) {
            window.open(url);
        } else {
            window.location = url;
        }
    },

    selectObject: function(unique_id) {
        var self = this;
        self.changed = true;
        self.input.value = unique_id;
        self.input.focus();
        MochiKit.Signal.signal(self.input, 'onchange', {target: self.input});
    },

    getObject: function() {
        return this.input.value;
    },

    getToolTipURL: function() {
        var othis = this;
        var unique_id = othis.getObject();
        if (!unique_id) {
            return null;
        }
        var qs = MochiKit.Base.queryString({
            'unique_id': unique_id,
            'view': '@@drag-pane.html'});
        var url = application_url + '/redirect_to?' + qs;
        return url;
    }
});


zeit.cms.ObjectReferenceSequenceWidget = gocept.Class.extend({

    construct: function(widget_id, parent_component) {
        var self = this;
        self.widget_id = widget_id;
        self.element = $(widget_id);
        self.parent_component = parent_component;
        self.form = MochiKit.DOM.getFirstParentByTagAndClassName(
            self.element, 'form');
        var droppable_element = MochiKit.Selector.findChildElements(
            self.element,
            ['> table.sequencewidget > tbody > tr:last-child'])[0];
        self.droppable = new zeit.cms.ContentDroppable(droppable_element, {
            accept: ['content-drag-pane', 'uniqueId'],
            activeclass: 'droppable-active',
            hoverclass: 'hover-content',
            ondrop: function(element, last_active_element, event) {
                    self.handleDrop(element);
            }
        });
        self.setObject();
        if (!isUndefinedOrNull(parent_component)) {
            self.events.push(MochiKit.Signal.connect(
                parent_component, 'close', self, self.destruct));
        }
    },

    destruct: function() {
        var self = this;
        self.droppable.destroy();
    },

    handleDrop: function(element) {
        // On drop we create a new field
        zeit.cms.setCookie(this.widget_id, element.uniqueId);
        var add_button = this.form[this.widget_id + '.add'];
        add_button.click();
    },

    setObject: function() {
        var unique_id =  zeit.cms.getCookie(this.widget_id);
        if (!unique_id) {
            return;
        }
        var count = Number(this.form[this.widget_id + '.count'].value);
        if (count <= 0) {
            return;
        }
        var field_nr = count - 1;

        var input = this.form[this.widget_id + '.' + field_nr + '.'];
        var widget = input.object_reference_widget;
        if (widget.getObject()) {
            return;
        }
        widget.selectObject(unique_id);
        zeit.cms.setCookie(this.widget_id, '');
    }

});


zeit.cms.ObjectAddForm = zeit.cms.LightboxForm.extend({
    process_post_result: function(result) {
        var self = this;

        if (self.has_errors()) {
            return result;
        }

        // enable the visual effect to work
        MochiKit.DOM.removeElementClass(self.container, 'busy');

        var node = MochiKit.DOM.getFirstElementByTagAndClassName(
            'span', 'result', self.container);
        var unique_id = node.textContent;
        MochiKit.Signal.signal(
            self, 'zeit.cms.ObjectReferenceWidget.selected',
            unique_id, node);
        return null;
    }

});
