(function() {

MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    if (! $('cp-undo')) {
        return;
    }
    var view = new zeit.cms.JSONView(
        context_url + '/undo-history', 'cp-undo');

    MochiKit.Signal.connect(window, 'changed', function() {
        MochiKit.Async.callLater(0.25, function() { view.render(); });
    });

});

}());
