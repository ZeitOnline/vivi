// Copyright (c) 2007 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

connect(window, "onload", function() {
    var table = getElementsByTagAndClassName('table', 'contentListing')[0];
    forEach(table.rows, function(row) {
        if (row.cells[0].nodeName == 'TD') {
            new Draggable(row, {
                starteffect: null,
                endeffect: null});
        }
    });
});

