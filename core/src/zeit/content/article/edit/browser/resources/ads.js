(function($){

var ad_places = [];


$('body').bind('update-ad-places', function() {
    $.getJSON(application_url + '/@@banner-rules', function(p) {
        ad_places = p;
    }).complete(function() {
        $('body').trigger('update-ads');
    });
});


$('body').bind('update-ads', function() {
    // When creating a new paragraph content editable will always copy all
    // attributes, which leads to duplicated ads. Even if we flush the
    // styles right after the paragraph has been created, there still is
    // some annoying flickering visible.
    // Therefore, when content editable is active, we need to create a
    // temporary style element which will contain all style informations for
    // the ad placeholders.
    var styles    = '',
        sheet     = $('<style>').attr('id', 'content_editable_hacks');
    ad_places.forEach(function(ad_place) {
        var p_index       = ad_place - 1, // Index starts with 0.
            ad_paragraph  = $('.type-p').find('p').eq(p_index),
            dummy_ad      = '',
            pos_paragraph = 0,
            sheet         = '',
            pos_div       = 0;
        if (ad_paragraph.length === 0) {
            pos_div       = $('.type-p').eq(0).index() + 1;
            pos_paragraph = ad_place;
        } else {
            // Position starts with 1.
            pos_div       = ad_paragraph.parents('.type-p').index() + 1,
            pos_paragraph = ad_paragraph.index() + 1;
        }

        // Dynamically created styles up here.
        dummy_ad = application_url+'/@@/zeit.content.article.edit/dummy-ad.png',
        styles  += '.type-p:nth-child(' + pos_div + ')'
                + ' p:nth-child(' + pos_paragraph + ')'
                + ' { background: url("' + dummy_ad + '")'
                + ' no-repeat scroll center bottom transparent;'
                + ' padding-bottom: 20em; min-height: 10px }';
    });
    sheet.html(styles);
    $('#content_editable_hacks').remove();
    $('body').append(sheet);
});


MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {

    $('body').trigger('update-ad-places');

    MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
        $('body').trigger('update-ads');
    });

});

}(jQuery));
