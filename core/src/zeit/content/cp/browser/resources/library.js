MochiKit.Signal.connect(
    window, 'cp-editor-loaded', function() {

    var tabs = new zeit.cms.Tabs('cp-library');

    var url = $('cp-informatives-inner').getAttribute('cms:url') +
        '/@@block-factories.json';
    tabs.add(new zeit.cms.ViewTab(
        'library-informatives', 'Informatives',
        new zeit.cms.JSONView(url, 'library-informatives')));

    var url = $('cp-teasermosaic').getAttribute('cms:url') + 
        '/@@block-factories.json';
    tabs.add(new zeit.cms.ViewTab(
        'library-mosaic', 'Mosaic',
        new zeit.cms.JSONView(url, 'library-mosaic')));
});
