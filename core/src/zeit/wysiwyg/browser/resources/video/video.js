// Video

function Import(aSrc) {
   document.write('<scr'+'ipt type="text/javascript" src="' + aSrc + '"></sc' + 'ript>');
}


var dialog		= window.parent ;
var oEditor		= dialog.InnerDialogLoaded() ;
var FCK			= oEditor.FCK ;
var FCKLang		= oEditor.FCKLang ;
var FCKConfig	= oEditor.FCKConfig ;
var FCKTools	= oEditor.FCKTools ;

var date_format = '%Y-%m-%d %H:%M';
var video_div;

Import(FCKConfig.FullBasePath + 'dialog/common/fck_dialog_common.js');

// Calendar, includes Date object patches for parsing/printing in a
// strptime/strftime like manner
Import(FCKConfig.PageConfig.ApplicationURL +
       '/@@/zc.datetimewidget/calendar.js');
Import(FCKConfig.PageConfig.ApplicationURL +
       '/@@/zc.datetimewidget/lang/calendar-en.js');
Import(FCKConfig.PageConfig.ApplicationURL +
       '/@@/mochikit/MochiKit.js');

window.addEventListener('load', function() {
	dialog.SetOkButton(true);
    new Calendar(1);

    if (get_video_div() !== null) {
        var video_id = get_video_id_div().textContent;
        var expires = get_expires_div().textContent;
        var format = get_format_div().textContent;

        $('videoId').value = video_id;
        $('expires').value = expires;
        $('format').value = format;
    }

    GetE('expires.1w').addEventListener('click', function() {
        var date = new Date();
        date.setDate(date.getDate() + 5);
        GetE('expires').value = date.print(date_format);
    }, false);

    GetE('expires.1m').addEventListener('click', function() {
        var date = new Date();
        date.setDate(date.getDate() + 30);
        GetE('expires').value = date.print(date_format);
    }, false);

    GetE('expires.infty').addEventListener('click', function() {
        GetE('expires').value = '';
    }, false);

}, false);


function get_video_div() {
    if (typeof video_div != 'undefined') {
        return video_div;
    }
    var selected_element = oEditor.FCKSelection.GetSelectedElement();
    if (selected_element === null) {
        selected_element = oEditor.FCKSelection.GetParentElement();
    }

    var class = $('kind').value;

    if (selected_element !== null) {
        if (selected_element.nodeName != 'DIV' ||
            !MochiKit.DOM.hasElementClass(selected_element, class)) {
            try {
                selected_element = MochiKit.DOM.getFirstParentByTagAndClassName(
                    selected_element, 'div', class);
            } catch (e) {
                selected_element = null;
            }
        }
    }
    return selected_element;
}

function get_video_id_div() {
    var video = get_video_div();
    if (video === null)
        return null
    var class = $('kind').value + 'Id';
    return MochiKit.DOM.getFirstElementByTagAndClassName(
        'div', class, video);
}

function get_expires_div() {
    var video = get_video_div();
    if (video === null)
        return null
    return MochiKit.DOM.getFirstElementByTagAndClassName(
        'div', 'expires', video);
}

function get_format_div() {
    var video = get_video_div();
    if (video === null)
        return null
    return MochiKit.DOM.getFirstElementByTagAndClassName(
        'div', 'format', video);
}

function Ok() {
    var video_id = GetE('videoId').value;
    var expires = GetE('expires').value;
    var format = GetE('format').value;
    if (!video_id) {
        GetE('videoId').focus();
        alert('Die Video-Id muss ausgefüllt werden.');
        return false;
    }
    if (expires) {
        // Make sure date is valid and matches format
        if (Date.parseDate(expires, date_format).print(date_format)
            != expires) {
            alert('Das Datumsformat stimmt nicht: ' + date_format);
            GetE('expires').focus();
            return false;
        }
    }

    oEditor.FCKUndo.SaveUndoStep();

    var div_class = $('kind').value;
    var id_div_class = $('kind').value + 'Id';

    if (get_video_div() === null) {
        var video_div = DIV(
            {'class': div_class},
            DIV({'class': id_div_class}, 
                video_id),
            DIV({'class': 'expires'},
                expires),
            DIV({'class': 'format'},
                format));

        var selected_element = oEditor.FCKSelection.GetBoundaryParentElement();
        selected_element.parentNode.insertBefore(
            video_div, 
            selected_element.nextSibling);
    } else {
        get_video_id_div().textContent = video_id;
        get_expires_div().textContent = expires;
        get_format_div().textContent = format;
    }

    return true;
}
