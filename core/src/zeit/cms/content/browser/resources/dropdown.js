zeit.cms.MasterSlaveDropDown = Class.extend({
    
    construct: function(master, slave, update_url) {
        var self = this;
        self.master = master;
        self.slave = slave;
        self.update_url = update_url;
        MochiKit.Signal.connect(master, 'onchange', self, self.update);
        self.update();
    },

    destroy: function() {
        MochiKit.Signal.disconnectAllTo(self, self.update);
    },

    update: function(event) {
        var self = this;
        var d = MochiKit.Async.doSimpleXMLHttpRequest(
            self.update_url, {master_token: self.master.value});
        d.addCallback(function(result) {
            var data = evalJSONRequest(result)
            var selected = self.slave.value;
            self.slave.options.length = 1
            forEach(data, function(new_option) {
                var label = new_option[0]
                var value = new_option[1]
                var option = new Option(label, value)
                if (value == selected) {
                    option.selected = true;
                }
                self.slave.options[self.slave.options.length] = option;
            });
        });
    }
})


zeit.cms.master_slave_dropdown = {}

zeit.cms.configure_ressort_dropdown = function(prefix) {
    if (isUndefinedOrNull(prefix)) {
        prefix = 'form.'
    }
    var master = $(prefix + 'ressort');
    var slave = $(prefix + 'sub_ressort');
    
    if (isNull(master) || isNull(slave)) {
        return
    }
    if (!isUndefinedOrNull(zeit.cms.master_slave_dropdown[prefix])) {
        zeit.cms.master_slave_dropdown[prefix].destroy();
    }
    var path = window.location.pathname.split('/').slice(0, -1);
    path.push('@@subnavigationupdater.json');
    path = path.join('/');
    zeit.cms.master_slave_dropdown[prefix] = 
        new zeit.cms.MasterSlaveDropDown(master, slave, path);
};


MochiKit.Signal.connect(window, 'onload', function(event) {
    zeit.cms.configure_ressort_dropdown();
});
