// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(window, "onload", function() {
    var images = getElementsByTagAndClassName('div', 'image-data');
    forEach(images, function(image) {
        new Draggable(image, {
            starteffect: null,
            endeffect: null});
    });
});


