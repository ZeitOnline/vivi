(function($) {

// XXX refactor the following two functions to use, e.g., an element attribute
// that specifies the factory, instead of doing two similar loops (#11016)

var setup_views = function(parent) {
    $('.inline-view', parent).each(function(i, container) {
        if ($(container).hasClass('setup-done')) {
            return;
        }
        $(container).addClass('setup-done');
        var url = container.getAttribute('cms:href');
        container.view = new zeit.cms.View(url, container);
        container.view.render();
    });
};


var wire_forms = function(parent) {
    $('.inline-form', parent).each(function(i, container) {
        if ($(container).hasClass('wired')) {
            return;
        }
        $(container).addClass('wired');
        var url = container.getAttribute('action');
        container.form = new zeit.cms.SubPageForm(
            url, container, {save_on_change: true, load_immediately: false});
    });
};

var evaluate_form_signals = function(event) {
    // we don't get the usual MochiKit behaviour that additional arguments to
    // signal() are passed along, since window is a DOM object and thus handles
    // signals differently.
    var form = event.event();
    if (isUndefined(form)) {
        return;
    }
    var signals = $.parseJSON($(form.container).find('span.signals').text());
    if (signals) {
        $.each(signals, function(i, signal) {
            MochiKit.Signal.signal.apply(
                this, extend([zeit.edit.editor, signal.name], signal.args));
        });
    }
};

var reload_inline_form = function(selector) {
    // views can send this signal to reload an inline form, by giving its
    // `prefix` as the signal parameter.
    var element = $('#form-' + selector).closest('form')[0];
    element.form.reload();
};

var reload_inline_view = function(selector) {
    // views can send this signal to reload an inline form, by giving its
    // `prefix` as the signal parameter.
    var element = $('.inline-view[cms\\:href$="' + selector + '"]')[0];
    element.view.render();
};


MochiKit.Signal.connect(window, 'script-loading-finished', function() {
    setup_views();
    wire_forms();
    MochiKit.Signal.connect(window, 'changed', evaluate_form_signals);
    MochiKit.Signal.connect(
        zeit.edit.editor, 'reload-inline-form', reload_inline_form);
    MochiKit.Signal.connect(
        zeit.edit.editor, 'reload-inline-view', reload_inline_view);
});

$(document).bind('fragment-ready', function(event) {
    var parent = event.__target;
    setup_views(parent);
    wire_forms(parent);
});

}(jQuery));
