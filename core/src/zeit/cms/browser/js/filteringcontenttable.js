function filterContentTable() {
    var filter_contenttype = document.getElementById('filter_content_typ').value.trim();
    var filter_publishtype = document.getElementById('filter_availibility').value.trim();
    var filter_ressorttype = document.getElementById('filter_ressort').value.trim();

    var is_urgent = document.getElementById('filter_is_urgent').checked;
    var is_optimized = document.getElementById('filter_is_optimized').checked;
    var has_supertitle = document.getElementById('filter_has_supertitle').checked;

    var filterData = {
        contenttype: filter_contenttype,
        publish: filter_publishtype,
        urgent: is_urgent,
        optimized: is_optimized,
        ressort: filter_ressorttype,
        supertitle: has_supertitle,
    };

    var contentTableRows = document.querySelectorAll('.contentListing tr');

    contentTableRows.forEach(function(row) {

        var contenttype_td = row.querySelector('td:nth-child(1) img');
        var publishtype_td = row.querySelector('.workflow-column > span');
        var ressorttype_td = row.querySelector('td:nth-child(9)');
        var is_urgent_td = row.querySelector('td:nth-child(10)');
        var is_optimized_td = row.querySelector('td:nth-child(11)');
        var has_supertitle_td = row.querySelector('td:nth-child(6)');

        if (contenttype_td !== null) {
            contenttype_td = contenttype_td.alt.trim();
        } else {
            contenttype_td = '';
        }

        if (publishtype_td !== null) {
            publishtype_td = publishtype_td.title.trim();
        } else {
            publishtype_td = '';
        }

        if (ressorttype_td !== null) {
            ressorttype_td = ressorttype_td.innerText.trim();
        } else {
            ressorttype_td = '';
        }

        if (is_urgent_td !== null) {
            is_urgent_td = is_urgent_td.innerText.trim();
        } else {
            is_urgent_td = '';
        }

        if (is_optimized_td !== null) {
            is_optimized_td = is_optimized_td.innerText.trim();
        } else {
            is_optimized_td = '';
        }

        if (has_supertitle_td !== null) {
            has_supertitle_td = has_supertitle_td.innerText.trim();
        } else {
            has_supertitle_td = '';
        }

        var curRowData = {
            contenttype: contenttype_td,
            publish: publishtype_td,
            urgent: is_urgent_td,
            optimized: is_optimized_td,
            ressort: ressorttype_td,
            supertitle: has_supertitle_td,
        };

        row.style.display = rowVisibility(curRowData, filterData);
    });

    document.querySelectorAll('thead tr')[0].style.display = "table-row";
}

function rowVisibility(curRowData, filterData) {
    Object.keys(filterData).filter(function(key) {
        if (typeof filterData[key] === 'string') {
            return filterData[key] === '';
        } else if (typeof filterData[key] === 'boolean') {
            return !filterData[key];
        }
        return true;
    }).forEach(function(removeKey){
        delete filterData[removeKey];
    });

    var hideRow = 'table-row';
    Object.keys(filterData).forEach(function(key) {
        if (typeof filterData[key] === 'boolean') {
            if (filterData[key] && curRowData[key] === '') {
                hideRow = 'none';
            }
        }

        if (typeof filterData[key] === 'string') {
            if (curRowData[key] !== filterData[key]) {
                hideRow = 'none';
            }
        }
    });

    return hideRow;
}

function setFilterValues(td_query_selector, filter_id, valueAttr) {
    var filterValues = new Set();

    var tableValues = Array.from(document.querySelectorAll(td_query_selector));
    var filterSelectForm = document.getElementById(filter_id);

    if (filterSelectForm === null) {
        return;
    }

    tableValues.forEach(function(tableValue) {
        var val = tableValue[valueAttr];
        filterValues.add(val);
    });

    filterValues.add('');

    Array.from(filterValues).sort().forEach(function(filterValue) {
        var opt = document.createElement('option');
        opt.text = filterValue;

        filterSelectForm.appendChild(opt);
    });
}

function registerFilterChangeEvents() {
    var filterContentTypeSelect = document.getElementById('filter_content_typ');
    var filterPublishTypeSelect = document.getElementById('filter_availibility');
    var is_urgent = document.getElementById('filter_is_urgent');
    var is_optimized = document.getElementById('filter_is_optimized');
    var filterRessortSelect = document.getElementById('filter_ressort');
    var has_supertitle = document.getElementById('filter_has_supertitle');

    if (filterContentTypeSelect !== null) {
        filterContentTypeSelect.onchange = filterContentTable;
    }

    if (filterPublishTypeSelect !== null) {
        filterPublishTypeSelect.onchange = filterContentTable;
    }

    if (is_urgent !== null) {
        is_urgent.onchange = filterContentTable;
    }

    if (is_optimized !== null) {
        is_optimized.onchange = filterContentTable;
    }

    if (filterRessortSelect !== null) {
        filterRessortSelect.onchange = filterContentTable;
    }

    if (has_supertitle !== null) {
        has_supertitle.onchange = filterContentTable;
    }
}

window.onload = function () {
    registerFilterChangeEvents();

    setFilterValues(
        '#topcontent table tr td:nth-child(1) img',
        'filter_content_typ',
        'alt');

    setFilterValues(
        '.workflow-column > span',
        'filter_availibility',
        'title');

    setFilterValues(
        '#topcontent table tr td:nth-child(9)',
        'filter_ressort',
        'innerText');
};