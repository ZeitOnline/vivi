connect(window, "onload", function() {
    var table = getElementsByTagAndClassName('table', 'feedsorting')[0];
    forEach(table.rows, function(row) {
        if (row.cells[0].nodeName == 'TD') {
            new Draggable(row, {
                ghosting: true
            });
        }
        
        new Droppable(row, {
            ondrop: function (element) {
                var tbody = element.parentNode;
                var before = null;
                if (row.cells[0].nodeName == 'TH') {
                    before = tbody.firstChild;
                } else {
                    before = row.nextSibling;
                }
                if (before) {
                    tbody.insertBefore(element, before);
                } else {
                    tbody.appendChild(element);
                }
            },
            hoverclass: 'feedsort-hover'
        });
    });
    
});
