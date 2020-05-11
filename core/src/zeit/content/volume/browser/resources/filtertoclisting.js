/**
 * Get the value from a given id and return the trimmed string
 *
 * @param {string} id
 * @returns {string} The trimmed string. If the given element is `null` return ''
 */
function getTrimedElementById(id) {
    var el = document.getElementById(id);

    return el === null ? '' : el.value.trim();
}

/**
 * Get the state (checked/unchecked) from a given id
 *
 * @param {string} id
 * @returns {boolean} Return the state of the given id.
 * If the id is null, return false
 */
function filterIsCheked(id) {
    var el = document.getElementById(id);

    return el === null ? false : el.checked;
}


/**
 * Filter the table of content
 */
function filterTocListingTable() {

    // The current filter datas
    var filterData = {
        contenttype: getTrimedElementById('filter_content_typ'),
        access: getTrimedElementById('filter_access'),
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
            access: getTdValue(row.querySelector('td:nth-child(13)'),
            'innerText'),
            urgent: getTdValue(row.querySelector('td:nth-child(9)'),
            'innerText'),
            optimized: getTdValue(row.querySelector('td:nth-child(10)'),
            'innerText'),
            ressort: getTdValue(row.querySelector('td:nth-child(8)'),
            'innerText'),
            supertitle: getTdValue(row.querySelector('td:nth-child(6)'),
            'innerText'),
            teaserimage: getTdValue(row.querySelector('td:nth-child(12)'),
            'innerText'),
        };

        row.style.display = rowVisibility(curRowData, filterData);

        if (row.style.display === 'table-row') {
            numberOfFilterData += 1;
        }
    });

    // show the header row
    document.querySelectorAll('thead tr')[0].style.display = "table-row";

    setNumberOfVisibleRows(numberOfFilterData);
}

/**
 * Get trimmed value of a given HTMLElement
 *
 * @param {string} raw_tdValue HTMLElement
 * @param {string} dataField Value attribute of `raw_tdValue`
 * @returns Returns '' if `raw_tdValue` is null, otherwise the trimmed
 * value of the td-value attribute
 */
function getTdValue(raw_tdValue, dataField) {
    return raw_tdValue === null ? '' : raw_tdValue[dataField].trim();
}

/**
 * Returns the display style of a given row and the current filter datas
 *
 * @param {Object} curRowData
 * @param {Object} filterData
 * @returns Returns 'none' or 'table-row'
 */
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

/**
 * Insert all values from a given td column into the given dropdown.
 *
 * @param {string} td_query_selector The css selector of the 'td', that contains the
 * filter value
 * @param {string} filter_id The 'id' of the filter drop-down menu
 * @param {string} valueAttr The attribute, that contains the fitler value of the
 * `td_query_selector`
 * @return If the given `filter_id` is not on the current page, return `null`,
 * otherwise `undefined`
 */
function setFilterValues(td_query_selector, filter_id, valueAttr) {
    var filterValues = new Set();

    var tableValues = Array.from(document.querySelectorAll(td_query_selector));
    var filterSelectForm = document.getElementById(filter_id);

    if (filterSelectForm === null) {
        return null;
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

/**
 * Register filter change events
 */
function registerFilterChangeEvents() {
    ['filter_content_typ', 'filter_access', 'filter_is_urgent',
    'filter_is_optimized', 'filter_ressort', 'filter_has_supertitle',
    'filter_has_teaser_img'].map(function(el) {
        var filterElement = document.getElementById(el);
        if (filterElement !== null) {
            filterElement.onchange = filterTocListingTable;
        }
    });
}

/**
 * Write the number of current visible rows in the table of cpntents
 *
 * @param {Int} number
 * @returns Returns `false` on error, otherwise `true`
 */
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
        'filter_content_typ', 'alt');

    setFilterValues(
        '#topcontent table tr td:nth-child(13)',
        'filter_access', 'innerText');

    setFilterValues(
        '#topcontent table tr td:nth-child(8)',
        'filter_ressort', 'innerText');
    //////////////////////////////////////////////////////////
});
