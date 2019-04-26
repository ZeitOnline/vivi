// common functions for all Zeit FCKEditor dialog commands

var dialog = window.parent;
var oEditor = dialog.InnerDialogLoaded();
var oPage = oEditor.parent;
var FCK = oEditor.FCK;
var FCKLang = oEditor.FCKLang;
var FCKConfig = oEditor.FCKConfig;
var FCKTools = oEditor.FCKTools;

function Import(src) {
   document.write('<scr'+'ipt type="text/javascript" src="' + src + '"></sc' + 'ript>');
}


Import(FCKConfig.FullBasePath + 'dialog/common/fck_dialog_common.js');


function setSkinCSS() {
    if (FCKTools.GetStyleHtml) {
        document.write(FCKTools.GetStyleHtml(GetCommonDialogCss(FCKConfig.FullBasePath + 'dialog/')));
    } else {
        document.write( '<link href="' + oEditor.FCKConfig.SkinPath + 'fck_dialog.css" type="text/css" rel="stylesheet"/>' ) ;
    }
}

zeit.wysiwyg = {};

zeit.wysiwyg.Dialog = gocept.Class.extend({

    // subclasses must set self.container_class in the constructor
    // or override get_container()

    construct: function () {
        var self = this;
        self.container = self.get_container();
    },

    get_container: function() {
        var self = this;
        var elem = oEditor.FCKSelection.GetSelectedElement();
        if (elem === null) elem = oEditor.FCKSelection.GetParentElement();

        if (elem !== null) {
            if (elem.nodeName != 'DIV' ||
                !MochiKit.DOM.hasElementClass(elem, self.container_class)) {
                try {
                    elem = MochiKit.DOM.getFirstParentByTagAndClassName(
                        elem, 'div', self.container_class);
                } catch (e) {
                    elem = null;
                }
            }
        }

        return elem;
    },

    get_div: function(class_) {
        var self = this;
        var container = self.container;
        if (container === null)
            return null;
        return MochiKit.DOM.getFirstElementByTagAndClassName(
            'div', class_, container);
    },

    get_value: function(class_) {
        var self = this;
        var div = self.get_div(class_);
        if (div === null) {
            return '';
        } else {
            return div.textContent;
        }
    },

    set_value: function(class_, value) {
        var self = this;
        var div = self.get_div(class_);
        div.textContent = value;
    },

    create_element: function(element) {
        oEditor.FCK.InsertElement(element);
        // Note: between the ' ' there is a non-breaking space.
        element.parentNode.insertBefore(P({}, ' '), element);
        element.parentNode.insertBefore(P({}, ' '), element.nextSibling);
    },

    submit: function() {
        var self = this;
        if (! self.validate())
            return false;

        oEditor.FCKUndo.SaveUndoStep();

        if (self.container === null)
            self.container = self.create();
        self.update();
        return true;
    },

    validate: function () {
        return true;
    },

    create: function () {
        return null; // override in subclass
    },

    update: function () {
        return; // override in subclass
    },

});


MochiKit.Signal.connect(window, 'onload', function(event) {
    dialog.SetOkButton(true);
    zeit.wysiwyg.dialog = new zeit.wysiwyg.dialog_class();
});


function Ok() {
    return zeit.wysiwyg.dialog.submit();
}
