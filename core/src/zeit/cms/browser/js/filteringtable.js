// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt
// General Javascript functions for filtering tables

zeit.cms.FilteringTable = gocept.Class.extend({

    construct: function() {
        this.contentElement = getFirstElementByTagAndClassName(
            'table', 'contentListing');
        if (typeof this.contentElement == 'undefined') {
            return;
        }
        var tablefilter = getElement('tableFilter');
        this.metadata_deferred = null;

        connect(this.contentElement, "onclick", this, 'onDataSelect');
        connect(this.contentElement, "onclick", this, 'enableDrag');
        connect(this.contentElement, "ondblclick", this, 'onView');
        connect(tablefilter, 'onkeyup', this, 'updateFilter');
    },

    updateFilter: function(event) {
        var input = event.target();
        var table = this.contentElement;
        var filter_table = this;
        var search_list = this.processSearchInput(input.value);
        var in_what;

        forEach(table.rows, function(row) {
            var lastcell = row.cells[row.cells.length - 1];
            if (lastcell.nodeName == 'TH')
                return;
            in_what = lastcell.getElementsByTagName('span')[0].textContent;
            if (filter_table.stringFilter(search_list, in_what)) {
                row.style.display = "table-row";
            } else {
                row.style.display = "none";
            }

        });
    },

    processSearchInput: function(input) {
        return input.toLowerCase().split(' ');
    },

    stringFilter: function(search_for, in_what) {
        in_what = in_what.toLowerCase();
        var word;
        for (var idx in search_for) {
            word = search_for[idx];
            if (!word) {
                continue;
            }
            if (in_what.indexOf(word) == -1) {
                return false;
            }
        }
        return true;
    },

    onDataSelect: function(event) {
        // handler fired, when the user selected a table cell
        this.cancelMetadataLoad();
        var base_url = this.get_base_url(event);
        if (!base_url)
            return;

        var metadata_url = base_url + '/@@metadata_preview';

        var d = MochiKit.Async.wait(0.25);
        d.addCallback(this.loadMetadataHTML, metadata_url);
        this.metadata_deferred = d;

        var old_selected = this.contentElement.old_selected;
        if (old_selected) {
            removeElementClass(old_selected, 'selected');
       }
        var tr = MochiKit.DOM.getFirstParentByTagAndClassName(
            event.target(), 'TR');
        this.contentElement.old_selected = tr;
        addElementClass(tr, 'selected');
    },

    onView: function(event) {
        this.cancelMetadataLoad();
        var base_url = this.get_base_url(event);
        if (!base_url)
            return;
        view_url = base_url + '/@@view.html';
        document.location = view_url;
    },

    get_base_url: function(event) {
        var tr = MochiKit.DOM.getFirstParentByTagAndClassName(
            event.target(), 'TR');
        var url_node = getFirstElementByTagAndClassName('span', 'URL', tr);
        if (url_node) {
            return url_node.textContent;
        }
    },


    loadMetadataHTML: function(url) {
        var d = doSimpleXMLHttpRequest(url);
        d.addCallbacks(
            function(result) {
                var bottomcontent = getElement('bottomcontent');
                var topcontent = getElement('topcontent');

                bottomcontent.innerHTML = result.responseText;

                addElementClass(topcontent, 'topcontent-small');
                showElement('bottomcontent');
            });
        return d;
    },

    cancelMetadataLoad: function() {
        if (this.metadata_deferred === null) {
            return;
        }
        logger.debug("Cancelling metadata load...");
        this.metadata_deferred.cancel();
        this.metadata_deferred = null;
    },

    enableDrag: function(event) {
        var row = MochiKit.DOM.getFirstParentByTagAndClassName(
            event.target(), 'TR');
        if (isUndefinedOrNull(row.draggble)) {
            row.draggable = zeit.cms.createDraggableContentObject(row);
        }
    },

});

var table;
connect(window, 'onload', function() {
  table = new zeit.cms.FilteringTable();
});


// Add-Menu support
function add_content(menu) {
  var url = menu.options[menu.selectedIndex].value;
  if (url.indexOf('http') == -1) {
    return false;
  }
  document.location.href = url;
  return true;
}
