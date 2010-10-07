(function() {

zeit.cms.declare_namespace('zeit.content.article');

var ident = MochiKit.Signal.connect(
    window, 'cp-editor-loaded',
    function() {
        MochiKit.Signal.disconnect(ident);
        log('article-editor initialized');
    });

})();
