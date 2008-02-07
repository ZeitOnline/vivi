// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$



connect(window, "onload", function(event) {
    var table = getElementsByTagAndClassName('table', 'contentListing')[0];
    connect(table, 'onclick', function(event) {
        var td = event.target()
        if (td.nodeName != 'TD')
            return

        var row = td.parentNode;
        if (typeof(row.draggble) == "undefined") {
            row.draggable = new Draggable(row, {
                starteffect: null,
                endeffect: null});
        }
    });
});
