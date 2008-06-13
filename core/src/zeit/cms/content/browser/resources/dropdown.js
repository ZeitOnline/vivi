zeit.cms.MasterSlaveDropDown = Class.extend({
    
    construct: function(master, slave, update_url) {
        this.master = $(master);
        this.slave = $(slave);
        this.update_url = update_url;

        if (this.master == null || this.slave == null) {
            return
        }
        connect(master, 'onchange', this, 'update');
        this.update();
    },

    update: function(event) {
        var othis = this;
        var d = doSimpleXMLHttpRequest(
            this.update_url, {master_token: this.master.value});
        d.addCallback(function(result) {
            var data = evalJSONRequest(result)
            var selected = othis.slave.value;
            othis.slave.options.length = 1
            forEach(data, function(new_option) {
                var label = new_option[0]
                var value = new_option[1]
                var option = new Option(label, value)
                if (value == selected) {
                    option.selected = true;
                }
                othis.slave.options[othis.slave.options.length] = option;
            });
        });
    },
})


connect(window, 'onload', function(event) {
    var path = window.location.pathname.split('/').slice(0, -1) 
    path.push('@@subnavigationupdater.json')
    path = path.join('/')
    new zeit.cms.MasterSlaveDropDown(
        'form.ressort', 'form.sub_ressort', path)
});
