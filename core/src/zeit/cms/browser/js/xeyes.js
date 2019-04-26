(function($) {

var leftX = 89;
var leftY = 38;

var rightX = 96;
var rightY = 37;

$(window).bind('load', function() {
    $('#main-navigation').append('<div id="pupil-left">');
    $('#main-navigation').append('<div id="pupil-right">');

    $('#pupil-left').offset({left: leftX, top: leftY});
    $('#pupil-right').offset({left: rightX, top: rightY});
});

$(window).bind('mousemove', function(event) {
    zeit.cms.move_eye(event, '#pupil-left', leftX, leftY);
    zeit.cms.move_eye(event, '#pupil-right', rightX, rightY);

});

zeit.cms.move_eye = function(event, element, x, y) {
    var mouseX = event.pageX;
    var mouseY = event.pageY;

    var difX = mouseX - leftX;
    var difY = mouseY - leftY;

    var angle = Math.atan2(difX, difY);
    var newX = Math.round(Math.sin(angle));
    var newY = Math.round(Math.cos(angle));

    $(element).offset({left: x + newX, top: y + newY});
};

}(jQuery));