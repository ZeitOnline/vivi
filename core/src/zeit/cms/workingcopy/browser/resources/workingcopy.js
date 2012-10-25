(function() {

    var ident;

    var make_draggable = function() {
        MochiKit.Signal.disconnect(ident);
        if (! $('workingcopycontents')) {
            return;
        }
        ident = MochiKit.Signal.connect(
            'workingcopycontents', 'onmouseover', function(event) {
                var trs = $$('#workingcopycontents tbody > tr');
                forEach(trs, function(row) {
                    zeit.cms.createDraggableContentObject(row);
                  });
                MochiKit.Signal.disconnect(ident);
        });
    };

    ident = MochiKit.Signal.connect(window, 'onload', make_draggable);

})();
