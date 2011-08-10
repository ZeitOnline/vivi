// Copyright (c) 2011 gocept gmbh & co. kg
// See also LICENSE.txt

zeit.cms.TableSorter = gocept.Class.extend({
    // Infrastructure to sort tables
    // Reorders the table on the browser.

    construct: function(class_name) {
        var othis = this;
        var table = MochiKit.DOM.getFirstElementByTagAndClassName(
            'table', class_name);
        forEach(table.rows, function(row) {
            if (row.cells[0].nodeName == 'TD') {
                new MochiKit.DragAndDrop.Draggable(row, {
                    ghosting: true
                });
            }

            new MochiKit.DragAndDrop.Droppable(row, {
                ondrop: function (element) {
                    var tbody = element.parentNode;
                    if (tbody.nodeName != 'TBODY') {
                        // TODO: i18n
                        alert('The table can only be sorted. ' +
                              'Adding is not possible.');
                        return;
                    }
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
                    othis.dropped(element);
                },
                hoverclass: 'tablesort-hover'
            });
        });

    },

    dropped: function(element) {
        // pass
    }

});
