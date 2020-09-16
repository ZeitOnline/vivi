zeit.cms.ParentChildDropDown = gocept.Class.extend({

    construct: function(parent, child, update_url) {
        var self = this;
        self.parent = parent;
        self.child = child;
        self.update_url = update_url;

        // XXX The following selector makes sense only in part of the forms
        // used by vivi. In particular, it doesn't work for the subpage form
        // of addcentral. When we implemented hiding the child drop-down to
        // fix #10664, the resulting difference in behaviour between
        // addcentral and, e.g., an article's edit form happened to be what
        // was requested, so we left it at that.
        self.child_field = jQuery(child).closest('.field');

        MochiKit.Signal.connect(parent, 'onchange', self, self.update);
        self.update();
    },

    destroy: function() {
        var self = this;
        MochiKit.Signal.disconnectAllTo(self, self.update);
    },

    update: function(event) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            self.update_url, {parent_token: self.parent.value});
        d.addCallback(function(result) {
            var data = MochiKit.Async.evalJSONRequest(result);

            if (data.length == 0) {
                self.child_field.hide();
            } else {
                self.child_field.show();
            }

            var selected = self.child.value;
            self.child.options.length = 1;
            forEach(data, function(new_option) {
                var label = new_option[0];
                var value = new_option[1];
                var option = new Option(label, value);
                if (value == selected) {
                    option.selected = true;
                }
                self.child.options[self.child.options.length] = option;
            });
        });
    }
});


zeit.cms.MultiGenerationDropDown = zeit.cms.ParentChildDropDown.extend({

    construct: function(parent, child, grandchild, update_url) {
        var self = this;
        self.parent = parent;
        self.child = child;
        self.grandchild = grandchild;
        self.update_url = update_url;

        // XXX The following selector makes sense only in part of the forms
        // used by vivi. In particular, it doesn't work for the subpage form
        // of addcentral. When we implemented hiding the child drop-down to
        // fix #10664, the resulting difference in behaviour between
        // addcentral and, e.g., an article's edit form happened to be what
        // was requested, so we left it at that.
        self.child_field = jQuery(child).closest('.field');
        self.grandchild_field = jQuery(grandchild).closest('.field');

        MochiKit.Signal.connect(parent, 'onchange', self, self.update);
        self.update();
    },

    update: function(event) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            self.update_url, {parent_token: self.parent.value});
        d.addCallback(function(result) {
            var data = MochiKit.Async.evalJSONRequest(result);

            if (data.length == 0) {
                self.child_field.hide();
                self.grandchild_field.hide();
            } else {
                self.child_field.show();
            }

            var selected = self.child.value;
            self.child.options.length = 1;
            forEach(data, function(new_option) {
                var label = new_option[0];
                var value = new_option[1];
                var option = new Option(label, value);
                if (value == selected) {
                    option.selected = true;
                }
                self.child.options[self.child.options.length] = option;
            });
        });
    }
});


zeit.cms.parent_child_dropdown = {};

zeit.cms.configure_parent_child = function(prefix, parent, child, update_url) {
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.';
    }
    parent = $(prefix + parent);
    child = $(prefix + child);

    if (isNull(parent) || isNull(child)) {
        return;
    }
    if (!isUndefinedOrNull(zeit.cms.parent_child_dropdown[parent.name])) {
        zeit.cms.parent_child_dropdown[parent.name].destroy();
    }
    var path = window.location.pathname.split('/').slice(0, -1);
    path.push(update_url);
    path = path.join('/');
    zeit.cms.parent_child_dropdown[parent.name] =
        new zeit.cms.ParentChildDropDown(parent, child, path);
};


zeit.cms.configure_multigeneration = function(prefix, parent, child, grandchild, update_url) {
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.';
    }
    parent = $(prefix + parent);
    child = $(prefix + child);
    grandchild = $(prefix + grandchild);

    if (isNull(parent) || isNull(child) || isNull(grandchild)) {
        return;
    }
    if (!isUndefinedOrNull(zeit.cms.parent_child_dropdown[parent.name])) {
        zeit.cms.parent_child_dropdown[parent.name].destroy();
    }
    var path = window.location.pathname.split('/').slice(0, -1);
    path.push(update_url);
    path = path.join('/');
    zeit.cms.parent_child_dropdown[parent.name] =
        new zeit.cms.MultiGenerationDropDown(parent, child, grandchild, path);
};


zeit.cms.configure_ressort_dropdown = function(prefix) {
    zeit.cms.configure_parent_child(
        prefix, 'ressort', 'sub_ressort', '@@subnavigationupdater.json');
};


zeit.cms.configure_channel_dropdowns = function(
        prefix, field, parent_index, child_index) {
    // XXX Rather ugly API to support usage in both z.c.article and z.c.cp.
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.';
    }
    var parents = jQuery(
        '[id^="' + prefix + field + '"][id$="combination_' + parent_index + '"]'
        );

    jQuery.each(parents, function(index, value) {
        zeit.cms.configure_parent_child(
            prefix, field + '.' + index + '..combination_' + parent_index,
            field + '.' + index + '..combination_' + child_index,
            '@@channelupdater.json');
    });
};

/**
 * The item currently in display belongs to the <select>, not the <option>,
 * but since CSS doesn't have neither a parent selector nor a
 * 'attribute != value' comparison, we need to use JS for this.
 */
zeit.cms.style_dropdowns = function(container) {
    jQuery('.required option[value = ""]', container).parent().css(
        'color', 'red');
    jQuery('.required option[value = ""]', container).css('color', 'red');
    jQuery('.required option[value != ""]', container).css('color', 'black');
};


MochiKit.Signal.connect(window, 'onload', function(event) {
    zeit.cms.configure_ressort_dropdown();
    zeit.cms.configure_channel_dropdowns('form.', 'channels', '00', '01');
    zeit.cms.style_dropdowns();
});


jQuery(document).bind('fragment-ready', function(event) {
    zeit.cms.style_dropdowns(event.__target);
});
