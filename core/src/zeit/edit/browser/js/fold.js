(function($){

zeit.cms.declare_namespace('zeit.edit');


var SESSION_KEY = 'zeit.edit.fold';

function get_state(){
    var state = window.sessionStorage.getItem(SESSION_KEY);
    if (state === null) {
        state = {};
    } else {
        state = JSON.parse(state);
    }
    if (state[window.context_url] === undefined) {
        state[window.context_url] = {};
    }
    return state;
}

function set_state(state) {
    window.sessionStorage.setItem(SESSION_KEY, JSON.stringify(state));
}


zeit.edit.fold = function(context) {
    var id = context.getAttribute('href');
    zeit.edit.toggle_folded(id);
};

zeit.edit.toggle_folded = function(id) {
    $('#'+id).toggleClass('folded');
    var state = get_state();
    state[window.context_url][id] = $('#'+id).hasClass('folded');
    set_state(state);
};

zeit.edit.restore_folding = function() {
    var state = get_state()[window.context_url];
    $('a[cms\\:cp-module="zeit.edit.fold"]').each(
        function(index, action) {
            var id = action.getAttribute('href');
            var folded = state[id];
            if (folded === undefined) {
                return;
            }
            if (folded) {
                log("Restore folding=on for", id);
                $('#'+id).addClass('folded');
            } else {
                log("Restore folding=off for", id);
                $('#'+id).removeClass('folded');
            }
    });
};


MochiKit.Signal.connect(window, 'cp-editor-initialized', function() {
    MochiKit.Signal.connect(zeit.edit.editor, 'after-reload', function() {
        zeit.edit.restore_folding();
    });
});

})(jQuery);
