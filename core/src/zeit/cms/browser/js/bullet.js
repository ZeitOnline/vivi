(function($){

$.fn.addBulletButton = function() {
    return this.each(function() {
        var area = $(this);
        var container = area.closest('.widget');
        var button = $('<a class="button addbullet"></a>');
        container.append(button);
        button.on('click', function(event) {
            area.val(area.val() + '\u2022');
        });
    });
};

$(document).bind('fragment-ready', function(event) {
    $('.js-addbullet', event.__target).addBulletButton();
});

$(document).ready(function() {
    $('.js-addbullet').addBulletButton();
});

}(jQuery));
