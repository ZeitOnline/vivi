(function($){

var QUOTE_CONFIG = null;
var NORMALIZATION_DISABLED = false;

MochiKit.Signal.connect(window, 'cp-editor-loaded', function() {
    if (!zeit.cms.in_article_editor()) {
        return;
    }

    $.getJSON(
        application_url + '/@@double-quote-characters',
        function(response) {
            QUOTE_CONFIG = {
                chars: new RegExp(response['chars'], 'g'),
                chars_open: new RegExp(response['chars_open'], 'g'),
                chars_close: new RegExp(response['chars_close'], 'g'),
                normalize_quotes: response['normalize_quotes']
            };
        }
    );
});

var normalize_quotes_in_field = function(input) {
    if (NORMALIZATION_DISABLED) {
        return;
    }

    if (!QUOTE_CONFIG) {
        return;
    }

    var text = input.val();

    if (!text) {
        return;
    }

    var normalized;
    if (QUOTE_CONFIG.normalize_quotes) {
        normalized = text.replace(QUOTE_CONFIG.chars_open, '»$1');
        normalized = normalized.replace(QUOTE_CONFIG.chars_close, '$1«');
    } else {
        normalized = text.replace(QUOTE_CONFIG.chars, '"');
    }

    if (normalized !== text) {
        input.val(normalized);
        input.trigger('change');
    }
};

var normalize_all_fields = function() {
    var selectors = [
        '#article-content-head\\.title',
        '#article-content-head\\.supertitle',
        '#article-content-head\\.subtitle',
        '#teaser-title\\.teaserTitle',
        '#teaser-supertitle\\.teaserSupertitle',
        '#teaser-text\\.teaserText'
    ];

    $(selectors.join(', ')).each(function() {
        normalize_quotes_in_field($(this));
    });
};

var update_normalization_state = function() {
    var checkbox = $('#article-content-head\\.disable_quote_normalization');
    if (checkbox.length) {
        NORMALIZATION_DISABLED = checkbox.is(':checked');

        if (!NORMALIZATION_DISABLED) {
            normalize_all_fields();
        }
    }
};

$(document).bind('fragment-ready', function(event) {
    var selectors = [
        '#article-content-head\\.title',
        '#article-content-head\\.supertitle',
        '#article-content-head\\.subtitle',
        '#teaser-title\\.teaserTitle',
        '#teaser-supertitle\\.teaserSupertitle',
        '#teaser-text\\.teaserText'
    ];

    $(selectors.join(', '), event.__target).on('blur', normalize_all_fields);

    // Checkbox-Handler
    $('#article-content-head\\.disable_quote_normalization', event.__target).on('change', function() {
        update_normalization_state();
    });

    // Initial state setzen
    update_normalization_state();
});

}(jQuery));