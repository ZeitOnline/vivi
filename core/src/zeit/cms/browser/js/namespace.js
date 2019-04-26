(function() {

    var declare_namespace = function(namespace) {
        var obj = window;
        forEach(namespace.split('.'), function(name) {
            if (isUndefined(obj[name])) {
                obj[name] = {};
            }
            obj = obj[name];
        });
    };

    declare_namespace('zeit.cms');
    declare_namespace('gocept');
    zeit.cms.declare_namespace = declare_namespace;

}());
