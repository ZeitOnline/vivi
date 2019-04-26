MochiKit.Signal.connect(window, "onload", function() {
    var images = MochiKit.DOM.getElementsByTagAndClassName('div', 'image-data');
    forEach(images, function(image) {
        new MochiKit.DragAndDrop.Draggable(image, {
            starteffect: null,
            endeffect: null});
    });
});


