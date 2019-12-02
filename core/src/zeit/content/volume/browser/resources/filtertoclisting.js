function getTrimedElementById(id) {
    return document.getElementById(id).value.trim();
}

function filterIsCheked(id) {
    return document.getElementById(id).checked;
}

function filterTocListingTable() {
    var filterData = {
        contenttype: getTrimedElementById('filter_content_typ'),
        publish: getTrimedElementById('filter_availibility'),
        urgent: filterIsCheked('filter_is_urgent'),
        optimized: filterIsCheked('filter_is_optimized'),
        ressort: getTrimedElementById('filter_ressort'),
        supertitle: filterIsCheked('filter_has_supertitle'),
        teaserimage: filterIsCheked('filter_has_teaser_img'),
    };

    var contentTableRows = document.querySelectorAll('.tocListing tr');
    var numberOfFilterData = 0;

    contentTableRows.forEach(function(row) {
        var curRowData = {
            contenttype: getTdValue(row.querySelector('td:nth-child(1) img'),
            'alt'),
            publish: getTdValue(row.querySelector('.workflow-column > span'),
            'title'),
            urgent: getTdValue(row.querySelector('td:nth-child(10)'),
            'innerText'),
            optimized: getTdValue(row.querySelector('td:nth-child(11)'),
            'innerText'),
            ressort: getTdValue(row.querySelector('td:nth-child(9)'),
            'innerText'),
            supertitle: getTdValue(row.querySelector('td:nth-child(6)'),
            'innerText'),
            teaserimage: getTdValue(row.querySelector('td:nth-child(14)'),
            'innerText'),
        };

        row.style.display = rowVisibility(curRowData, filterData);

        if (row.style.display === 'table-row') {
            numberOfFilterData += 1;
        }
    });

    document.querySelectorAll('thead tr')[0].style.display = "table-row";
    setNumberOfVisibleRows(numberOfFilterData);
}

function getTdValue(raw_tdValue, dataField) {
    return raw_tdValue === null ? '' : raw_tdValue[dataField].trim();
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
    ['filter_content_typ', 'filter_availibility', 'filter_is_urgent',
    'filter_is_optimized', 'filter_ressort', 'filter_has_supertitle',
    'filter_has_teaser_img'].map(function(el) {
        var filterElement = document.getElementById(el);
        if (filterElement !== null) {
            filterElement.onchange = filterTocListingTable;
        }
    });
}

function setNumberOfVisibleRows(number) {
    var numOfVisibleRows = document.getElementById('numberOfVisibleRows');
    if (numOfVisibleRows === null) {
        return false;
    }
    numOfVisibleRows.innerHTML = '<strong>' + number + '</strong>';
    return true;
}

jQuery(document).ready(function() {
    if (setNumberOfVisibleRows(document.querySelectorAll('.tocListing tr').length) === false) {
        return;
    }

    registerFilterChangeEvents();

    // insert the filter values of the three dropdown menus
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
    //////////////////////////////////////////////////////////
});
