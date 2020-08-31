zeit.cms.MasterSlaveDropDown = gocept.Class.extend({

    construct: function(master, slave, update_url) {
        var self = this;
        self.master = master;
        self.slave = slave;
        self.update_url = update_url;

        // XXX The following selector makes sense only in part of the forms
        // used by vivi. In particular, it doesn't work for the subpage form
        // of addcentral. When we implemented hiding the slave drop-down to
        // fix #10664, the resulting difference in behaviour between
        // addcentral and, e.g., an article's edit form happened to be what
        // was requested, so we left it at that.
        self.slave_field = jQuery(slave).closest('.field');

        MochiKit.Signal.connect(master, 'onchange', self, self.update);
        self.update();
    },

    destroy: function() {
        var self = this;
        MochiKit.Signal.disconnectAllTo(self, self.update);
    },

    update: function(event) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            self.update_url, {master_token: self.master.value});
        d.addCallback(function(result) {
            var data = MochiKit.Async.evalJSONRequest(result);

            if (data.length == 0) {
                self.slave_field.hide();
            } else {
                self.slave_field.show();
            }

            var selected = self.slave.value;
            self.slave.options.length = 1;
            forEach(data, function(new_option) {
                var label = new_option[0];
                var value = new_option[1];
                var option = new Option(label, value);
                if (value == selected) {
                    option.selected = true;
                }
                self.slave.options[self.slave.options.length] = option;
            });
        });
    }
});


zeit.cms.MultiGenerationDropDown = gocept.Class.extend({

    construct: function(grandparent, parent, child, update_url) {
        var self = this;
        self.grandparent = grandparent;
        self.parent = parent;
        self.child = child;
        self.update_url = update_url;

        // XXX The following selector makes sense only in part of the forms
        // used by vivi. In particular, it doesn't work for the subpage form
        // of addcentral. When we implemented hiding the slave drop-down to
        // fix #10664, the resulting difference in behaviour between
        // addcentral and, e.g., an article's edit form happened to be what
        // was requested, so we left it at that.
        self.parent_field = jQuery(parent).closest('.field');
        self.child_field = jQuery(child).closest('.field');

        MochiKit.Signal.connect(grandparent, 'onchange', self, self.update);
        self.update();
    },

    destroy: function() {
        var self = this;
        MochiKit.Signal.disconnectAllTo(self, self.update);
    },

    update: function(event) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            self.update_url, {master_token: self.grandparent.value});
        d.addCallback(function(result) {
            var data = MochiKit.Async.evalJSONRequest(result);

            if (data.length == 0) {
                self.parent_field.hide();
                self.child_field.hide();
            } else {
                self.parent_field.show();
            }

            var selected = self.parent.value;
            self.parent.options.length = 1;
            forEach(data, function(new_option) {
                var label = new_option[0];
                var value = new_option[1];
                var option = new Option(label, value);
                if (value == selected) {
                    option.selected = true;
                }
                self.parent.options[self.parent.options.length] = option;
            });
        });
    }
});


zeit.cms.master_slave_dropdown = {};

zeit.cms.configure_master_slave = function(prefix, master, slave, update_url) {
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.';
    }
    master = $(prefix + master);
    slave = $(prefix + slave);

    if (isNull(master) || isNull(slave)) {
        return;
    }
    if (!isUndefinedOrNull(zeit.cms.master_slave_dropdown[master.name])) {
        zeit.cms.master_slave_dropdown[master.name].destroy();
    }
    var path = window.location.pathname.split('/').slice(0, -1);
    path.push(update_url);
    path = path.join('/');
    zeit.cms.master_slave_dropdown[master.name] =
        new zeit.cms.MasterSlaveDropDown(master, slave, path);
};


zeit.cms.configure_multigeneration = function(prefix, grandparent, parent, child, update_url) {
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.';
    }
    grandparent = $(prefix + grandparent);
    parent = $(prefix + parent);
    child = $(prefix + child);

    if (isNull(grandparent) || isNull(parent) || isNull(child)) {
        return;
    }
    if (!isUndefinedOrNull(zeit.cms.master_slave_dropdown[grandparent.name])) {
        zeit.cms.master_slave_dropdown[grandparent.name].destroy();
    }
    var path = window.location.pathname.split('/').slice(0, -1);
    path.push(update_url);
    path = path.join('/');
    zeit.cms.master_slave_dropdown[grandparent.name] =
        new zeit.cms.MultiGenerationDropDown(grandparent, parent, child, path);
};


zeit.cms.configure_ressort_dropdown = function(prefix) {
    zeit.cms.configure_master_slave(
        prefix, 'ressort', 'sub_ressort', '@@subnavigationupdater.json');
};


zeit.cms.configure_channel_dropdowns = function(
        prefix, field, master_index, slave_index) {
    // XXX Rather ugly API to support usage in both z.c.article and z.c.cp.
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.';
    }
    var masters = jQuery(
        '[id^="' + prefix + field + '"][id$="combination_' + master_index + '"]'
        );

    jQuery.each(masters, function(index, value) {
        zeit.cms.configure_master_slave(
            prefix, field + '.' + index + '..combination_' + master_index,
            field + '.' + index + '..combination_' + slave_index,
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
