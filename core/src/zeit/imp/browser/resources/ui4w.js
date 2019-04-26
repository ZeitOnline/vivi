//UI4W: One File Distribution

/**********  _meta.js  ***********/

var UI = {};
UI.version = '0.6.0-pre';


/**********  Lang.js  ***********/

/***
.. title:: UI.Lang - primitive string i18n

===============================
UI.Lang - primitive string i18n
===============================

Synopsis
========

::

    <script>LANG=es</script>
    <script src="lib/MochiKit.js"></script>
    <script src="lib/ui.js"></script> <!-- The order matters: the LANG
                                           declaration mustgoes before the
                                           ui.js import -->
    <script>
    assert(_("The value must be a number") == "El valor debe ser numérico")
    </script>

Description
===========

UI.Lang is a primitive attempt to make i18n on UI4W strings which are meant to
be read by the user. By now, it doesn't offer much to the developer, but in a
future it can become a mini i18n framework.

Dependencies
============

* MochiKit_.

.. _MochiKit: http://www.mochikit.com

Overview
========

Adding languages
----------------

TODO!

Language autodetection
----------------------

If the global variable `LANG` is not set, this modules tries to autodetect the 
user language using the  `navigator.userLanguage`, `navigator.browserLanguage`
and `navigator.language` properties, on that order.

API Reference
=============
TODO!
***/


UI.Lang = {};
UI.Lang.Language = function(code, messages) {
    bindMethods(this);
    this.code = code;
    this.messages = messages;
}
UI.Lang.Language.prototype = {
    'translate': function(str) {
        return this.messages[str];
    }
};
UI.Lang.C = new UI.Lang.Language('C', {});

UI.Lang.es = new UI.Lang.Language('es', {
    "The value must be a number": "El valor debe ser num\u00E9rico",
    "The field is required": "Debe ingresar un valor en este campo",
    "The field is not valid": "El valor ingresado no es v\u00E1lido",
    "The value must contain only letters": "El valor debe contener solo letras",
    "The value must be a valid email address": "El valor debe contener una direcci\u00F3n de correo v\u00E1lida",
    "Sun": "Dom",
    "Sunday": "Domingo",
    "Mon": "Lun",
    "Monday": "Lunes",
    "Thu": "Mar",
    "Thursday": "Martes",
    "Wed": "Mie",
    "Wednesday": "Miercoles",
    "Tue": "Jue",
    "Tuesday": "Jueves",
    "Fri": "Vie",
    "Friday": "Viernes",
    "Sat": "Sab",
    "Saturday": "Sabado",
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre"
});


UI.Lang.setLanguage = function(code) {
    if (typeof(code) != "undefined" && typeof(UI.Lang[code]) != "undefined") {
        UI.Lang.current = UI.Lang[code];
    } else {
        logWarning("UI.Lang has no translations for language " + code);
        UI.Lang.current = UI.Lang.C;
    }
}

if (typeof(LANG) != "undefined") {
    UI.Lang.setLanguage(LANG);
} else {
    var _detectedLang = navigator.userLanguage ||
                        navigator.browserLanguage ||
                        navigator.language;
    if (_detectedLang.length >= 2) {
        UI.Lang.setLanguage(_detectedLang.substring(0, 2));
    } else {
        logWarning("UI.Lang: Can't autodetect language. (Browser says: " + _detectedLang + ")");
        UI.Lang.setLanguage('C');
    }
    _detectedLang = null;
}

function _(str) {
    return  UI.Lang.current.translate(str) || str;
}
/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/
/**********  Widget.js  ***********/

/***
.. title:: UI.Widget - common widget services

==================================
UI.Widget - common widget services
==================================

Description
===========

This module contains the base and common widget methods.

The most used method defined here is :mochiref:`w$()`, an alias of
`UI.Widget.get()`.

Dependencies
============

MochiKit_.

.. _MochiKit: http://www.mochikit.com

Overview
========

What's a Widget?
----------------

A Widget is a GUI component that interacts with users, such as a Table, a
TreeView or a Form.

Widget Registration
-------------------

UI.Widget class manages the widget registry. This registry is a mapping between
DOM elements and the associated widget, if any. Widget registration also ensures
that a DOM element wrapped by a widget has the CSS class associated with it.

Once a widget instance is registed you can use the
:mochiref:`UI.Widget.get(element)` to obtain a reference to the widget
associated to the specified DOM element.

Widget registration is made by the constructor of the classes that inherits
UI.Widget. If you extend UI.Widget, put something like this on the
constructor::

    My.PrettyWidget = function(...) {
        bindMethods(this)
        //Initialization stuff
        this.element = ...
        this.cssClass = ...
        this.register()
    }

API Reference
=============
***/

/***

Class UI.Widget
---------------

Properties
~~~~~~~~~~

:mochidef:`UI.Widget.prototype.element`:

    The DOM element wrapped by the widget. **(Read-Only)**.

:mochidef:`UI.Widget.prototype.cssClass`:

    The CSS class that the element wrapped by the widget must have. This
    property should have the same value on the same class instances, but should
    differ between UI.Widget derived classes.

***/
UI.Widget = function(element) {
    bindMethods(this);
    this.element = $(element);
    this.cssClass = 'uiwidget';
    this.register();
}

/***
Static methods
~~~~~~~~~~~~~~
***/

/***

:mochidef:`UI.Widget.get(element)`:
    Returns the widget wrapped by $(`element`). As `element` is passed to `$()`,
    it can be a DOM element or a string.

:mochidef:`w$(element)`:
    A convenience alias for :mochiref:`UI.Widget.get(`element`). Note that it is
    exported to the global scope, so you don't need to prefix it with UI.Widget

***/
UI.Widget.get = function(elementId) {
    return $(elementId)._widget;
}
var w$ = UI.Widget.get;

/***

Methods
~~~~~~~
***/
UI.Widget.prototype = {
/***

:mochidef:`UI.Widget.prototype.register()`:

    Registers the widget. This should be called only from the derived classes
    constructors and after the element and cssClass propeties has been set.
***/
    'register': function() {
        if (this.element) {
            this.element._widget = this;
            addElementClass(this.element, this.cssClass);
        }
    },
/***
:mochidef:`UI.Widget.prototype.hide()`:

    Hides the widget.
***/

    'hide': function() {
        hideElement(this.element);
    },
/***
:mochidef:`UI.Widget.prototype.show(display="block")`:

    Shows the widget, using the CSS display property value specified by
    `display`.
***/
    'show': function(/*optional*/display) {
        showElement(this.element, display);
    },
/***
:mochidef:`UI.Widget.prototype.toDOM(parentElement)`,
:mochidef:`UI.Widget.prototype.__dom__(parentElement)`:

    Implements the MochiKit's DOM coercion protocol
    <http://mochikit.com/doc/html/MochiKit/DOM.html#dom-coercion-rules>`_.
***/
    'toDOM': function(parentElement) {
        return this.element;
    },

    '__dom__': function(parentElement) {
        return this.element;
    }
};

/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/


/**********  TableModel.js  ***********/

/***
.. title:: UI.TableModel - a model for your tables

======================================
UI.ListModel - a model for your tables
======================================

Synopsis
========

::

    var employees = [{'name': 'John', 'id': 123, 'salary': 1000},
                     {'name': 'Jack', 'id': 234, 'salary': 1100}];
    var employeesModel = new UI.ArrayTableModel(employees,
                                                ['name', 'salary'],
                                                ['string', 'number'],
                                                ['Name', 'Salary']);

    assert(employeesModel.getHeader(0) == 'Name');
    assert(employeesModel.getColType(1) == 'string');
    assert(employeesModel.getNumCols() == 2);
    assert(employeesModel.getNumRows() == 2);
    assert(employeesModel.getNumRows() == 2);
    assert(employeesModel.getCell(0, 1) == 1000);
    assert(employeesModel.getCell(1, 0) == 'Jack');
    assert(employeesModel.objects == employees);

    employees.push({'name': 'The new employee', 'id': 1500,
                    'salary': 500});
    //You must tell the model that the array has changed
    employeesModel.changed()


Description
===========

The UI.ListModel 'interface' is used by widgets that shows tablular data, such
as the :mochiref:`Table::UI.Table` widget.

Dependencies
============

MochiKit_.

.. _MochiKit: http://www.mochikit.com

Overview
========

A TableModel can be seen as a two dimension matrix, plus a header and a footer.
The API is pretty straightforward to implement and is detailed on
'`Class UI.TableModel`_'. The interesting part comes with the provided
implementations.

* :mochiref:`UI.ArrayTableModel` is a generic implementation that works when
  you have an array of objects, and each object must be mapped to a row, mapping
  properties to columns.

* :mochiref:`UI.AsyncArrayTableModel` inherits from ArrayListModel but
  enables you to get the array contents asynchronously, giving you the power of
  AJAX.

* :mochiref:`UI.HTMLTableModel` allows you to use a DOM table element as
  a table model.

API Reference
=============
***/

/***

Class UI.TableModel
-------------------

This is an 'abstract' class that defines the table model interface and provides
a default implementation for some methods. This default methods are not very
efficient, so override it if you can.

Signals
--------

:mochidef:`changed`:

    Fired by a table model when the model is changed.  Not actually fired by
    this class, derived classes must take care of the signaling.

***/
UI.TableModel = function(){
    bindMethods(this);
    //registerSignals(this, ['changed']);
};


/***

Methods
-------
***/
UI.TableModel.prototype = {
/***

:mochidef:`UI.TableModel.prototype.getNumCols()`:

    Returns the number of columns of this model.
***/
    'getNumCols': function(){return 0;},
/***

:mochidef:`UI.TableModel.prototype.getNumRows()`:

    Returns the number of rows of this model.
***/
    'getNumRows': function(){return 0;},
/***

:mochidef:`UI.TableModel.prototype.getCell(rowIndex, colIndex)`:

    Returns the content for the cell located on the row `rowIndex` and
    column `colIndex`.
***/
    'getCell': function(rowIndex, colIndex){return null;},
/***

:mochidef:`UI.TableModel.prototype.getHeader(colIndex)`:

    Returns the content for the header associated to the column `colIndex`.
***/
    'getHeader': function(colIndex){return null;},

/***

:mochidef:`UI.TableModel.prototype.getFooter(colIndex)`:

    Returns the content for the footer associated to the column `colIndex`.
***/
    'getFooter': function(colIndex){return null;},
/***

:mochidef:`UI.TableModel.prototype.getColType(colIndex)`:

    Returns the data type for the contents of the column `colIndex`.
***/
    'getColType': function(colIndex){return null;},

/***

:mochidef:`UI.TableModel.prototype.hasHeader()`:

    Returns true if the model has a header.
***/
    'hasHeader': function() {return false;},

/***

:mochidef:`UI.TableModel.prototype.hasFooter()`:

    Returns true if the model has a footer.
***/
    'hasFooter': function() {return false;},

/***

:mochidef:`UI.TableModel.prototype.getRow(rowIndex)`:

    Returns an array with the contents of the cells for the row `rowIndex`. The
    default implementation contructs the array using `getCell` and `getNumCols`.
***/

    'getRow' : function(rowIndex) {
        return map(partial(this.getCell, rowIndex), range(0, this.getNumCols()));
    },

/***

:mochidef:`UI.TableModel.prototype.getRows()`:

    Returns a two-dimension array with the cells of the model. The default
    implementation constructs the array using the `getRow` and `getNumRows`.
***/
    'getRows': function() {
        return map(this.getRow, range(0, this.getNumRows()));
    },
/***

:mochidef:`UI.TableModel.prototype.getHeaders()`:

    Returns an array with all the model headers. The default implementation
    constructs the array using `getHeader` and `getNumCols`.
***/
    'getHeaders': function() {
        return map(this.getHeader, range(0, this.getNumCols()));
    },
/***

:mochidef:`UI.TableModel.prototype.getFooters()`:

    Returns an array with all the model footers. The default implementation
    constructs the array using the `getFooter` and `getNumCols`.
***/
    'getFooters': function() {
        return map(this.getFooter, range(0, this.getNumCols()));
    },

/***

:mochidef:`UI.TableModel.prototype.getColTypes()`:

    Returns an array with the all column types for the model. The default
    implementation constructs the array using `getColType` and `getNumCols`.
***/
    'getColTypes': function() {
        return map(this.getColType, range(0, this.getNumCols()));
    }
};

/***

Class UI.ArrayTableModel
------------------------

This is a generic :mochiref:`UI.TableModel` implementation, backed by an array
of objects. See the Synopsis_ section for an example use.

:mochidef:`UI.ArrayTableModel(objects, fields, types, headers=null, footers=null)`:

    Constructs an ArrayTableModel, backed by the `objects` array of objects.

    `fields` is the initial value for the
    :mochiref:`UI.ArrayTableModel.prototype.fields` property. If null, all the
    fields are used.

    `types` is the initial value for the
    :mochiref:`UI.ArrayTableModel.prototype.types` property.

    `headers` is the initial value for the
    :mochidef:`UI.ArrayTableModel.prototype.headers` property. If null, the
    fields names are used.

    `footers` is the initial vlaue for the
    :mochiref:`UI.ArrayTableModel.prototype.footers` property.

Properties
~~~~~~~~~~


:mochidef:`UI.ArrayTableModel.prototype.objects`:

    The array of objects backing the table model.

:mochidef:`UI.ArrayTableModel.prototype.fields`:

    An array of strings, containing the name of the fields of the objects used
    by the model.

:mochidef:`UI.ArrayTableModel.prototype.types`:

    An array of strings, containing the types of the fields. These types can be:

    - 'string'
    - 'stringCaseInsentive'
    - 'numeric'
    - 'date'
    - 'currency'

:mochidef:`UI.ArrayTableModel.prototype.headers`,
:mochidef:`UI.ArrayTableModel.prototype.footers`:

    Arrays of values for the table headers and footers, if any.

**If you change or mutate any of the properties, make sure to invoke the
:mochiref:`UI.TableListModel.prototype.changed` method ASAP.**

***/
UI.ArrayTableModel = function(objects, fields, types, headers, footers) {
    bindMethods(this);
    this.objects = objects || [];
    this.fields = fields || this._autoDetectFields();
    this.headers = headers || this._autoDetectHeaders();
    this.types = types;
    this.footers = footers;
}
/***
Methods
~~~~~~~
***/
UI.ArrayTableModel.prototype = update(new UI.TableModel(), {
/***

:mochidef:`UI.TableModel.prototype.getNumCols()`:

    Returns the number of columns of this model.
***/
    'getNumCols': function() {
        return this.fields ? this.fields.length : 0;
    },

/***

:mochidef:`UI.ArrayTableModel.prototype.getNumRows()`:

    Returns the number of rows of this model.
***/
   'getNumRows': function() {
        return this.objects ? this.objects.length : 0;
    },
/***

:mochidef:`UI.ArrayTableModel.prototype.getCell(rowIndex, colIndex)`:

    Returns the content for the cell located on the row `rowIndex` and
    column `colIndex`.
***/

    'getCell': function(rowIndex, colIndex) {
        var val;
        try {
            val = this.objects[rowIndex][this.fields[colIndex]];
            if (val == null || typeof(val) == 'undefined') {
                val = "";
            }
        } catch(e) {
            val = "";
        }
        return val;
    },
/***

:mochidef:`UI.ArrayTableModel.prototype.getHeader(colIndex)`:

    Returns the content for the header associated to the column `colIndex`.
***/
    'getHeader': function(colIndex) {
        try {
            return this.headers[colIndex];
        } catch(e) {
            return "";
        }
    },
/***

:mochidef:`UI.ArrayTableModel.prototype.getFooter(colIndex)`:

    Returns the content for the footer associated to the column `colIndex`.
***/
    'getFooter': function(colIndex) {
        try{
            return this.footers[colIndex];
        } catch(e) {
            return "";
        }
    },
/***

:mochidef:`UI.ArrayTableModel.prototype.getColType(colIndex)`:

    Returns the data type for the contents of the column `colIndex`.
***/
    'getColType': function(colIndex) {
        try {
            return this.types[colIndex];
        } catch(e) {
            return "string";
        }
    },
    '_autoDetectFields': function() {
        if (this.objects && this.objects.length >= 1) {
            var fields = [];
            for (field in this.objects[0]) {
                fields.push(field);
            }
            return fields;
        } else {
            return [];
        }
    },
    '_autoDetectHeaders': function() {
        var headers = [];
        for (var i = 0; i < this.getNumCols(); i++) {
            headers.push(this.fields[i]);
        }
        return headers;
    },
/***

:mochidef:`UI.ArrayTableModel.prototype.hasHeader()`:

    Returns true if the model has a header.
***/
    'hasHeader': function() {
        return !(!this.headers);
    },
/***

:mochidef:`UI.ArrayTableModel.prototype.hasFooter()`:

    Returns true if the model has a footer.
***/
    'hasFooter': function() {
        return !(!this.footers);
    },
/***
:mochidef:`UI.ArrayTableModel.changed()`:

    Notify the model that some property has been changed or mutated.
***/
    'changed': function() {
        signal(this, 'changed');
    }
});

/***
Class UI.AsyncArrayTableModel
-----------------------------

Inherits from :mochiref:`UI.ArrayTableModel`. Adds AJAX capabilities to array
table models, enabling them to retrieve the backing array from a 
Asyncronous HTTP request that returs a JSON_ array. Optionally, you can provide
a mapping function to traslate the HTTP JSON response to a array of flat 
objects.

.. _JSON: http://www.json.org

Example use::

    var model = new UI.AsyncArrayTableModel(['field1', 'field2'],
                                            ['string', 'numeric'],
                                            ['Header 1', 'Header 2']);

    model.retrieveData('my/url?' + queryString(['param1', 'param2'],
                                               ['value1', 'value2']));

:mochidef:`UI.AsyncArrayTableModel(fields, [types, headers, footers, mapFunc])`

    Constructs an asynchronous array table model, where `fields`, `types`,
    `headers` and `footers` are the default values for the
    :mochiref:`UI.ArrayTableModel.prototype.fields`,
    :mochiref:`UI.ArrayTableModel.prototype.types`,
    :mochiref:`UI.ArrayTableModel.prototype.headers` and
    :mochiref:`UI.ArrayTableModel.prototype.footers` properties.

    `mapFunc` should be a function that takes as input the response given
    by the server and translate it to a array of objects as expected by
    this class.
***/

UI.AsyncArrayTableModel = function(fields, types, headers, footers, mapFunc) {
    bindMethods(this);
    this.objects = [];
    this.fields = fields;
    this.headers = headers;
    this.types = types;
    this.footers = footers;
    this._mapFunc = mapFunc;
}

/***
Methods
~~~~~~~
***/
UI.AsyncArrayTableModel.prototype = update(new UI.ArrayTableModel(), {
/***

    :mochidef:`UI.AsyncArrayTableModel.prototype.retrieveData(url, method='GET')`.

    Retrieves the array using a XMLHTTP request to the specified `url`. The
    response must be a JSON array.

    By now, the only possible value for `method` is GET.

    Returns a
    :mochiref:`http://mochikit.com/doc/html/MochiKit/Async::Deferred` as
    returned by
    :mochiref:`http://mochikit.com/doc/html/MochiKit/Async::loadJSONDoc(url)`

***/
    'retrieveData': function(url, method) {
        var method = method || 'GET';
        var d = loadJSONDoc(url);
        d.addCallback(this._receiveData);
        return d;
    },
    '_receiveData': function(objects) {
        this.objects = objects;
	if (this._mapFunc) {
	    this.objects = map(this._mapFunc, objects);
	}
        if (!this.fields) {
            this._autoDetectFields();
        }
        if (!this.headers) {
            this._autoDetectHeaders();
        }
        this.changed();
    }
});

/***
Class UI.HTMLTableModel
-----------------------

This class implements a TableModel backed by a HTML <table> element.
**This implementation never emits the :mochiref:`changed` signal**.

Inherits from :mochiref:`UI.TableModel`.

    :mochidef:`UI.HTMLTableModel(tableElement, colTypes=null)`:

    Constructs a HTMLTableModel using the `tableElement` <table> dom
    element. `colTypes` is an array of strings specifing the data types
    for the columns (See :mochiref:`UI.TableModel.prototype.getColTypes`).

***/
UI.HTMLTableModel = function(tableElement, /*optional*/ colTypes) {
    bindMethods(this);
    this._htmlTable = tableElement;
    this._colTypes = colTypes;
}

UI.HTMLTableModel.prototype = update(new UI.TableModel(), {
/***

:mochidef:`UI.TableModel.prototype.getNumCols()`:

    Returns the number of columns of this model.
***/
    'getNumCols': function() {
        try {
            return this._htmlTable.tBodies[0].rows[0].cells.length;
        } catch(e) {
            return 0;
        }
    },
/***

:mochidef:`UI.TableModel.prototype.getNumRows()`:

    Returns the number of rows of this model.
***/

    'getNumRows': function() {
        try {
            return this._htmlTable.tBodies[0].rows.length;
        } catch (e) {
            return 0;
        }
    },
/***

:mochidef:`UI.TableModel.prototype.getCell(rowIndex, colIndex)`:

    Returns the content for the cell located on the row `rowIndex` and
    column `colIndex`.
***/

    'getCell': function(rowIndex, colIndex) {
        try {
            return this._htmlTable.tBodies[0].rows[rowIndex].cells[colIndex].childNodes;
        } catch (e) {
            return '';
        }
    },
/***

:mochidef:`UI.TableModel.prototype.getHeader(colIndex)`:

    Returns the content for the header associated to the column `colIndex`.
***/
    'getHeader': function(colIndex) {
        try {
            return this._htmlTable.tHead.rows[0].cells[colIndex].childNodes;
        } catch (e) {
            return '';
        }
    },
/***

:mochidef:`UI.TableModel.prototype.getFooter(colIndex)`:

    Returns the content for the footer associated to the column `colIndex`.
***/
    'getFooter': function(colIndex) {
        try {
            return this._htmlTable.tFoot.rows[0].cells[colIndex].childNodes;
        } catch (e) {
            return '';
        }
    },
/***

:mochidef:`UI.TableModel.prototype.getColType(colIndex)`:

    Returns the data type for the contents of the column `colIndex`, as
    specified by the `colTypes` parameters on the constructor. If no colTypes
    was specified, `'string'` is returned.
***/

    'getColType': function(colIndex) {
        try {
            if (this._colTypes) {
                return this._colTypes[colIndex];
            } else {
                return 'string';
            }
        } catch (e) {
            return 'string';
        }
    },
/***

:mochidef:`UI.TableModel.prototype.hasHeader()`:

    Returns true if the `<table>` wrapped by the model has a `<thead>` child
    node.
***/
    'hasHeader': function() {
        return !(!this._htmlTable.tHead);
    },
/***

:mochidef:`UI.TableModel.prototype.hasFooter()`:

    Returns true if the `<table>` wrapped by the model has a `<tfoot>` child
    node.
***/

    'hasFooter': function() {
        return !(!this._htmlTable.tFoot);
    }
});
/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/
/**********  ListModel.js  ***********/

/***
.. title:: UI.ListModel - a model for your lists

=====================================
UI.ListModel - a model for your lists
=====================================

Synopsis
========

::

    var employees = [{'name': 'John', 'id': 123, 'salary': 1000},
                     {'name': 'Jack', 'id': 234, 'salary': 1100}]
    var employeesModel = new UI.ArrayListModel(employees, 'name', 'id');

    assert(employeesModel.getLabel(0) == 'John');
    assert(employeesModel.getValue(1) == 234);
    assert(employeesModel.getLength() == 2);
    assert(employeesModel.objects == employees);

    employees.push({'name': 'The new employee', 'id': 1500,
                                 'salary': 500});
    //You must tell the model that the array has changed
    employeesModel.changed()


Description
===========

The UI.ListModel 'interface' is used by widgets that shows list of things, such
as a list of options.

Dependencies
============

MochiKit_.

.. _MochiKit: http://www.mochikit.com

Overview
========

A ListModel can be seen as two parallel arrays containg labels and values
respectively. The API is pretty straightforward to implement and is detailed on
'`Class UI.ListModel`_'. The interesting part comes with the provided
implementations.

:mochiref:`UI.ArrayListModel` is a generic implementation that works for some
common cases:

* You have an array of objects and the value and label that you want are
  properties of these objects.

* You have an array of objects and the value and label that you want are the
  toString() of each object.

:mochiref:`UI.AsyncArrayListModel` inherits from ArrayListModel but enables you
to get the array contents asynchronously, giving you the power of AJAX.

:mochiref:`UI.HTMLSelectListModel` is a workaround made to make the life easy to
the users of mochiref:`Form::UI.SelectFormInput` who don't wants to make a
Javascript model for their select and likes to specifiy the select options as
plain HTML when declaring the form.

API Reference
=============
***/


/***
Class UI.ListModel
------------------

Signals
~~~~~~~

:mochidef:`changed`:

    Fired by the list model when it changes. Not actually fired by this
    class, derived classes must take care of the signaling.
***/
UI.ListModel = function(){
    bindMethods(this);
    //registerSignals(this, ['changed']);
};

/***
Methods
~~~~~~~
***/
UI.ListModel.prototype = {
/***

:mochidef:`UI.ListModel.prototype.getLabel(n)`:

    Returns the n-th label in the model. Derived classes must override this
    method.
***/
    'getLabel': function(index) {return "";},
/***

:mochidef:`UI.ListModel.prototype.getValue(n)`:

    Returns the n-th value in the model. Derived classes must override this
    method.
***/
    'getValue': function(index) {return "";},
/***

:mochidef:`UI.ListModel.prototype.getLength()`:

    Returns the model length. Derived classes must override this moethod.
***/
    'getLength': function() {return 0;}
};
/***

Class UI.ArrayListModel
-----------------------

UI.ArrayListModel is a implementation of ListModel, useful for making list
models from simple objects arrays.

Inherits from :mochiref:`UI.ListModel`.

This class doesn't keep observing the array looking for changes, so the :mochiref:UI.ArrayListModel.prototype.changed` must be manually called when the
array changes.

:mochidef:`UI.ArrayListModel(objects, labelField=null, valueField=null)`

    Constructs a ArrayListModel for the array `objects`. `labelField` and
    `valueField` are the default values for the
    :mochiref:`UI.ArrayListModel.prototype.labelField` and
    :mochiref:`UI.ArrayListModel.prototype.valueField` properties.

    If `labelField` is not null, the `labelField` property of each object in the
    array will be used as the label values. Otherwise, labels are the toString()
    of each object in the array.

    If `valueField` is

Properties
~~~~~~~~~~

:mochidef:`UI.ArrayListModel.prototype.objects`:

    The object array used by the model. If you change this property or mutate
    the array, make sure to invoke the
    :mochiref:UI.ArrayListModel.prototype.changed` method ASAP.

:mochiref:`UI.ArrayListModel.labelField`:

    The field used to get the model labels. If not null, the `labelField` property
    of each object in the :mochiref:`UI.ArrayListModel.prototype.objects` array
    will be used as the label values. Otherwise, labels are the `toString()`
    of each object in the array. If you change this property make sure to invoke
    the :mochiref:UI.ArrayListModel.prototype.changed` method ASAP.


:mochiref:`UI.ArrayListModel.valueField`:

    The field used to get the model values. If not null, the `valueField`
    property of each object in the array will be used as the model values.
    Otherwise, values will be the same as labels. If you change this property,
    make sure to invoke the :mochiref:UI.ArrayListModel.prototype.changed`
    method ASAP.


***/
UI.ArrayListModel = function(objects, /*optional*/ labelField,
                             /*optional*/ valueField) {
    bindMethods(this);
    this.objects = objects;
    this.labelField = labelField;
    this.valueField = valueField;
}

/***

Methods
~~~~~~~
***/
UI.ArrayListModel.prototype = update(new UI.ListModel(), {
/***

:mochidef:UI.ArrayListModel.prototype.getLabel(n)`:

    Returns the n-th label in the model.
***/
    'getLabel': function(index) {
        return this.labelField ? this.objects[index][this.labelField] :
                                 "" + this.objects[index];
    },

/***

:mochidef:UI.ArrayListModel.prototype.getValue(n)`:

    Returns the n-th value in the model.
***/

    'getValue': function(index) {
        return this.valueField ? this.objects[index][this.valueField]:
                                 this.getLabel(index);
    },
/***

:mochidef:UI.ArrayListModel.prototype.getLength(n)`:

    Returns the model length.
***/

    'getLength': function() {
        return this.objects.length;
    },
/***

:mochidef:UI.ArrayListModel.prototype.changed()`:

    Notify the model that the array backing it has changed.

    Emits the :mochiref:`changed` signal.
***/
    'changed': function() {
        signal(this, 'changed');
    }
});

/***

Class UI.AsyncArrayListModel
----------------------------

Inherits from :mochiref:`UI.ArrayListModel`. Adds AJAX capabilities to array
list models, enabling them to retrieve the backing array from a XMLHTTP request
that returs a JSON_ array.

.. _JSON: http://www.json.org

Example use::

    var model = new UI.AsyncArrayListModel('labelField', 'valueField');
    model.retrieveData('my/url?' + queryString(['param1', 'param2'],
                                               ['value1', 'value2']));

:mochidef:`UI.AsyncArrayListModel(labelField, valueField)`

    Constructs an asynchronous array list model, where `labelField` and
    `valueField` are the default values for the
    :mochiref:`UI.ArrayListModel.prototype.labelField` and
    :mochiref:`UI.ArrayListModel.prototype.valueField` properties.
***/
UI.AsyncArrayListModel = function(labelField, valueField) {
    bindMethods(this);
    this.objects = [];
    this.labelField = labelField;
    this.valueField = valueField;
}

/***

Methods
~~~~~~~
***/
UI.AsyncArrayListModel.prototype = update(new UI.ArrayListModel(), {

/***

:mochidef:`UI.AsyncArrayListModel.prototype.retrieveData(url, method='GET')`.

    Retrieves the array using a XMLHTTP request to the specified `url`. The
    response must be a JSON array.

    By now, the only possible value for `method` is GET.

    Returns a
    :mochiref:`http://mochikit.com/doc/html/MochiKit/Async::Deferred` as
    returned by
    :mochiref:`http://mochikit.com/doc/html/MochiKit/Async::loadJSONDoc(url)`

***/
    'retrieveData': function(url, method) {
        var method = method || 'GET';
        var d = loadJSONDoc(url);
        d.addCallback(this._receiveData);
        return d;
    },
    '_receiveData': function(array) {
        this.objects = array;
        this.changed();
        return array;
    }
});
/***
Class UI.HTMLSelectListModel
----------------------------

This class implements a ListModel backed by the option elements of a <select>.
**This implementation never emits the :mochiref:`changed` signal**.

Inherits from :mochiref:`UI.ListModel`.

:mochidef:`UI.HTMLSelectListModel(selectElement)`:

    Constructs a HTMLSelectListModel using the `selectElement` <select> dom
    element
***/
UI.HTMLSelectListModel = function(selectElement) {
    this._options = selectElement.getElementsByTagName("option");
}

UI.HTMLSelectListModel.prototype = update(new UI.ListModel(), {
/***

:mochidef:`UI.ArrayListModel.prototype.getLabel(n)`:

    Returns the n-th label in the model.
***/
    'getLabel': function(index) {
        return scrapeText(this._options[index]);
    },
/***

:mochidef:`UI.ArrayListModel.prototype.getValue(n)`:

    Returns the n-th value in the model.
***/

    'getValue': function(index) {
        return this._options[index].value;
    },
/***

:mochidef:`UI.ArrayListModel.prototype.getLength()`:

    Returns the model length.
***/

    'getLength': function() {
        try {
            return this._options.length;
        } catch (e) {
            return 0;
        }
    }
});


/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/


/**********  Window.js  ***********/

/***
.. title:: UI.Window - keep the popups inside the document

================================================
UI.Window - keep the popups inside the document
================================================

Synopsis
========

::

    <!-- Plain old HTML -->
    <div id="myWindow" class="uiwindow"
         style="height:400px; width:400px; left: 0px; top: 0px; position: absolute;">
        <h1>My first window <img align="right" src="close.gif" onclick="w$('myWindow').close()"></h1>
        <div class="uicontent">
            Window content goes here.
        </div>
    </div>


    // Windows can be created and manipulated by Javascript too
    var win = new UI.Window('myDOMElement');
    win.setTitleBar(UI.Window.standardTitleBar('UI.Window Demo'));
    win.include('window-content.html');



Description
===========

UI.Window is a simple container, draggable by the title bar.

By the way. the titlebar is just another div element. It can contain whatever
elements you want.

TODO: Specialized Window, having a standar title bar with close, minimize and
restore button at least.

Dependencies
============

* MochiKit_.
* :mochiref:`Draggable::UI.Draggable`.
* :mochiref:`Widget::UI.Widget`.

.. _MochiKit: http://www.mochikit.com

Overview
========

UI.Window is a very simple convenience widget, as almost all the features
provided are provided with the DOM or on MochiKit.

The more prominent feature is the XMLHTTP inclusion of other html fragments,
enabling you to make includes without server-side support. But be careful:
as stated in the API Reference, by now this don't work for any HTML fragment.

API Reference
=============

***/


/***
Class UI.Window
---------------

Inherits from :mochiref:`Widget::UI.Widget`.

:mochidef:`UI.Window(element)`:

    Constructs a window wrapping the `element` DOM node.

    If the `element` has no child with the CSS class `uititlebar`, a default
    titlebar is created

    If the `element` has no child with the CSS class 'uicontent', that child
    is created, and the `element` children is moved to that child.
    [TODO: clarify this]

Properties
~~~~~~~~~~

:mochidef:`UI.Window.prototype.element`:

    The div element wrapped by the Window. **Read-Only**.

:mochidef:`UI.Window.prototype.titleBar`:

    The div element containing the title bar. **Read-Only**, use
    :mochiref:`setTitleBar(titleBarElement)`.

:mochidef:`UI.Window.prototype.content`

    The div element containing the main window area. **Read-Only**, use
    :mochiref:`setContent(contentElement)`.

:mochidef:`UI.Window.prototype.visible`:

    True is the Window is visible. **Read-Only**.

:mochidef:`UI.Window.draggableTitle`:

   The :mochiref:`Draggable::UI.Draggable` wrapping the titlebar. **Read-Only**.

Signals
~~~~~~~

:mochidef:`hidden`:

    Fired when the window is hidden.

:mochidef:`show`:

    Fired when the window is shown.

:mochidef:`closed`:

    Fired when the window is closed. Note that the window element doesn't exists
    anymore when the signal is fired.

:mochidef:`moved`:

    Fired when the window is moved.

***/
UI.Window = function(element) {
    bindMethods(this);
    if (element) {
        this.element = $(element);
    } else {
        this.element = DIV({style: {'height': "400px",  'width': "400px",
                                    'left': "0px", 'top': "0px",
                                    'position': "absolute"}});
    }
    this.titleBar = null;
    this.content = null;
    this.draggableTitle = null;
    var titleBars = this.element.getElementsByTagName("h1");
    var titleBar = null;
    if (titleBars.length == 0) {
        this.setTitleBar(UI.Window.standardTitleBar("Untitled Window"));
    } else {
        this.setTitleBar(titleBars[0]);
    }
    var contents = getElementsByTagAndClassName("div", "uicontent", this.element);
    if (contents.length == 0) {
        var div = DIV({'class': 'uicontent'});
        var contentChilds = filter(function(el){return el.className != 'uititlebar'},
                                   this.element.childNodes);
        //Add the window element children to the window content div.
        map(partial(appendChildNodes, div), contentChilds);
        this.setContent(div);
    } else {
        this.setContent(contents[0]);
    }
    this.resize(elementDimensions(this.element));
    this.visible = getStyle(this.element, 'display') != "none";
    //registerSignals(this, ['hidden', 'shown', 'closed', 'moved']);
    this.cssClass = 'uiwindow';
    this.register();
    this.NAME = this.element.id + " (UI.Window)";
};
/***
Methods
~~~~~~~
***/

UI.Window.prototype = update(new UI.Widget(), {
/***

:mochidef:`UI.Window.prototype.show(coords=null)`

    Makes the window visible. if `coords` is not null, the window element
    position will be (`coords.x`, `coords.y`).

    Emits the shown signal.
***/
    'show': function(/*optional*/coords) {
        showElement(this.element);
        signal(this, 'shown');
        if (coords) {
            this.moveTo(coords);
        }
    },
/***

:mochidef:`UI.Window.prototype.hide()`

    Makes the window invisible.

    Emits the hidden signal.
***/
    'hide': function() {
        hideElement(this.element);
        signal(this, 'hidden');
    },
/***

:mochidef:`UI.Window.prototype.close()`

    Destroys the Window.

    Emit the closed signal.
***/
    'close': function() {
        removeElement(this.element);
        this.draggableTitle.disable();
        this.draggableTitle = null;
        signal(this, 'closed');
    },
/***

:mochidef:`UI.Window.prototype.moveTo(coords)`:

    Sets the window element position to (`coords.x`, `coords.y`).
***/
    'moveTo': function(coords) {
        setElementPosition(this.element, coords);
        signal(this, 'moved', coords);
    },
/***

:mochidef:`UI.Window.prototype.resize(dimensions)`:

    Sets the window element dimensions to `dimensions.h`x`dimensions.w`.
***/
    'resize': function(dimensions) {
        setElementDimensions(this.element, dimensions);
    },
    '_adjustSize': function() {
        setElementDimensions(this.content, {'w': this.element.clientWidth - 4,
                                            'h': this.element.clientHeight -
                                                 elementDimensions(this.titleBar).h - 4});
    },

/***

    :mochidef:`UI.Window.prototype.include(url)`

    Asynchronously loads the `url` and includes the content inside the window.

    The url contents are expected to be an HTML fragment. (No <html>, <head>,
    <body> tags).

    Note: As innerHTML is used to insert the content inside the window, any
    <script> tags present on the content will not work. Other elements or
    attributes may or may not work so use this with caution.

    Returns the
    :mochiref:`http://mochikit.com/doc/html/MochiKit/Async::Deferred`
    returned by
    :mochiref:`http://mochikit.com/doc/html/MochiKit/Async::doSimpleXMLHttpRequest`.
***/
    'include': function(url) {
        var el = DIV();
        this.setContent(el);
        var d = doSimpleXMLHttpRequest(url);
        d.addCallback(function(req){
            removeElementClass(el, 'uierror');
            el.innerHTML = req.responseText;
            return req;
        });
        d.addErrback(function(req){
            addElementClass(el, 'uierror');
            if (req) {
                el.innerHTML = req.responseText;
            } else {
                el.innerHTML = _("Error loading") + " " + url;
            }
        });
        return d;
    },
    'setTitleBar': function(titleBarElement) {
        if (this.titleBar) {
            removeElement(this.titleBar);
            this.draggableTitle.disable();
        }
        addElementClass(titleBarElement, 'uititlebar');
        if (this.element.firstChild) {
            this.element.insertBefore(titleBarElement, this.element.firstChild);
        } else {
            this.element.appendChild(titleBarElement);
        }
        this.titleBar = titleBarElement;
        this.draggableTitle = new UI.Draggable(this.titleBar);
        this.draggableTitle.elementToMove = this.element;
    },
    'setContent': function(contentElement) {
        if (this.content) {
            removeElement(this.content);
        }
        addElementClass(contentElement, 'uicontent');
        this.content = contentElement;
        appendChildNodes(this.element, this.content);
        setElementDimensions(this.content, {'w': this.element.clientWidth - 4,
                                            'h': this.element.clientHeight -
                                                 elementDimensions(this.titleBar).h - 4});

    }
});

/***

Automatic widget construction details
-------------------------------------

Declaration of windows on HTML is straightforward::

    <div class="uiwindow style="position:relative; height:<number>px; width:<number>px"
         ui:draggable="true|false">
        <h1>Window Title</h1>
        <div class="uicontent">Window Content</div>
    </div>

The position, height and width are not required, as they can be specified in
other ways  (such a CSS stylesheet).

The `ui:draggable` special attribute is optional, default to `true`. If
explicitly set to `false` the window would not be draggable by the user. As
this is done disabling the draggable contained on the property
:mochiref:`UI.Window.prototype.draggableTitle`, you can re-enable it with
javascript.

***/
UI.Window._fromElement = function(element) {
    var win = new UI.Window(element);
    var draggable = getNodeAttribute('ui:draggable') || "true";
    if (draggable == "false") {
        win.draggableTitle.disable();
    }
}

UI.Window.standardTitleBar = function(title) {
    return H1({'class': 'uititlebar'}, title);
}

/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/
/**********  Draggable.js  ***********/

/***
.. title: UI.Draggable - makes a DOM element draggable

============================================
UI.Draggable - makes a DOM element draggable
============================================

Synopsis
========

::

    // The element identified by 'myDOMElement' will be draggable by the user.
    var draggable = new UI.Draggable('myDOMElement');

    // The element identified by 'foo' will be draggable by the user only on the
    // X axis.
    var draggable = new UI.Draggable('foo', UI.Draggable.DRAG_X);

    //The element identified by 'bar' will by draggable as long the specified
    //limits are not surpased.
    var draggable = new UI.Draggable('foo', null, [0, 100], [0, 200]);


Description
===========

UI.Draggable is a DOM element wrapper, featuring limited drag and drop features.

By now, UI.Draggable just makes a DOM element draggable by the user. Optionally
you can limit the drag capability to just an axis, or jail the element in a
box.

TODO: Full D&D features including drop targets and auto 'rollback' when the
draggable is not dropped in any sensible location.


Dependencies
============

MochiKit_.

.. _MochiKit: http://www.mochikit.com

API Reference
=============

***/


/***
Class UI.Draggable
-------------------

:mochidef:`UI.Draggable(element, flags=DRAG_X | DRAG_Y, leftLimits=null,
topLimits=null)`

    Creates a new Draggable object. The draggable will wrap the element
    `element`, making it draggable to anywhere by default. `element` can be an
    string.

    `flags`, `leftLimits` and `topLimits` is the initial value for the
    :mochiref:`UI.Draggable.prototype.flags`,
    :mochiref:`UI.Draggable.prototype.leftLimits` and
    :mochiref:`UI.Draggable.prototype.topLimits` properties.


Properties
~~~~~~~~~~

:mochidef:`UI.Draggable.prototype.element`:

    The DOM element wrapped by the Draggable. **(Read-only)**.

:mochidef:`UI.Draggable.prototype.elementToMove`:

    The DOM element moved when :mochiref:`UI.Draggable.prototype.element` is dragged.

:mochidef:`UI.Draggable.prototype.flags`:

    Bit-field value, controls some draggable behaviour, such as the axis where
    the drag is limited. (See :mochiref:`UI.Draggable.DRAG_X`,
    :mochiref:`UI.Draggable.DRAG_Y`).

:mochidef:`UI.Draggable.prototype.leftLimits`:

    Two-element array containing lower and higher limits for
    `this.element.style.left`. If null, no limits will apply in the x axis.
    Note: What this limits means in practice depends on the value of
    `this.element.style.position`.

:mochidef:`UI.Draggable.prototype.topLimits`:

    Analogue to :mochiref:`UI.Draggable.prototype.leftLimits`, for the y axis.

Signals
~~~~~~~

:mochidef:`UI.Draggable.prototype.dragStarted`:

    Fired when the drag is started (mousedown over `element` or
    when :mochiref:`UI.Draggable.prototype.start()` is invoked). It doesn't
    imply that the element has been moved yet.

:mochidef:`UI.Draggable.prototype.dragFinished`:

    Fired when the drag ends (mouseup over `element` or when
    :mochiref:`UI.Draggable.prototype.stop()` is invoked). It doesn't imply
    that the element was moved between the start and the end.

:mochidef:`UI.Draggable.prototype.dragging`:

    Fired when the element is being dragged (mousemove over `element` after
    mousedown and before mouseup, or when
    :mochiref:`UI.Draggable.prototype.move()` is invoked.

    Be careful when connecting to this signal, it can fire many times on short
    intervals, and doing something cpu intensive can become the draggable
    unusable.

***/
UI.Draggable = function(element, flags, leftLimits, topLimits) {
    bindMethods(this);
    if (element) {
        this.element = $(element);
    } else {
        this.element = DIV();
    }
    this.element = $(element);
    this.elementToMove = $(element);
    this.flags = arguments.length >=2 ? flags: UI.Draggable.DRAG_X | UI.Draggable.DRAG_Y;
    this.leftLimits = leftLimits;
    this.topLimits = topLimits;
    this._dragXStart = -1;
    this._dragYStart = -1;
    this._leftStart = -1;
    this._topStart = -1;

    this._installMouseDown();
    this._disabled = false;
    //registerSignals(this, ['dragStarted', 'dragFinished', 'dragging']);
    this.NAME = repr(element) + " (Draggable)";

}

/***
Static vars
~~~~~~~~~~~
:mochidef:`UI.Draggable.DRAG_X`, :mochidef:`UI.Draggable.DRAG_Y`:

    Bit-flag for the :mochiref:`UI.Draggable.prototype.flag` property. When on,
    the draggable allows movement on the specified axis.

***/
UI.Draggable.DRAG_X = 1;
UI.Draggable.DRAG_Y = 2;
//Using Draggable and not Draggable.prototype, as this vars are
//'class variables', not 'instace variables'
UI.Draggable._draggable = null;

/***
Methods
~~~~~~~
***/

UI.Draggable.prototype = {
/***
:mochidef:`UI.Draggable.prototype.startFromEvent(event)`:

    Calls :mochiref:`UI.Draggable.prototype.start(x, y)` using the mouse
    coordinates contained on the DOM event `event`.
***/
    'startFromEvent': function(e) {
        var e = e || window.event;
        var x = e.screenX;
        var y = e.screenY;

        this.start(x, y);
    },
/***
:mochidef:`UI.Draggable.prototype.start(refX, refY)`:

    Usually called from the automatically installed onmousedown handler, this
    method starts the element drag. `refX` and `refY` are just the reference
    points where the drag starts.

***/
    'start': function(mouseX, mouseY) {
        if (this._disabled) return;
        if (UI.Draggable._draggable) {
            logError("Can't drag " + repr(this.element) + " as " +
                      repr(UI.Draggable._draggable.element) + " is being already dragged");
            return;
        }
        UI.Draggable._draggable = this;
        this.elementToMove.style.zIndex = 1;

        this._dragXStart = mouseX;
        this._dragYStart = mouseY;
        this._leftStart = parseInt(getStyle(this.elementToMove, 'left'), 10);
        this._topStart = parseInt(getStyle(this.elementToMove, 'top'), 10);
        if ((isNaN(this._leftStart) || isNaN(this._topStart))) {
            logger.error("Can't start the drag for " + repr(this) + " " +
                         "Either the left or the top of the dragged element is not a number " +
                         "left: " + this._leftStart + " top: " + this._topStart);
            return;
        }
        signal(this, 'dragStarted');
    },

/***
:mochidef:`UI.Draggable.prototype.move(x, y)`:

    Usually called from the autocatically installed onmousemove handler, this
    method move the element by `(refX - x, refY - y)` pixels, where `refX` and
    `refY` are the values passed to
    :mochiref:`UI.Draggable.prototype.start(refX, refY)`.
***/
    'move': function(mouseX, mouseY) {
        if (this._disabled) return;
        if ((this.flags & UI.Draggable.DRAG_X) > 0) {
            var newLeft = (this._leftStart + mouseX - this._dragXStart);
           if (this.leftLimits) {
                if (newLeft < this.leftLimits[0]) {
                     newLeft = this.leftLimits[0];
                }
               if (newLeft > this.leftLimits[1]) {
                    newLeft = this.leftLimits[1];
                }
            }
            if(!isNaN(newLeft)) {
                this.elementToMove.style.left = newLeft + "px";
            } else {
                logger.error("Draggable.move: newLeft isNaN");
            }
        }
        if ((this.flags & UI.Draggable.DRAG_Y) > 0) {
            var newTop = (this._topStart + mouseY - this._dragYStart);
            if (this.topLimits) {
                if (newTop < this.topLimits[0])  {
                    newTop = this.topLimits[0];
                }
                if (newTop > this.topLimits[1]) {
                    newTop = this.topLimits[1];
                }
            }
            if(!isNaN(newTop)) {
                this.elementToMove.style.top = newTop + "px";
            } else {
                logger.error("Draggable.move: newTop isNaN");
            }

        }
        signal(this, 'dragging');
    },
/***
:mochidef:`UI.Draggable.prototype.stop()`:

    Usually called from the automatically installed onmouseup handler. Stops the
    drag.

***/
    'stop': function() {
        var e = e || window.event;
        UI.Draggable._draggable = null;
        signal(this, 'dragFinished');
    },

    '_installMouseDown': function() {
        var oldMouseDown = this.element.onmousedown;
        var draggable = this;
        this.element.onmousedown = function(e) {
            var e = e || window.event;
            draggable.startFromEvent(e);
            if (oldMouseDown) {
                oldMouseDown.apply(this.element, arguments);
            }
        }
    },
/***
:mochidef:`UI.Draggable.prototype.enable()`:

    Enables the draggable (By default, the draggable is enabled).
***/
    'enable': function() {
        this._disabled = false;
    },
/***
:mochidef:`UI.Draggable.prototype.disable()`:

    Disables the draggable. Once disabled, the
    :mochiref:`UI.Draggable.prototype.start(refX, refY)` and
    :mochiref:`UI.Draggable.prototype.move(x, y)` will have no effect.
***/
    'disable': function() {
        this._disabled = true;
    }
};

connect(document, 'onmousemove', function(event) {
    var e = event.event();
    var x = e.screenX;
    var y = e.screenY;

    if (UI.Draggable._draggable) {
        UI.Draggable._draggable.move(x, y);
    }
});

connect(document, 'onmouseup', function(event) {
    var e = event.event();
    if (UI.Draggable._draggable) {
        UI.Draggable._draggable.stop(e);
    }
});

/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>.

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/
/**********  Table.js  ***********/

/***
.. title:: UI.Table - the table widget

=============================
UI.Table - the table widget
=============================

Synopsis
========

::

    <div class="uitable">
        <table>
            <thead>
                <tr>
                    <th>First Col.</th><th>Second Col.</th><th>Thrid Col.</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>123</td><td>Sample</td><td>999</td>
                </tr>
                <tr>
                    <td>456</td><td>Text</td><td>888</td>
                </tr>
                <tr>
                    <td>780</td><td>Column</td><td>777</td>
                </tr>
            </tbody>
        </table>
    </div>



Description
===========

UI.Table is a UI component that improves simple HTML tables providing tfeatures
tipical in GUI tables, such as sorting and filtering.

This widget can be used as an unobstrusive addon to simple HTML tables as shown
in the Synopsis_, or can be used along with the
:mochiref:`TableModel::UI.TableModel` class, in a MVC-like style.

Dependencies
============

* MochiKit_.
* :mochiref:`TableModel::UI.TableModel`.
* :mochiref:`Widget::UI.Widget`.

.. _MochiKit: http://www.mochikit.com

Overview
========

[TODO]

API Reference
=============

Class UI.Table
---------------

:mochidef:`UI.Table(element, model)`:

    Creates a table, inserting as a child of the <div> element $(`element`).
    `model` is the initial table model, used to render the table.

Properties
~~~~~~~~~~~

:mochidef:`UI.Table.prototype.element`:

    The <div> element onto the dynamic <table> is rendered. **Read-Only**.

:mochidef:`UI.Table.prototype.selectedRow`:

    The index of the currently selected row. -1 if no row is selected.
    **Read-Only**, use the :mochiref:`UI.Table.prototype.selectRow(rowIndex)` 
    method to change it.

Signals
~~~~~~~

:mochidef:`rowClicked`:

    Fired when the user clicks a row in the table. The clicked row index, and
    the event associated with the click are passed are parameters to the
    connected slots. Note that the :mochiref:`rowSelected` signal is
    more general, as this signal is not emited when a row is selected
    programatically, or by other methods different from a mouse click
    (such a keyboard navigation when supported?).

:mochidef:`headerClicked`:

    Fired when the user clicks on a header. The clicked header index and the
    event associated are passed as parameters to the connected slots.

:mochidef:`rowSelected`:

    Fired when a row is selected, independtly of how (programatically,
    user click, etc). The row index is passed as parameter to the connected
    slots

:mochidef:`rowMouseOver`:

    Fired when a mouse-over occured on a row. The row index and the event
    associated are passed as parameters to the connected slots.

:mochidef:`rowMouseOut`:

    Fired when a mouse-out occured on a row. The row index and the event
    associated are passed as parameters to the connected slots.

:mochidef:`rowAdded`:

    Fired when a row is about to be rendered. This may be because a new row has
    been added, or simply because the entire table is being rendered. A <tr> DOM
    element and the row index on the model is passed as parameter to the slots. 
    As the element is a mutable DOM object, slots can use this signal to manipulate 
    the rendered rows contents.

***/

UI.Table = function(element, model) {
    bindMethods(this);
    if (element) {
        this.element = $(element);
    } else {
        this.element = DIV();
    }
    this.selectedRow = -1;
    this._modelRowIndexes = []; //Map from the body row index to the model row index
    this._bodyRowIndexes = []; //Map from the model row index to the body row index
    this._selectedTR = null;
    this._highlightedTR = null;
    this._sortCol = -1;
    this._arrow = SPAN(null);
    this._model = null;
    //registerSignals(this, ['rowClicked', 'headerClicked', 'rowSelected',
    //                       'rowMouseOver', 'rowMouseOut', 'rowAdded'])
    this.cssClass = 'uitable';
    this.register();

    if (model) {
        this.setModel(model);
    }
    this.NAME = this.element.id + "(UI.Table)"
}

UI.Table._NO_ARROW = "&nbsp;&nbsp;&nbsp;";
UI.Table._DOWN_ARROW = "&nbsp;&nbsp;&darr;";
UI.Table._UP_ARROW = "&nbsp;&nbsp;&uarr;";


/***

Methods
~~~~~~~
***/
UI.Table.prototype = update(new UI.Widget(), {

/***

:mochidef:`UI.Table.prototype.setModel(model)`:

    Sets the model used to render the table to the `model`
    :mochiref:`TableModel::UI.TableModel` instance. Redraws the table according
    to the `model` contents.
***/
    'setModel': function(model) {
        this._model = model;
        connect(model, 'changed', this, 'render'); //Re-render the table when the model change
        this.render();
    },
/***

:mochidef:`UI.Table.prototype.model()`:

    Returns the TableModel associated with the Table.
***/
    'model': function() {
        return this._model;
    },

/***

:mochidef:`UI.Table.prototype.render`:

    Redraws the HTML table
***/
    'render': function() {
        if (!this._model) {
            logError("Can't render a table without model");
            return;
        }
        var existingTable = this.getTableElement();
        if (existingTable) {
            swapDOM(existingTable, null); //For now we just erase the old table
        }
        var optionals = [];
        if (this._model.hasHeader()) {
            optionals.push(THEAD(null,
                                 TR(null,
                                    map(this._makeTH, this._model.getHeaders(),
                                        range(0, this._model.getNumCols())))));
        }
        if (this._model.hasFooter()) {
            optionals.push(TFOOT(null,
                                 TR(null,
                                    map(partial(TD, null), this._model.getFooters()))));
        }
        var table =  TABLE(null,
                           optionals,
                           TBODY(null,
                                 map(this._makeTR, this._model.getRows(),
                                     range(0, this._model.getNumRows()))));
        this.element.appendChild(table);
        this._initIndexesMaps();
    },
    '_initIndexesMaps': function() {
        this._bodyRowIndexes = [];
        this._modelRowIndexes = [];
        //on init, index are the same in the model and in the table body;
        for (var i = 0; i < this._model.getNumRows(); i++) {
            this._bodyRowIndexes.push(i);
            this._modelRowIndexes.push(i);
        }
    },
/***

:mochidef:`UI.Table.prototype.getTableElement()`:

    Returns the DOM <table> element generated by the last render() call.
***/
    'getTableElement': function() {
        return this.element.getElementsByTagName("table")[0];
    },

    '_makeTH': function(cell, colIndex) {
        var th = TH(null,
                    cell);
        addElementClass(th, 'col_' + colIndex);
        var table = this;
        th.onclick = function(e) {
            table.clickHeader(colIndex, e || window.event);
        }
        return th;
    },
    '_makeTR': function(row, rowIndex) {
        var tr = TR(null, map(this._makeTD, row, this._model.getColTypes()));
        addElementClass(tr, 'row_' + rowIndex);
        addElementClass(tr, (rowIndex % 2) == 0 ? 'even': 'odd');
        var table = this;
        tr.onclick = function(e) {
            table.clickRow(table.modelRowIndex(tr.sectionRowIndex), e || window.event);
        }
        tr.onmouseover = function(e) {
            table.mouseOverRow(table.modelRowIndex(tr.sectionRowIndex), e || window.event);
        }
        tr.onmouseout = function(e) {
            table.mouseOutRow(table.modelRowIndex(tr.sectionRowIndex), e || window.event);
        }
        signal(this, 'rowAdded', tr, rowIndex);
        return tr;
    },
    '_makeTD': function(cell, type) {
        switch(type) {
            case 'rawhtml':
                var td = TD(null);
                td.innerHTML = cell;
                return td;
            default:
                return TD(null, cell);
        }
    },
    //rowIndex is the index in the model of the row, not the index in the tbody
    'clickRow': function(rowIndex, /*optional*/event) {
        this.selectRow(rowIndex);
        signal(this, 'rowClicked', rowIndex, event);
    },
    'clickHeader': function(colIndex, /*optional*/event) {
        var header = this.getTH(colIndex);
        var lastOrder = header.getAttribute('_order') || 'asc';
        var newOrder = lastOrder == 'asc' ? 'desc' : 'asc';
        header.setAttribute('_order', newOrder);
        this.sort(colIndex, newOrder == 'desc');
        if (newOrder == 'asc') {
            this._arrow.innerHTML = UI.Table._DOWN_ARROW;
        } else {
            this._arrow.innerHTML = UI.Table._UP_ARROW;
        }
        header.appendChild(this._arrow);
        signal(this, 'headerClicked', colIndex, event);
    },
    //rowIndex is the index in the model of the row, not the index in the tbody
    'mouseOverRow': function(rowIndex, /*optional*/event) {
        this.highlightRow(rowIndex);
        signal(this, 'rowMouseOver', rowIndex, event);
    },
    'mouseOutRow': function(rowIndex, /*optional*/ event) {
        this.highlightRow(-1);
        signal(this, 'rowMouseOut', rowIndex, event);
    },
/***

:mochidef:`UI.Table.prototype.selectRow(rowIndex)`:

    Selects the row which index on the model is `rowIndex`.
***/
    'selectRow': function(rowIndex) {
        if (this._selectedTR) {
            removeElementClass(this._selectedTR, 'ui_active');
        }
        var selectedRow = this.getTR(rowIndex);
        if (selectedRow) {
            addElementClass(selectedRow, 'ui_active');
            this._selectedTR = selectedRow;
        } else {
	    this._selectedTR = null;
	}
        this.selectedRow = rowIndex;	
        signal(this, 'rowSelected', rowIndex);
    },
    //rowIndex is the index in the model of the row, not the index in the tbody
    'highlightRow': function(rowIndex) {
        if (this._highlightedTR) {
            removeElementClass(this._highlightedTR, 'ui_hover');
        }
        var rowToHighlight = this.getTR(rowIndex);
        if (rowToHighlight) {
            addElementClass(rowToHighlight, 'ui_hover');
            this._highlightedTR = rowToHighlight;
        }
    },
/***

:mochidef:`UI.Table.prototype.modelRowIndex(tBodyRowIndex)`:

    Returns the index on the model of the row having `tBodyRowIndex` index on
    the rendered <tbody>.
***/
    'modelRowIndex': function(bodyRowIndex) {
        return this._modelRowIndexes[bodyRowIndex];
    },
/***

:mochidef:`UI.Table.bodyRowIndex(modelRowIndex)`:

    Returns the index on the rendered tbody of the row having the
    `modelRowIndex` index on the model
***/
    'bodyRowIndex': function(modelRowIndex) {
        return this._bodyRowIndexes[modelRowIndex];
    },
/***

:mochidef:`UI.Table.getTR(rowIndex)`:

    Returns the rendered <tr> for the `rowIndex`-th row on the model
***/
    'getTR': function(rowIndex) {
        var bodyRowIndex = this.bodyRowIndex(rowIndex);
        if (bodyRowIndex >= 0) {
            return this.getTableElement().tBodies[0].rows[bodyRowIndex];
        } else {
            return null;
        }
    },
/***
:mochidef:`UI.Table.getTH(colIndex)`:

    Returns the rendered <th> for the `colIndex`-th header on the model.
***/
    'getTH': function(colIndex) {
        if (colIndex >= 0) {
            return this.getTableElement().tHead.rows[0].cells[colIndex];
        } else {
            return null;
        }
    },
    //Adapted code from http://www.kryogenix.org/code/browser/sorttable/sorttable.js
    '_sortDate': function(a, b) {
        // y2k notes: two digit years less than 50 are treated as 20XX, greater than 50 are treated as 19XX
        aa = scrapeText(a.cells[this.sortCol]);
        bb = scrapeText(b.cells[this.sortCol]);
        if (aa.length == 10) {
            dt1 = aa.substr(6,4)+aa.substr(3,2)+aa.substr(0,2);
        } else {
            yr = aa.substr(6,2);
            if (parseInt(yr) < 50) { yr = '20'+yr; } else { yr = '19'+yr; }
            dt1 = yr+aa.substr(3,2)+aa.substr(0,2);
        }
        if (bb.length == 10) {
            dt2 = bb.substr(6,4)+bb.substr(3,2)+bb.substr(0,2);
        } else {
            yr = bb.substr(6,2);
            if (parseInt(yr) < 50) { yr = '20'+yr; } else { yr = '19'+yr; }
            dt2 = yr+bb.substr(3,2)+bb.substr(0,2);
        }
        if (dt1==dt2) return 0;
        if (dt1<dt2) return -1;
        return 1;
    },

    '_sortCurrency': function(a, b) {
        aa = scrapeText(a.cells[this.sortCol]).replace(/[^0-9.]/g,'');
        bb = scrapeText(b.cells[this.sortCol]).replace(/[^0-9.]/g,'');
        return parseFloat(aa) - parseFloat(bb);
    },

    '_sortNumeric': function(a, b) {
        aa = parseFloat(scrapeText(a.cells[this.sortCol]));
        if (isNaN(aa)) aa = 0;
        bb = parseFloat(scrapeText(b.cells[this.sortCol]));
        if (isNaN(bb)) bb = 0;
        return aa-bb;
    },

    '_sortString': function(a, b) {
        var aa = scrapeText(a.cells[this.sortCol]).toLowerCase();
        var bb = scrapeText(b.cells[this.sortCol]).toLowerCase();
        if (aa==bb) return 0;
        if (aa<bb) return -1;
        return 1;
    },

    '_sortStringCaseSensitive': function(a,b) {
        aa = scrapeText(a.cells[this.sortCol]);
        bb = scrapeText(b.cells[this.sortCol]);
        if (aa==bb) return 0;
        if (aa<bb) return -1;
        return 1;
    },
    /***
    :mochidef:`UI.Table.prototype.sort(colIndex, reverse=false)`:

    Sorts the rendered table, by the `colIndex`-th column. If `reverse` is
    `true`, the table is sorted in reverse.
    ***/
    'sort': function(colIndex, reverse) {
        colIndex = colIndex || 0;
        reverse = reverse || false;
        this.sortCol = colIndex;
        var dataType = this._model.getColType(colIndex) || "string"; //TODO: Autodetect data type
        var fnName = '_sort' + dataType.charAt(0).toUpperCase() +
                       dataType.substring(1);

        if (!this[fnName]) {
            logError("UI.Table.sort: Type " + dataType + " unrecognized");
            return;
        }
        var table = this.getTableElement();
        var newRows = new Array();
        for (var i = 0; i < table.tBodies[0].rows.length; i++) {
            newRows[i] = table.tBodies[0].rows[i];
            newRows[i]._modelIndex = this.modelRowIndex(i);
        }
        newRows.sort(this[fnName]);
        for (var i = 0; i < newRows.length; i++) {
            if (!reverse) {
                table.tBodies[0].appendChild(newRows[i]);
            } else {
                table.tBodies[0].appendChild(newRows[newRows.length - 1 -  i]);
            }
            this._modelRowIndexes[i] = newRows[i]._modelIndex;
            this._bodyRowIndexes[newRows[i]._modelIndex] = i;
            try {
                delete newRows[i]._modelIndex;
            } catch (e) {
                //In IE the delete doesn't work (Why?)
                newRows[i]._modelIndex = null;
            }
        }
    }
});

/***

Automatic widget construction details
-------------------------------------

Declaring UI.Tables with no dynamic data is simple, just wrap your table onto a
div with the `uitable` css class, as shown on the Synopsis_.

When connecting the UI.Table with a model, the HTML syntax is also pretty
simple::

    <div class="uitable" ui:model="<js-expression>"></div>

Where `<js-expression>` must evaluate to a valid
:mochiref:`TableModel::UI.TableModel`.

***/

UI.Table._fromElement = function(element) {
    var table = new UI.Table(element.id || element.getAttribute('id'));
    //This is pretty dummy, but some times someone wants the sorting and
    //filtering without getting into javascript coding
    var model = element.getAttribute('ui:model');
    if (!model) {
        var htmlTables = element.getElementsByTagName('table');
        if (htmlTables && htmlTables.length > 0) {
            table.setModel(new UI.HTMLTableModel(htmlTables[0]));
        }
        return;
    } else {
        table.setModel(eval("(" + model + ")"));
        return;
    }
}
/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/
/**********  Slider.js  ***********/

/***
.. title:: UI.Slider - the slider widget

=============================
UI.Slider - the slider widget
=============================

Synopsis
========

::

    <input type="text" id="myinput">
    <div class='uislider' id="myslider" style="width: 410px;"
         ui:input="myinput" ui:minvalue="0" ui:maxvalue="100">

Description
===========

UI.Slider is a rich UI component that allows the user to select a value from a
predefined range.

Optionally you can link the slider to a <input>, to change the input value when
the slider is moved and viceversa.

Dependencies
============

* MochiKit_.
* :mochiref:`Draggable::UI.Draggable`.
* :mochiref:`Widget::UI.Widget`.

.. _MochiKit: http://www.mochikit.com

Overview
========

The Slider API is pretty simple. You can get and set the value, and link an
input to the slider. See the following API Reference for details.

API Reference
=============

Class UI.Slider
---------------

TODO: Fix the redundancy in steps and valueMapperFunctions!

:mochidef:`UI.Slider(element, steps=101, valueMapperFunctions=null, linkedInput=null)`:

    Creates a slider wrapping the <div> element $(`element`). `steps` and
    `valueMapperFunctions` are the initial  values for the properties
    :mochiref:`UI.Slider.prototype.steps` and
    :mochiref:`UI.Slider.prototype.valueMapperFunctions`. 
    But if valueMapperFunctions is null the initial value will be
    :mochiref:`UI.Slider.ValueMappers.range(0, 100, 1)`.
    The `linkedInput` is passed to the 
    :mochiref:`UI.Slider.prototype.linkWithInput` method.
    

:mochidef:`UI.Slider(element, minValue=0, maxValue=100, linkedInput=null)`:

    Compability with UI4W 0.5.x. And it's a simpler way to write this::

        new UI.Slider(elements, maxValue - minValue + 1, 
                      [partial(operator.add, minValue),
                       partial(operator.add, -minValue)]
                      linkedInput)


Properties
~~~~~~~~~~

:mochidef:`UI.Slider.prototype.element`:

    The <div> element wrapped by this slider. **Read-Only**.

:mochidef:`UI.Slider.prototype.minValue`,
:mochidef:`UI.Slider.prototype.maxValue`:

    Compatibility with UI4W 0.5.x.
    The minimum and maximum value for the slider value range. 
    **Deprecated**.

:mochidef:`UI.Slider.prototype.value`:

    The current slider value. **Read-Only**, use the
    :mochiref:`UI.Slider.prototype.setValue(value)` method to change this 
    property.

:mochidef:`UI.Slider.prototype.step`:

    The current slider value. **Read-Only**, use the
    :mochiref:`UI.Slider.prototype.setStep(value)` method to change this 
    property.

:mochidef:`UI.Slider.prototype.valueMapperFunctions`:

    Array of two functions, used to map slider 'steps' to meaningful values.
    The first function should receive a step value and return the slider value.
    The second is the inverse of that, receiving a value and returning the 
    corresponding step.

    There are some useful generators to this pair of function in 
    mochiref:`UI.Slider.ValueMappers`.


:mochidef:`UI.Slider.prototype.draggable`:

    The Draggable::UI.Draggable instance used by the slider. 
    *Use with caution*. **Read-Only**.

:mochidef:`UI.Slider.prototypr.tipFormatter`:

    A function to format the value to be shown on the tip.


Signals
~~~~~~~

:mochidef:`valueChanged`:

    Fired when the slider value changes. Be careful, this signal can be fired
    many times in short intervals.

***/


UI.Slider = function(element, steps, valueMapperFunctions, linkedInput) {
    // Compatibility code: In revisions prior to 240, the signature of this
    // constructor is (element, minValue, maxValue, linkedInput). 
    // So we need to detect when the old constructor is being called.
    // This is done checking for the valueMapperFunctions type: If it's a
    // number, the constructor is being called as the old one.
    // This is not perfect, as according to the docs of the old API, 
    // maxValue could be null while minValue isn't. And that case is not
    // covered here.
    if (typeof(valueMapperFunctions) == "number") {
        this.minValue = steps;
        this.maxValue = valueMapperFunctions;
        steps = this.maxValue - this.minValue + 1;
        valueMapperFunctions = [partial(operator.add, this.minValue), 
                                partial(operator.add, this.minValue)];
    } else {
        //Old fields that has no sense when not in compatibility mode
        this.minValue = 0;
        this.maxValue = 0;
    }

    bindMethods(this);
    if (element) {
        this.element = $(element);
    } else {
        this.element = DIV({'style': {'width': '100px'}});
    }
    this.steps = steps || 101;
    this.valueMapperFunctions = valueMapperFunctions || 
                                UI.Slider.ValueMappers.range(0, 100, 1);
    this.step = 0;
    this.value = valueMapperFunctions[0](0); //Minimum value
    this.linkedInput = null;
    this._valueTip = DIV({'class': 'uislidertip'});
    hideElement(this._valueTip);
    document.getElementsByTagName("body")[0].appendChild(this._valueTip);
    var childrens = this.element.getElementsByTagName("div");
    if (!childrens || childrens.length == 0) {
        var sliderDiv = DIV(null, ' ');
        this.element.appendChild(sliderDiv);
        childrens = this.element.getElementsByTagName("div");
    }
    var child = childrens[0];
    this._draggableWidth = parseInt(getStyle(child, 'width'), 10);
    this._maxLeft = parseInt(getStyle(this.element, 'width'), 10) -
                             this._draggableWidth;
    this.draggable = new UI.Draggable(child, UI.Draggable.DRAG_X, [0, this._maxLeft]);
    connect(child, 'onmouseover', this, '_showValueTip');
    connect(child, 'onmouseout', this, '_hideValueTip');
    connect(this.draggable, 'dragging', this, '_updateValue');
    this._connectWithClicks();
    //registerSignals(this, ['valueChanged']);
    this.cssClass = 'uislider';
    this.tipFormatter = operator.identity;
    this.register();
    this._updateValue();
    if (linkedInput) {
        this.linkWithInput(linkedInput);
        linkedInput.value = this.value;
    }
    this.NAME = this.element.id + "(UI.Slider)";
}

/***

Methods
~~~~~~~
***/
UI.Slider.prototype = update(new UI.Widget(), {
    //Updates the slider value using the left position
    '_updateValue': function(/*optional*/ left) {
        if (arguments.length == 0) {
            left = parseInt(getStyle(this.draggable.element, 'left'), 10);
        }
        this.setStep(Math.round((left / this._maxLeft) * (this.steps - 1)),
                     false); // Updates the step without moving the slider again
        
    },

    //Called when the user clicks the slider
    '_click': function(pageX, pageY) {
        var elementX = elementPosition(this.element).x;
        var relativeClickX = (pageX - elementX - this._draggableWidth / 2);
        this.setStep(parseFloat((relativeClickX / this._maxLeft) *
                               (this.steps - 1)));
    },

/***
:mochidef:`UI.Slider.prototype.setStep(step, moveSlider=true)`:

    Moves the slider to the position corresponding to the step `step` .

    By default, the slider should be moved when the current
    step is changed  progamatically. 
    
    [The only known exception is the when setStep is used internally by
    _updateValue, which is called when the slider has been moved manually 
    by the user]
***/
    'setStep': function(step, /*optional*/ moveSlider) {
        if (isUndefinedOrNull(moveSlider)) {
            moveSlider = true; 
        }
        if (step > this.steps - 1) {
            step = this.steps - 1;
        }

        if (step < 0) {
            step = 0;
        }

        if (moveSlider) {
            var left = Math.round(((step) / (this.steps - 1)) *
                                  this._maxLeft);
            
            this.draggable.element.style.left = left + "px"; 
        }
        
        this.step = parseInt(step, 10);
        var oldValue = this.value;
        this.value = this.valueMapperFunctions[0](this.step);
        this._valueTip.innerHTML = this.tipFormatter(this.value);
        if (this.value != oldValue) {
            signal(this, 'valueChanged', this.value);
            if (this.linkedInput) {
                this.linkedInput.value = this.value;
            }
            this._locateTip();
        }
    },

/***
:mochidef:`UI.Slider.prototype.setValue(value)`:

    Moves the slider to the position corresponding to the value `value` .
***/
    'setValue': function(value) {
        this.setStep(this.valueMapperFunctions[1](value));
    },


    '_showValueTip': function() {
        this._locateTip();
        showElement(this._valueTip);
    },

    '_locateTip': function() {
        var pos = elementPosition(this.draggable.element);
        var tipDim = elementDimensions(this._valueTip);
        pos.y -= (tipDim.h + 5)
        setElementPosition(this._valueTip, pos);        
    },

    '_hideValueTip': function() {
        hideElement(this._valueTip);
    },

    //Makes the onclick event registration
    '_connectWithClicks': function() {
        var slider = this;
        connect(this.element, 'onclick', function(e) {
            var mouse = e.mouse();
            slider._click(mouse.page.x, mouse.page.y);
        });
        connect(this.draggable.element, 'onclick', function(e) {
            e.stop();
            return false;
        });
    },
/***

:mochidef:`UI.Slider.prototype.linkWithInput(inputElement)`:

    'Links' the slider and the input element `inputElement`. When the slider
    values changes, the input will be update with the new value. And if the
    input value changes, the slider will move accordingly.

    Current limitation: Only one input can be linked to the slider. Linking
    another can produce unexpected behaviour [FIXME!]
***/
    'linkWithInput': function(inputElement) {
        this.linkedInput = inputElement;
        this.linkedInput.value = this.value;
        var slider = this;
        connect(inputElement, 'onchange', function(e) {
            var val = parseFloat(inputElement.value, 10);
            if (!isNaN(val)) {
                slider.setValue(val);
            }

        });
    }
});

/***
UI.Slider.ValueMappers
----------------------

Contains some useful functions to construct the value mappers required by
mochiref:`UI.Slider`. See mochiref:`UI.Slider.prototype.valueMapperFunctions`.

***/

UI.Slider.ValueMappers = {


/***
:mochidef:`UI.Slider.ValueMappers.range(minValue, maxValue, by=1)`:

    Makes a pair of mappers for the values between `minValue` and `maxValue`.
    A `by` parameter can be specified to get stepped values.
***/
    'range': function(minValue, maxValue, by) {
        by = by || 1;

        var toValue = function(step) {
            return (minValue + (step * by));
        };
        var toStep = function(value) { 
            return ((value - minValue) / by);
        };
        return [toValue, toStep];
    },

/***
:mochidef:`UI.Slider.ValueMappers.values(x, y, z....)`:

    Makes a pair of mappers for the values specified as arguments.
***/
    'values': function(/*arguments...*/) {
        var vals = arguments;
        var toValue = function(step) {
            return vals[step];
        }
        var toStep =  function(value) {
            var step = findIdentical(vals, value);
            if (step == -1) {
                throw {'msg': "Step for value " + value + " not found"};
            }
            return step;
        }
        return [toValue, toStep];
    }

}
/***

Automatic widget construction details
-------------------------------------

Sliders are tipically constructed via HTML, using simple divs to declare them::

    <div class="uislider" ui:minValue="<number>" ui:maxValue="<number>"
         ui:step="<number>" ui:input="<string-with-an-input-id>" 
         style="width:<number>px"></div>

`<div class="uislider">` elements may include the `ui:minValue`, `ui:maxValue,
`ui:step` special attributes indicating the range for the slider values.

Alternatively, the `ui:values` can specify a strict list of values for the 
slider, as shown below::

    <div class="uislider" ui:values="<array-of-values>"
         ui:input="<string-with-an-input-id>" 
         style="width:<number>px"></div>


`ui:input` is also optional and contains the id of an <input> element to link
the slider with (See :mochiref:`UI.Slider.prototype.linkWithInput`).

Note that this element *must have a width using 'px' as the unit*. The width
can be given on the style attributes (as in the example), or via CSS.
Anyway, after the document is loaded, the slider must have a width.
***/
UI.Slider._fromElement = function(element) {
    var minValue = parseFloat(getNodeAttribute(element, 'ui:minvalue') || "0", 
                            10);
    var maxValue = parseFloat(getNodeAttribute(element, 'ui:maxvalue') || "100",
                            10);
    var step = parseFloat(getNodeAttribute(element, 'ui:step') || "1",  10);
    var steps = 0;
    var linkedInput = getNodeAttribute(element, 'ui:input');
    var values = getNodeAttribute(element, 'ui:values');
    var mapperFunctions = null;
    if (values) {
        values = eval(values);
        steps = values.length;
        mapperFunctions = UI.Slider.ValueMappers.values.apply(window, values);
    } else {
        steps = Math.floor((maxValue - minValue) / step) + 1;
        mapperFunctions = UI.Slider.ValueMappers.range(minValue, 
                                                       maxValue, step);
    }
    var slider = new UI.Slider(element, steps, mapperFunctions);

    if (linkedInput) {
        slider.linkWithInput($(linkedInput));
    }

}

/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/

/**********  Form.js  ***********/

/***
.. title:: UI.Form - Form validation framework

===================================
UI.Form - Form validation framework
===================================

Synopsis
========

::

    <form class="uiform">
        <!-- Simple items -->
        <input type="text" name="name" id="name"
               ui:label="First Name" ui:validators="[alphaspaces, required]">
        <input type="text" name="email" id="email"
               ui:label="e-Mail" ui:validators="[email, required]">
        <!-- Composite items -->
        <span ui:label="Phone Number">
            (<input type="text" name="areacode" id="areacode""
                    ui:validators="[numeric]">) -
            <input type="text" name="phonenum" id="phonenum"
                    ui:validators="[numeric, required]">
        </span>
    </form>


Description
===========

UI.Form is an advanced validation framework for html forms. It takes care of
validation of typical data types, such as numbers, emails, and provides a simple
way to plug more special validations on individuals inputs or entire forms.

As a bonus, UI.Form can take care of the form layout, avoiding the tedious with
labels and tables.

Dependencies
============

* MochiKit_.
* :mochiref:`Widget::UI.Widget`.
* :mochiref:`ListModel::UI.ListModel`.

.. _MochiKit: http://www.mochikit.com

Overview
========

Form layout
-----------

By default, UI.Form will alter the layout of the form children, putting them in
a table with two columns: one for the labels, one for the inputs. The labels are
right aligned.

If you want to take control over form layout, add `ui:keeplayout="true"` to the
form::

    <form ui:keeplayout="true">
    <!-- ... -->
    </form>

Form validation
---------------

The ui:validators attribute, may specify form-level or input-level validators,
depending on where are located (<form> or <input>, <select>, <textarea>). The
content of ui:validators attribute must be a javascript expression that
evaluates to a array of functions. Each function is a 'validator'.

Input level validators are pretty simple: they receive the input element as
parameter, and returns an error message if the input is invalid or
UI.Form.VALIDATION_PASSED if everything is ok.

Form level validators are somewhat different: they receive the form element as
parameter, and returns UI.Form.VALIDATION_PASSED when no error is detected, but
when a validation error happens, the validator returns an
array of :mochiref:UI.Form.Error object. Each Error object has a message and a
list of erroneous fields associated with that message. Example::


    function validateForm(form) {
        if (form['foo'].match(/^\s*$/) && form['bar'].match(/^\s*$/)) {
            return [new UI.Form.Error("Either foo or bar must be specified",
                                      [form['foo'], form['bar']])];
        }
        return UI.Form.VALIDATION_PASSED;
    }

UI4W provides some default validators, present in the
:mochiref:`UI.Form.Validators` namespace, thought they can be specified without
the UI.Form.Validators prefix.

Validators are called automatically when the form is submitted in the standard
synchronous way (cancelling the submit if one or more validators raise errors),
or when invoking the :mochiref:`UI.Form.prototype.submitAsync()` method.

Alternatively, you can call them manually invoking the
:mochiref:`UI.Form.prototype.validate()`
method.

Behind of the scenes
--------------------

:mochiref:`UI.Form` contains a array of :mochiref:`UI.FormItem`.

A FormItem represents a 'row' in the form. Each FormItem contains a array of
:mochiref:`UI.FormInput`.

UI.FormInput wraps a <input> element. There is some specializations of
UI.FormInput, that handles  the other form element (SelectFormInput for
<select>, TODO: TextAreaFormImput  for <textarea>), but from the UI.Form point
of view, they are just FormInputs.

API Reference
=============

***/

/***
Class UI.Form
-------------

UI.Form is the facade to the form layout and validation framework.

Inherits from :mochiref:`Widget::UI.Widget`.

:mochidef:`UI.Form(element, items=[], validators=[])`

    Creates a Form, wrapping the `element` DOM form element. `items` and
    `validators` are the initial values for the
    :mochiref:`UI.Form.prototype.items` and
    :mochiref:`UI.Form.prototype.validators` properties.

Properties
~~~~~~~~~~

:mochidef:`UI.Form.prototype.element`:

    The form element wrapped by the form. **Read-only**

:mochidef:`UI.Form.prototype.items`:

    Array of the :mochiref:`UI.FormItem` objects. Each items may contain one
    or more `UI.FormInput` objects.

:mochidef:`UI.Form.prototype.validators`:

    Array of validators functions. See `Form validation`_.

Signals
~~~~~~~

:mochidef:`submitted`:

    Fired when the user submits the form. At this stage the form is not
    validated.

:mochidef:`sent`:

    Fired when the form has been sent and the current page is currently running.
    This only happens when the form is asyncronous submitted.

:mochidef:`validationPassed`, :mochidef:`validationFailed`:

    One of these signals are fired after the validation, depending of the
    validation result.

***/
UI.Form = function(element, /*optional*/items, /*optinal*/validators) {
    bindMethods(this);
    element = element || FORM();
    this.element = $(element);
    this.items = items || [];
    this.validators = validators || [];
    //registerSignals(this, ['submitted', 'sent', 'validationPassed',
    //                       'validationFailed']);
    this.cssClass = 'uiform';
    this._invalidInputs = [];
    this.register();
    this.NAME = this.element.id + "(UI.Form)";
    var oldonsubmit = element.onsubmit;
    var form = this;
    element.onsubmit = function() {
        if (!form.validate()) {
            return false;
        }
        if (!oldonsubmit) {
            return true;
        } else {
            return oldonsubmit();
        }
    }
}

/***
Static Vars
~~~~~~~~~~~
***/

/***

:mochidef:`UI.Form.VALIDATION_PASSED`:

    Value returned by input and form level validators when the validation
    passed.

***/
UI.Form.VALIDATION_PASSED = "";

/***
:mochidef:`UI.Form.Messages`:

    Validation messages for the default validators (See
    `Predefined Form Validators`_).

    It contains string objects, named `REQUIRED`, `NOT_VALID`, `NUMBER`, `ALPHA`,
    `ALPHANUM`, `ALPHASPACES`, `ALPHANUMSPACES` and `EMAIL`. You can modify this
    objects to get custom messages. (Note: If you just want to translate
    messages, look at :mochiref:`Lang::UI.Lang`).

    Example::

        UI.Form.Messages.REQUIRED = 'Please, fill this field';
        UI.Form.Messages.NOT_VALID = 'Please enter a valid value for this field';
***/

UI.Form.Messages = {
    'REQUIRED': _("The field is required"),
    'NOT_VALID': _("The field value is not valid"),
    'NUMBER': _("The value must be a number"),
    'ALPHA': _("The value must contain only letters"),
    'ALPHANUM': _("The value must contain only letters and numbers"),
    'ALPHASPACES': _("The value must contain only letters and spaces"),
    'ALPHANUMSPACES': _("The value must contain only letters, numbers and spaces"),
    'EMAIL': _("The value must be a valid email address")
}


/***
Methods
~~~~~~~
***/
UI.Form.prototype = update(new UI.Widget(), {
/***
:mochidef:`UI.Form.prototype.render()`:

    Redraws the form, using automatic layout.
***/
    'render': function() {
        //map(removeElement, this.element.childNodes);
        this.element.appendChild(TABLE(null,
                                       TBODY(null,
                                             map(function(i){return i.render()},
                                             this.items))));
    },
/***
:mochidef:`UI.Form.prototype.validate()`:

    Trigger form validation. Erroneous fields will be marked with the uierror
    css class, and a uitip div will be visible when the mouse is over the
    invalid element.

    Emits the validationPassed or validationFailed signals depending on
    validation status.

    Return true if the validation passed, false if failed.
***/
    'validate': function() {
        this._invalidInputs = [];
        var valid = true;
        for (var i = 0; i < this.items.length; i++) {
            if (this.items[i].inputs) {
                for(var j = 0; j < this.items[i].inputs.length; j++) {
                    //FIXME: The real error is not here, this not-null-validation
                    //should be removed
                    if (this.items[i].inputs[j]){
                        this.items[i].inputs[j].validate();
                        if (!this.items[i].inputs[j].valid) {
                            this._invalidInputs.push(this.items[i].inputs[j].element)
                            valid = false;
                        }
                    }
                }
            }
        }
        for (var i = 0; i < this.validators.length; i++) {
            var errs = this.validators[i](this.element)
            //The result is a array of errors, each containing a message and a array of fields
            var form = this;
            if (errs && errs.length) {
                valid = false;
                forEach(errs, function(err) {
                    var inputs = err.fields;
                    var msg = err.message;
                    forEach(inputs, function(input) {
                        //TODO: Mark the errors and show the message.
                        //if(input.id) w$(input.id).markError(err.msg);
                        form._invalidInputs.push(input);
                    });
                });
            }
        }
        if (valid) {
            signal(this, 'validationPassed');
        } else {
            signal(this, 'validationFailed');
        }
        return valid;
    },
/***
:mochidef:`UI.Form.prototype.submitAsync(url=this.element.action, extraNames=[],
extraValues=[], method='GET')`:

    Submits the form asynchronously, to the `url` specified, only if form
    validation passes.

    `extraNames` is an  array of extra parameters to append on the request.
    `extraValues` are  the values of these extra parameters (obviously,
    `extraNames` and `extraValues` must have the same length).

    TODO: You can also specify the HTTP method for the request. (By now just
    'GET' is supported).

    Emits the sent signal when the form is sent.

    Return a Mochikit's Deferred object, corresponding to the return value of
    Mochikit's sendXMLHttpRequest, or null if the validation failed.

***/
    'submitAsync': function(url, /*optional*/extraNames, /*optional*/extraValues, /*optional*/method) {
        if (!this.validate()) {
            return null;
        }
        signal(this, 'submitted');
        var extraNames = extraNames || [];
        var extraValues = extraValues || [];
        var method = method || 'GET';
        var url = url || this.element.action;
        if (url) {
            var contents = formContents(this.element);
            var names = contents[0];
            var values = contents[1];
            extend(names, extraNames);
            extend(values, extraValues);
            var d = doSimpleXMLHttpRequest(url, names, values);
            signal(this, 'sent', names, values);
            return d;
        }
        return fail("UI.Form.submitAsync: No url given and url autodetection failed");
    },
/***
:mochidef:`UI.Form.prototype.invalidInputs()`:

    Returns an array of erroneous <input> elements as reported by the last
    validation done.
***/
    'invalidInputs': function() {
        return this._invalidInputs;
    }

});


/***
Class UI.Form.Error
-------------------

Instances of UI.Form.Error are returned by form-level validators when the
validation fails.

:mochidef:`UI.Form.Error(message, inputElement1, ...)`

    Constructs a form valdation error with a `message` and a list of erroneous
    input fields.

Properties
~~~~~~~~~~

:mochidef:`UI.Form.Error.prototype.message`:

    The error message.

:mochidef:`UI.Form.Error.prototype.fields`:

    Array of input elements associated with the validation error.
***/
UI.Form.Error = function(msg /*, fields...*/) {
    this.message = msg;
    this.fields = extend([], arguments, 1);
}

/***
Class UI.FormItem
-----------------

Note: Most of the time you don't need to manually construct the FormItems, they
are constructed automatically for you when declaring a form with the `uiform`
css class.

:mochidef:`UI.FormItem(element, label="", inputs=[], flow='horizontal')`

    Crates a form item (Somewhat equivalent to a form row), wrapping the html
    element `element`.

    `label`, `inputs` and `flow` are the initial values for
    the :mochiref:`UI.FormItem.prototype.label`,
    :mochiref:`UI.FormItem.prototype.inputs` and
    :mochiref:`UI.FormItem.prototype.flow` properties.

Properties
~~~~~~~~~~

:mochidef:`UI.FormItem.prototype.element`:

    The DOM element wrapped by the form item. **Read-Only**.

:mochidef:`UI.FormItem.prototype.label`:

    The item label.

:mochidef:`UI.FormItem.prototype.inputs`:

    An array of :mochiref:`UI.FormInput` objects, asociated with the <input>
    elements contained on the form item element.

:mochidef:`UI.FormItem.prototype.flow`:

    The flow for the rendering of the `element` childs. It can be 'horizontal'
    or 'vertical'.

***/

UI.FormItem = function(element, label, inputs, flow) {
    bindMethods(this);
    if (element) {
        this.element = $(element);
    } else {
        this.element = SPAN(null, inputs);
    }
    this.label = label || "";
    this.inputs = inputs || [];
    this.flow = flow || "horizontal";
}
/***
Methods
~~~~~~~
***/

UI.FormItem.prototype = {
/***
:mochidef:`UI.FormItem.prototype.render()`

    Renders the item in memory, returing a TR element containg the item with the
    new layout. (Used by :mochiref:`UI.Form.prototype.render()`)
***/
    'render': function() {
        var childs = filter(function(el){return el.nodeType > 0},
                            this.element.childNodes);
        if (childs && childs.length) {
            var style = {'class': 'noborderspace'};
            if (this.flow == "horizontal") {
                this.element.appendChild(TABLE(style,
                                               TBODY(null,
                                                     TR(style,
                                                        map(partial(TD, style), childs)))));
            } else {
                this.element.appendChild(TABLE(style,
                                                TBODY(null,
                                                      map(function(el){
                                                          return TR(style,
                                                                     TD(style, el))
                                                      }, childs))));
            }
        }
        return TR(null,
                   TD({'align': 'right'},
                      LABEL(null, this.label!=""?this.label+":":"")),
                   TD(null, this.element));
    }
};

/***
Class UI.FormInput
------------------

Note: Most of the time you don't need to manually construct the FormInputs, as
they are constructed automatically for you when declaring a form with the
`uiform` css class.

Inherits from :mochiref:`Widget::UI.Widget`.

:mochidef:`UI.FormItem(element, validators)`:

    Creates a FormItem, a thin wrapper around the input element `element`.

    `validators` is the initial value for the
    :mochiref:`UI.FormInput.validators` property.

Properties
~~~~~~~~~~

:mochidef:`UI.FormInput.prototype.element`:

    The <input> element wrapped by the FormInput. **Read-Only**.

:mochidef:`UI.FormInput.validators`:

    An array of input-level validators functions. See `Form Validation`.

:mochiref:`UI.FormInput.valid`:

    True if the element value was valid the last time when validation ran.

***/

UI.FormInput = function(element, validators) {
    bindMethods(this);
    if (element) {
        this.element = $(element);
    } else {
        this.element = INPUT();
    }
    this.validators = validators;
    this.cssClass = "uiforminput";
    this.valid = true;
    this.tip = null;
    this.register();
    this._connectEvents();
}

/***
Methods
~~~~~~~
***/
UI.FormInput.prototype = update(new UI.Widget(), {
/***

:mochidef:`UI.FormInput.prototype.validate()`:

    Validates the element data, marking the element with the `uierror` css class
    if the validation failed and poping out a tip when the mouse is over the
    erroneous input.
***/
    'validate': function() {
        var element = this.element;
        this.unmarkError();
        this.valid = true;
        if (!this.validators) return;
        for (var i = 0; i < this.validators.length; i++) {
            var msg = this.validators[i](this.element);
            if (msg && (msg != UI.Form.VALIDATION_PASSED)) {
                this.markError(msg);
                return false;
            }
        }
        return true;
    },
/***
:mochidef:`UI.FormInput.prototype.markError(message)`:

    Mark the element as erroneous, setting the `uierror` class and poping out a
    tip with the speciifed `message` when the mouse is over the input.

***/

    'markError': function(msg) {
        addElementClass(this.element, 'uierror');
        var position = elementPosition(this.element);
        var dimensions = elementDimensions(this.element);
        if (typeof(position.x) != 'undefined' && typeof(dimensions.w) != 'undefined') {
            this.tip = DIV({'class': 'uitip'}, DIV({'class': 'uimsg'}, msg));
            this.tip.style.left = (position.x + dimensions.w) + "px";
            this.tip.style.top = (position.y) + "px";
            hideElement(this.tip);
            document.getElementsByTagName('body')[0].appendChild(this.tip);
            connect(this.element, 'onmouseover', this, 'showTip');
            connect(this.element, 'onmouseout', this, 'hideTip');
        } else {
            logWarning("FormInput.markError: Can't get element position and/or dimensions");
        }
        this.valid = false;
    },
/***
:mochidef:`UI.FormInput.prototype.showTip()`:

    Shows the popup error tip.
***/
    'showTip': function() {
        showElement(this.tip);
    },
/***
:mochidef:`UI.FormInput.prototype.hideTip()`:

    Hides the popup error tip.
***/
    'hideTip': function() {
        hideElement(this.tip);
    },
/***
:mochidef:`UI.FormInput.prototype.unmarkError()`:

    Removes the error `uierror` class from the element and disables the
    error message tip.
***/
    'unmarkError': function() {
        removeElementClass(this.element, 'uierror');
        if (this.tip) {
            disconnect(this.element, 'onmouseover', this, 'showTip');
            disconnect(this.element, 'onmouseout', this, 'hideTip');
            removeElement(this.tip);
            this.tip = null;
            this.element.onmouseover = null;
            this.element.onmouseout = null;
        }
    },
    '_connectEvents': function() {
        if (!this.element) return;
        var oldblur = this.element.onblur;
        var oldfocus = this.element.onfocus;
        var formInput = this;
        this.element.onblur = function() {
            formInput.validate();
            if (oldblur) {
                oldblur.apply(this.element, arguments);
            }
        }
        this.element.onfocus = function() {
            formInput.unmarkError();
            if (oldfocus) {
                oldfocus.apply(this.element, arguments);
            }
        }
    }
});

/***
Class UI.SelectFormInput
------------------------

UI.SelectFormInput is a UI.FormInput derived class that manages a <select>
element.

Inherits from :mochiref:`UI.FormInput`.

:mochidef:`UI.SelectFormInput(element, validators, model)`:

    Creates a SelectFormInput wrapping the <select> element `element`.

    `validators` is the initial value for
    :mochiref:`UI.SelectFormInput.prototype.validators` property.

    `model` is the :mochiref:`ListModel::UI.ListModel` used to populate the select field
    options.

Properties
~~~~~~~~~~

:mochidef:`UI.SelectFormInput.prototype.element`:

    The <select> element wrapped by the select form input. **Read-Only**.

***/
UI.SelectFormInput = function(element, validators, model) {
    bindMethods(this);
    this._model = null;
    if (element) {
        this.element = element;
    } else {
        this.element = SELECT();
    }
    this.element = $(element);
    this.cssClass = "uiselectforminput";
    this.register();
    this.setModel(model);
}

/***
Methods
~~~~~~~
***/
UI.SelectFormInput.prototype = update(new UI.FormInput(), {

/***
:mochidef:`UI.SelectFormInput.prototype.setModel(listModel)`:

    Sets a new :mochiref:`ListModel::UI.ListModel` for the select options
***/
    'setModel': function(model) {
        disconnect(this.model, 'changed', this, 'render'); //FIXME (Deprecated by MochiKit)
        this._model = model;
        this.render();
        connect(model, 'changed', this, 'render');
    },

/***
    Returns the :mochiref:`ListModel::UI.ListModel` assigned to the
    SelectFormInput.
***/
    'model': function() {
        return this._model;
    },

/***
    Renders the options according to the :mochiref:`UI.ListModel` assigned.
***/
    'render': function() {
        replaceChildNodes(this.element, []);//For now we just erase the old options
        for (var i = 0; i < this._model.getLength(); i++) {
            this.element.appendChild(OPTION({'value': this._model.getValue(i)},
                                             this._model.getLabel(i)));
        }
    }
});

/***
Predefined Form Validators
---------------------------

The UI.Form.Validators namespace contains some common used validators include
on UI4W. You don't need to fully qualify this validators when declaring them on
html using the `ui:validators` special attribute.

***/


UI.Form.Validators = {};

/***
:mochidef:`UI.Form.Validators.required(el)`:

    Returns UI.Form.Messages.REQUIRED if the value of the element `el` is
    empty or contains  only spaces. Otherwise returns UI.Form.VALIDATION_PASSED.
***/
UI.Form.Validators.required = function(el) {
    return el.value.match(/^\s*$/) ?
           UI.Form.Messages.REQUIRED :
           UI.Form.VALIDATION_PASSED ;
}

/***
:mochidef:`UI.Form.Validators.regexp(regexp, message=UI.Form.Messages.NOT_VALID)
(el)`:

    [Note that this function actually returns a validator function. The produced
    validator function is described below].

    Returns `message` if the value  of the element`el` doesn't match the regular
    expression `regexp`. Otherwise returns UI.Form.VALIDATION_PASSED.

    Note that `regexp` is a RegExp object, not a string.
***/
UI.Form.Validators.regexp = function(re, msg) {
    return function(el) {
        return el.value.match(re) ? UI.Form.VALIDATION_PASSED :
                                    msg || UI.Form.Messages.NOT_VALID;
    }
}

/***
:mochidef:`UI.Form.Validators.numeric(el)`:

    Returns UI.Form.Messages.NUMBER if the value of the element `el` is not a
    number. Otherwise returns UI.Form.VALIDATION_PASSED. Empty or spaces-only
    values are allowed.
***/
UI.Form.Validators.numeric = function(el) {
    var val = el.value.replace(/,/, "").replace(/\./, "");  //FIXME: Too arbitrarious.

    return (isNaN(val)) ? UI.Form.Messages.NUMBER :
                          UI.Form.VALIDATION_PASSED;
};
/***
:mochidef:`UI.Form.Validators.alpha(el)`:

    Returns UI.Form.Messages.ALPHA if the value of the element `el` is not
    alphabetic. Otherwise returns UI.Form.VALIDATION_PASSED. Empty value is
    allowed.
***/

UI.Form.Validators.alpha = UI.Form.Validators.regexp(/^[A-Za-z]*$/,
                                                     UI.Form.Messages.ALPHA);
/***
:mochidef:`UI.Form.Validators.alphaspaces(el)`:

    Returns UI.Form.Messages.ALPHASPACES if the value of the element `el` is not
    alphabetic-with-or-without-spaces. Otherwise returns UI.Form.VALIDATION_PASSED.
    Empty value is allowed.
***/

UI.Form.Validators.alphaspaces = UI.Form.Validators.regexp(/^[A-Za-z\s]*$/,
                                                           UI.Form.Messages.ALPHASPACES);

/***
:mochidef:`UI.Form.Validators.alphanum(el)`:

    Returns UI.Form.Messages.ALPHANUM if the value of the element `el` is not
    alphanumeric. Otherwise returns UI.Form.VALIDATION_PASSED. Empty value is
    allowed.
***/
UI.Form.Validators.alphanum = UI.Form.Validators.regexp(/^[0-9A-Za-z]*$/,
                                                        UI.Form.Messages.ALPHANUM);

/***
:mochidef:`UI.Form.Validators.alphanumspaces(el)`:

    Returns UI.Form.Messages.ALPHANUM if the value of the element `el` is not
    alphanumeric-with-or-without-spaces. Otherwise returns
    UI.Form.VALIDATION_PASSED. Empty value isallowed.
***/

UI.Form.Validators.alphanumspaces = UI.Form.Validators.regexp(/^[0-9A-Za-z\s]*$/,
                                                              UI.Form.Messages.ALPHANUMSPACES);


/***
:mochidef:`UI.Form.Validators.email(el)`:

    Returns UI.Form.Messages.EMAIL if the value of the element `el` is not
    an email adress. Otherwise returns UI.Form.VALIDATION_PASSED. Empty value is
    allowed.
***/

UI.Form.Validators.email = UI.Form.Validators.regexp(/^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+\.[A-Za-z]{2,4}$/,
                                                     UI.Form.Messages.EMAIL);

/***
Automatic widget construction details
-------------------------------------

As seen on Synopsis_ example, 90%+ of the time you just need to specify your
form in html with special attributes and classes. The objects needed to make the
form usable are constructed automatically by UI4W. The following is the details
about that html->javascript object conversion

***/

/***
ui:validators attribute
~~~~~~~~~~~~~~~~~~~~~~~

The `ui:validators` attribute, can be present on <form>, <input> and the other
form input related elements. It must contains a valid javascript expression that
evaluates to a javascript array of function. These array of functions is mapped
to the validators property of UI.Form or UI.FormInput.

The UI.Form.Validators.* functions are exported to the global namespace when the
expression evaluation is done.

***/

UI.FormInput._getValidators = function(el) {
    var validators = el.getAttribute("ui:validators");
    if (validators) {
        with(UI.Form.Validators) {//FIXME: Moz complains about with(){eval()}
            validators = eval("(" + validators + ")");
        }
    } else {
        validators = [];
    }
    return validators;
}
/***
<input> elements
~~~~~~~~~~~~~~~~

::

    <input ui:validators="js-expression">

The input element only has one special attribute: ui:validators. For details on
these attribute see `ui:validators attribute`_.
***/

UI.FormInput._fromElement = function(el) {
    return new UI.FormInput(el, UI.FormInput._getValidators(el));
}

/***
<select> elements
~~~~~~~~~~~~~~~~~

::

    <select ui:validators="js-expression" ui:model="js-expression">

The select input has two special attributes: ui:validators and ui:model.

ui:model value must be a javascript expression that evaluates to a
UI.ListModel object. See :mochiref:`ListModel::UI.ListModel` for info about the list
models.

ui:validators is parsed as described on `ui:validators attribute`_.

***/
UI.SelectFormInput._fromElement = function(el) {
    var model = el.getAttribute("ui:model");
    if (model) {
        model = eval("(" + model + ")");
        return new UI.SelectFormInput(el, UI.FormInput._getValidators(el), model);
    } else {
        model = new UI.HTMLSelectListModel(el.cloneNode(true));
        var select = new UI.SelectFormInput(el, UI.FormInput._getValidators(el), model);
        //map(removeElement, select.childNodes);
        select.render();
        return select;
    }
}

/***
direct <form> children elements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    <tag ui:label="label-text-literal">

Each direct <form> child is mapped to a UI.FormItem. The item label is obtained
from the ui:label special attribute value, that is string literal. (No
javascript expression here ;-).

There is no problem on putting <input> or other
form input tags as a direct <form> child: that's just a FormItem with only one
FormInput (the typical case, BTW).

For FormItems with more than one input, group the inputs on an element, as shown
on the Phone Number in the Synopsis_.

***/

UI.FormItem._fromElement = function(el) {
    var label = getNodeAttribute(el, "ui:label");
    var fInputs = [];
    if (el.tagName.toLowerCase() == "input") {
        fInputs.push(UI.FormInput._fromElement(el));
    } else if (el.tagName.toLowerCase() == "select") {
        fInputs.push(UI.SelectFormInput._fromElement(el));
    } else if (el.tagName.toLowerCase() == "textarea") {
        fInputs.push(UI.FormInput._fromElement(el));
    }
    var inputs = el.getElementsByTagName("input");
    if (inputs && inputs.length) {
        fInputs = fInputs.concat(map(UI.FormInput._fromElement, inputs));
    }
    var textareas = el.getElementsByTagName("textarea");
    if (textareas && textareas.length) {
        fInputs = fInputs.concat(map(UI.FormInput._fromElement, textareas));
    }
    var selects = el.getElementsByTagName("select");

    if (selects && selects.length) {
        fInputs = fInputs.concat(map(function(element) {
                                        s = UI.SelectFormInput._fromElement(element);
                                     }, selects));
    }

    //var textareas = el.getElementsByTagName("textarea");

    return new UI.FormItem(el, label, fInputs);
}

/***

<form> elements
---------------
::

    <form class="uiform" ui:validators="javascript-expression"
          ui:keeplayout="true|false">

The form element must be declared with the uiform class to be detected by UI4W
as a UI. If the attribute `ui:keeplayout` is specified and the value is "true",
UI.Form will not manage the form layout.

ui:validators is parsed as described on `ui:validators attribute`_.
***/
UI.Form._fromElement = function(el) {
    var keepLayout = getNodeAttribute(el, "ui:keeplayout");
    keepLayout = (keepLayout && (keepLayout == "true"));
    var validators = getNodeAttribute(el, "ui:validators");
    if (validators) {
        with(UI.Form.Validators) {//FIXME: Moz complains about with(){eval}
            validators = eval("(" + validators + ")");
        }
    } else {
        validators = [];
    }
    var childs = filter(function(el){return el.nodeType == 1},
                        el.childNodes);
    var form = new UI.Form(el, map(UI.FormItem._fromElement, childs), validators);
    if (!keepLayout) form.render();
    return form;

}

/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/

/**********  Accordion.js  ***********/

/***

=========================================================
UI.Accordion - Transform a set of Divs into an accordion
=========================================================

Synopsis
========

::

    <div class="uiaccordion" id="myAccordion"/>
        <div id="element1">
            <div>First Title Bar</div>
            <div>First Titles Content</div>
        </div>
        <div id="element2">
            <div>Second Title Bar</div>
            <div>Second Titles Content</div>
        </div>
        <div id="element3">
            <div>Third Title Bar</div>
            <div>Third Titles Content</div>
        </div>
    </div>


Description
===========

UI.Accordion provides multiple or single expansion and collapsing of contents.

TODO: Enrich de expansion and collapsing of contents with visual effects and transitions.

Dependencies
============

* MochiKit_.
* :mochiref:`Widget::UI.Widget`

.. _MochiKit: http://www.mochikit.com

Overview
========

[TODO]

API Reference
=============

***/

/***
Class: UI.Accordion
-------------------

Inherits from :mochiref:`Widget::UI.Widget`.

:mochidef:`UI.Accordion(element, multipleExpansion=false)`

    Creates a new Accordion object. `element` parameter can be either an element
    or id. `multipleExpansion` flag can be omited, default value is false.


Properties
~~~~~~~~~~

:mochidef:`multipleExpansion`:

    Flag indicating which mode is on, multiple or single expansion.

***/

UI._slideUp = function(el){slideUp(el, {'queue': {'position': 'break', 
                                                  'scope': el.id}})};
UI._slideDown = function(el){slideDown(el, {'queue': {'position': 'break',
                                                      'scope': el.id}})};

UI.Accordion = function(element, multiple) {
    this._hide = UI._slideUp;
    this._show = UI._slideDown;
    bindMethods(this);
    element = element || this._defaultElement();
    if (multiple == null || typeof(multiple) == 'undefined') {
        multiple = false;
    }
    if (element) {
        this.element = $(element);
    } else {
        this.element = this._defaultElement();
    }
    this.element = $(element);
    this.multipleExpansion = multiple;
    this.elements  = filter(this._elementNode, iter(this.element.childNodes));
    var elementNode = this._elementNode;

    forEach(this.elements, function(el) {
        var content = DIV({'class': 'uiaccordioncontent'});
        //Ids are used later as effect scopes
        content.id = 'uiaccordioncontent_' + Math.random(); 
        hideElement(content);
        addElementClass(el, 'uiaccordiontitle');
        var childElements = filter(elementNode, el.childNodes);
        addElementClass(childElements[0], 'uiaccordiontitlebar');
        childElements.splice(0, 1);
        forEach(childElements, function(childEl) {
            content.appendChild(childEl);
        });
        el.appendChild(content);
    });
    this._installOnClicks();
    this.activeElements = [];
    this.cssClass = "uiaccordion";
    this.collapseAll();
    this.register();
    this.NAME = this.element.id + "(UI.Accordion)";
}

/***
Methods
~~~~~~~
***/

UI.Accordion.prototype = update(new UI.Widget(), {
/***
:mochidef:`setMultipleExpansion(flag)`:

Used for switching between multiple or single expansion.
***/
    'setMultipleExpansion': function(multiple) {
        this.multipleExpansion = multiple;
        if(!multiple && this.activeElements.length > 1)
            this.collapseAll();
    },
/***
:mochidef:`expand(element)`:

Expands the content asociated to the title. `element` parameter can be either an
element or id and must be a direct child of accordion element.

***/
    'expand': function(element) {
        var contents = filter(this._elementNode, element.childNodes);
        addElementClass(contents[0], 'uiexpanded');
        contents.splice(0, 1);
        forEach(contents, this._show);
        var index = findIdentical(this.activeElements, element);
        if(index == -1) {
            this.activeElements.push(element);
        }
        if(!this.multipleExpansion && this.activeElements.length > 1) {
            this.collapse(this.activeElements[0]);
        }
    },
/***
:mochidef:`expandAll()`:

Expands all accordion contents.

***/

    'expandAll': function() {
        if(!this.multipleExpansion) {
            logError("UI.Accordion.expandAll: Can't expand all elements if not in multipleExpansion mode");
            return;
        }
        forEach(this.elements, this.expand);
    },
/***
:mochidef:`collapse(element)`:

Collapse the content asociated to the title. `element` parameter can be either an
element or id and must be a direct child of accordion element.

***/
    'collapse': function(element) {

        var contents = filter(this._elementNode, element.childNodes);
        removeElementClass(contents[0], 'uiexpanded');
        contents.splice(0, 1); //The first element is the title, and shouldn't be hidden.
        forEach(contents, this._hide);

        var index = findIdentical(this.activeElements, element);
        if (index != -1) {
            this.activeElements.splice(index,1);
        } else {
            logWarning("UI.Accordion.collapse: collapsing a non-expanded element!?");
        }
    },
/***
:mochidef:`collapseAll()`:

Collapse all accordion contents.

***/
    'collapseAll': function() {
        forEach(extend(null, this.activeElements), this.collapse);
    },
    //FIXME: Not very useful, as accordions structure are inmutable by now.
    //       On later releases, Accordion API may be broken to make it mutable.
    '_defaultElement': function() {
        return DIV({'class': 'uiaccordion'});
    },
    '_installOnClicks': function() {
        var accordion = this;
        forEach(this._titleBars(), function(titleBar) {
            connect(titleBar,'onclick', function(e) {
                var activeElementIndex = findIdentical(accordion.activeElements,titleBar.parentNode);

                if(activeElementIndex == -1) {//Title is not active
                    accordion.expand(titleBar.parentNode);//Then we expand its content


                } else { //Title is active
                    accordion.collapse(titleBar.parentNode);//Then we collapse it
                }
            });
        });
    },
    '_elementNode': function(el) {
        return el.nodeType == 1;
    },
    '_firstChildElement': function(el) {
        return filter(this._elementNode, el.childNodes)[0];
    },
    '_titleBars': function() {
        return map(this._firstChildElement, this.elements)
    }
});

/***
Automatic widget construction details
-------------------------------------

The sintax is::


    <div class="uiaccordion" ui:multiple="true|false">
    <!-- Here goes accordion elements -->
    </div>

Where if the `ui:multiple` attribute is set to "true", the resulting accordion
will have multiple expansion enabled. By default, the multiple expansion is
false.

***/
UI.Accordion._fromElement = function(el) {
    var multiple = (getNodeAttribute(el, 'ui:multiple') == "true");
    new UI.Accordion(el, multiple);
}

/***

Authors
=======

- Lionel Olavarria. <lolavarria@imagemaker.cl>
- Leonardo Soto. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/
/**********  Calendar.js  ***********/

/***
.. title:: UI.Calendar - Calendar widget/container

=======================================
UI.Calendar - Calendar/widget container
=======================================

Synopsis
========

::

    <table class="uicalendar" ui:month="8" ui:year="2006">
    </table>
 

Description
===========

UI.Calendar is, at the same time, a simple HTML date picker widget and a 
container very useful for displaying date-based information.

Dependencies
============

* MochiKit_.
* :mochiref:`Widget::UI.Widget`.

.. _MochiKit: http://www.mochikit.com

Overview
========

[TODO]

[Calendar months goes from 1 = January to 12 = December. Note the difference 
with Date.prototype.getMonth() wich start counting from 0.

On the other hands, days of week ranges from 0 to 6. ]



API Reference
=============

***/

/***
Class UI.Calendar
-----------------

The calendar widget.

Inherits from :mochiref:`Widget::UI.Widget`.

:mochidef:`UI.Calendar(element, year=null, month=null)`

    Creates a Calendar, wrapping the `element` DOM table element. If `year` 
    *and* `month` are provided, the calendar start showing that month of that 
    year.

Properties
~~~~~~~~~~

:mochidef:`UI.Calendar.prototype.element`:

    The div element wrapped by the form. **Read-only**

:mochidef:`UI.Calendar.prototype.year`:
   
    The year shown on the calendar. **Read-only**

:mochidef:`UI.Calendar.prototype.month`:

    The year shown on the calendar. **Read-only**

:mochidef:`UI.Calendar.prototype.firstDayOfWeek`:

    The first day of the week. [FIXME doc]

:mochidef:`UI.Calendar.prototype.showHeader`
   
    Whether the calendar header (month name, year, etc) should be visible or 
    not.

Signals
~~~~~~~

:mochidef:`drawn`:

    Fired when the calendar is drawn. It happens where the month is changed,
    for example.

***/
UI.Calendar = function(element, year, month) {
    bindMethods(this);
    element = element || DIV();
    var now = new Date();
    if (isUndefinedOrNull(year)) {
	this.year = now.getFullYear();
    } else {
	this.year = year;
    }
    var now = new Date();
    if (isUndefinedOrNull(month)) {
	this.month = now.getMonth() + 1;
    } else {
	this.month = month;
    }
    this.showHeader = true;
    this.firstDayOfWeek = 0;
    this.element = $(element);
    this.table = TABLE();
    this.element.appendChild(this.table);
    this.cssClass = 'uicalendar';
    this.draw();
    this.register();
    this.NAME = this.element.id + "(UI.Calendar)";
}

/***
Static variables
~~~~~~~~~~~~~~~~

*Note: You don't want to modify this variables*.

:mochidef:`UI.Calendar.dayNames`, mochidef:`UI.Calendar.dayShortNames`:

    Arrays of strings containing the long and short names of the days of the
    week.    

***/

UI.Calendar.dayShortNames = [_('Sun'), _('Mon'), _('Thu'), _('Wed'), 
                             _('Tue'), _('Fri'), _('Sat')];

UI.Calendar.dayNames = [_('Sunday'), _('Monday'), _('Thursday'), 
                        _('Wednesday'), _('Tursday'), _('Friday'), 
                        _('Saturday')];

/***
:mochidef:`UI.Calendar.monthNames`:
    
    Array of strings containing the month names.
***/
UI.Calendar.monthNames = [_('January'), _('February'), _('March'), _('April'),
                          _('May'), _('June'), _('July'), _('August'), 
                          _('September'), _('October'), _('November'), 
                          _('December')];

/***
:mochidef:`UI.Calendar.monthDaysNormalYear`, 
:mochidef:`UI.Calendar.monthDaysLeapYear`:

    Arrays of integers containing the number of days per month in normal and
    leap years.

***/

UI.Calendar.monthDaysNormalYear =  [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 
                                    30, 31];
UI.Calendar.monthDaysLeapYear =  [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 
                                  30, 31];

UI.Calendar.SUNDAY = 0;
UI.Calendar.MONDAY = 1;
UI.Calendar.THURSDAY = 2;
UI.Calendar.WEDNESDAY = 3;
UI.Calendar.TUESDAY = 4;
UI.Calendar.FRIDAY = 5;
UI.Calendar.SATURDAY = 6;

// This methods should go onto a small library (Or maybe onto MochiKit?)
UI.Calendar._isLeapYear = function(year) {
    return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0);
};

UI.Calendar._monthDays = function(year) {
    if (UI.Calendar._isLeapYear(year)) {
        return UI.Calendar.monthDaysLeapYear;
    }
    return UI.Calendar.monthDaysNormalYear;
};

UI.Calendar._january1st = function(year) {
    return (year + 
            parseInt((year - 1) / 4) - 
            parseInt((year - 1) / 100) + 
            parseInt((year - 1) / 400)) % 7;
};

UI.Calendar._month1st = function(year, month) {
    var day = UI.Calendar._january1st(year);
    var monthDays = UI.Calendar._monthDays(year);
    for (var i = 0; i < month - 1; i++) {
        day += monthDays[i];
    }
    return day % 7;
};

UI.Calendar._monthWeeks = function(year, month, weekStartDay) {
    var weekStartDay = weekStartDay || 0;
    var monthDays = UI.Calendar._monthDays(year)[month - 1];
    var firstDay = UI.Calendar._month1st(year, month);
    firstDay = (7 + firstDay - weekStartDay) % 7;
    var firstWeekDays = (7 - firstDay);
    var weeks = Math.ceil(1 + (monthDays - firstWeekDays) / 7);
    return weeks;
};

UI.Calendar._day = function(date, firstDayOfWeek) {
    return (7 + date.getDay() - firstDayOfWeek) % 7;    
};


UI.Calendar._toPaddedEuroDate = function(d) {
    var american = toPaddedAmericanDate(d);
    var parts = american.split('/');
    return parts[1] + '/' + parts[0] + '/' + parts[2];
};

UI.Calendar.prototype = update(new UI.Widget(), {
    'draw': function() {
	var day = -1 * ((7 + UI.Calendar._month1st(this.year, this.month) - 
                         this.firstDayOfWeek) % 7);
	var headerRow = TR();
        for (var i = 0; i < 7; i++) {
            var d = (i + this.firstDayOfWeek) % 7;
            var th = TH(UI.Calendar.dayShortNames[d]);
            addElementClass(th, 'weekday' + day);
            headerRow.appendChild(th);
        }
        var header = THEAD(null, headerRow);
        var body = TBODY();
        var weeks = UI.Calendar._monthWeeks(this.year, this.month, 
                                            this.firstDayOfWeek);
        var lastDay = UI.Calendar._monthDays(this.year)[this.month - 1];
        for (var i = 0; i < weeks; i++) {
            var tr = TR();
            addElementClass(tr, 'week' + (i + 1));
            for (var j = 0; j < 7; j++) {
                var td = null;
                if (day >= 0 && day < lastDay) {
                    var numDiv = DIV(null, ++day);
                    addElementClass(numDiv, 'daynumber');
                    var contentDiv = DIV(null);
                    addElementClass(contentDiv, 'daycontent');
                    td = TD(null, numDiv, contentDiv); 
                } else {
                    td = TD();
                    ++day;
                }
                addElementClass(td, 'date_' + this.year + '_' +
                                     this.month + '_' + day);
                addElementClass(td, 
                                'weekday' + ((j + this.firstDayOfWeek) % 7));
                tr.appendChild(td);
            }
            body.appendChild(tr);        
        }
        var tableElements = [];
        if (this.showHeader) {
	    var prevMonth = SPAN({'class': 'uicalendar_prevmonth'}, "< ");
	    var nextMonth = SPAN({'class': 'uicalendar_nextmonth'}, " >"); 
	    var monthName = SPAN({'class': 'uicalendar_monthname'}, 
				 this.monthName() + " " +
				 this.year)
		
	    connect(prevMonth, 'onclick', this, 'prevMonth');
	    connect(nextMonth, 'onclick', this, 'nextMonth');
	    //TODO: Disconnect this on the next redraw
	    var caption = createDOM('CAPTION', null, 
				    prevMonth, monthName, nextMonth);
	    tableElements[tableElements.length] = caption;
        }
        tableElements[tableElements.length] = header;
        tableElements[tableElements.length] = body;
	if (this.table) {
	    removeElement(this.table);
	}
	this.table = TABLE(null, tableElements);
	appendChildNodes(this.element, this.table);
        signal(this, 'drawn');

    },
    
    'contentForDate': function(date) {
        var td = this.cellForDate(date);
        if(!td) {
            return null;
        }
        return getElementsByTagAndClassName('div', 'daycontent', td)[0];
    },

    'cellForDate': function(date) {
        return this.cellsForDateRange(date, date)[0];
    },

    //start and end are inclusive
    'cellsForDateRange': function(startDate, endDate) {
        if (startDate.getFullYear() > this.year ||
            endDate.getFullYear() < this.year ||
            (startDate.getFullYear() == this.year && 
             startDate.getMonth() + 1 > this.month) || 
            (endDate.getFullYear() == this.year && 
             endDate.getMonth() + 1 < this.month)){
		 logDebug("cellsForDateRange: range out of month");
            return [];
	} 
        if (startDate.getFullYear() < this.year ||
            (startDate.getFullYear() == this.year &&
             startDate.getMonth() + 1 < this.month)) {

	    startDate = new Date(this.year, this.month - 1, 1);
        }
        if (endDate.getFullYear() > this.year ||
            (endDate.getFullYear() == this.year &&
             endDate.getMonth() + 1 > this.month)) {
            var lastMonthDay = UI.Calendar._monthDays(this.year)[this.month];
	    endDate = new Date(this.year, this.month - 1, lastMonthDaty);
        }
        var firstDay = UI.Calendar._month1st(startDate.getFullYear(), 
                                             startDate.getMonth() + 1);
        firstDay = (7 + firstDay - this.firstDayOfWeek) % 7;
	var startDay = firstDay + startDate.getDate() - 1;
        var endDay = firstDay + endDate.getDate() - 1;
        var cal = this;
        return map(function(d) {
	   return cal.table.tBodies[0].rows[parseInt(d / 7)].cells[d % 7];        
        }, range(startDay, endDay + 1));
    },
    
    'addDateClass': function(date, cssClass) {
        addElementClass(this.cellForDate(date), cssClass);
    },

    'addDateRangeClass': function(startDate, endDate, cssClass) {
        forEach(this.cellsForDateRange(startDate, endDate), function(c) {
            addElementClass(c, cssClass);
        });
    },
    
    'removeDateClass': function(date, cssClass) {
        removeElementClass(this.cellForDate(date), cssClass);
    },
 
    'nextMonth': function() {
        var d = new Date(this.year, this.month , 1);
        this.year = d.getFullYear();
        this.month = d.getMonth() + 1;
        this.draw();
    },
    
    'prevMonth': function() {
        var d = new Date(this.year, this.month - 2, 1);
        this.year = d.getFullYear();
        this.month = d.getMonth() + 1;
        this.draw();
    },

    'monthName': function() {
	return UI.Calendar.monthNames[this.month - 1];
    }
});

/***

Automatic widget construction details
-------------------------------------

Calendars can be created using this HTML markup:


    <div class="uicalendar" ui:year="<number>" ui:month="<number>"
         ui:firstDayOfWeek="<number>" ui:showHeader="<boolean>"
    </div>

Where [TODO: Attributes explanation]

***/
UI.Calendar._fromElement = function(el) {
    var now = new Date();
    var year = getNodeAttribute(el, "ui:year");
    if (!isUndefinedOrNull(year)) {
        //Support for relative years
	if (/^[\+-]/.test(year)) {
	    year = now.getFullYear() + parseInt(year, 10);
	} else {
	    year = parseInt(year, 10);
	}
    } else {
	year = now.getFullYear();
    }
    var month = getNodeAttribute(el, "ui:month"); 
    if (!isUndefinedOrNull(month)) {
        //Support for relative months
	if (/^[\+-]/.test(month)) {
	    var monthDate = new Date(year, 
				     now.getMonth() + parseInt(month, 10),
				     1);
	    month = monthDate.getMonth() + 1;
	    year = monthDate.getFullYear();
	}
    }
    var firstDayOfWeek = getNodeAttribute(el, "ui:firstDayOfWeek");
    var showHeader = getNodeAttribute(el, "ui:showHeader");
    var cal = new UI.Calendar(el, year, month);
    if (!isUndefinedOrNull(firstDayOfWeek)) {
        cal.firstDayOfWeek = parseInt(firstDayOfWeek, 10);
    }
    if (!isUndefinedOrNull(showHeader)) {
	cal.showHeader = !(showHeader == "false");
    }
    cal.draw(); //FIXME why?
}
/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/



/**********  LightBox.js  ***********/

/***
.. title:: UI.LightBox - Cool modal windows

================================
UI.LightBox - Cool modal windows
================================

Synopsis
========

::

    <a href="javascript:w$('samplebox').show()">Show the dialog</a>
    <div class="uilightbox" id="samplebox">
        <div>Hello World!</div>
        <a href="javascript:w$('samplebox').hide()">Hide this dialog</a>
    </div>
 

Description
===========

UI.LightBox is a adaptatation of `Mochi Lightbox`_, wich in turn is a port of the 
`Lightbox Gone Wild` to MochiKit.

.. _`Mochi Lightbox`: http://projects.frogyz.com.ar/mochi-lightbox/
.. _`LightBox Gone Wild`: http://particletree.com/features/lightbox-gone-wild/

It basically provides a nice way to show modal dialogs, shadowing and 
disabling  the entire page while displaying a centered div. 
It differs from Mochi Lightbox on not requiring lightbox contents being a 
separate HTML fragment document. That allows more flexibility, as widgets or 
other dynamic contents could be placed onto the lightbox.

Dependencies
============

* MochiKit_.
* :mochiref:`Widget::UI.Widget`.

.. _MochiKit: http://www.mochikit.com

Overview
========

[TODO]


API Reference
=============

***/

/***
Class UI.LightBox
-----------------

The lightbox widget.

Inherits from :mochiref:`Widget::UI.Widget`.

:mochidef:`UI.LightBox(element)`

    Creates a Lightbox, corresponding to the `element` DOM div element. 

Properties
~~~~~~~~~~

None?

Signals
~~~~~~~

:mochidef:`shown`:

    Fired when the lightbox is made visible.

:mochidef:`hidden`:

    Fired when the lightbox is hidden.

***/

UI.LightBox = function(element) {
    bindMethods(this);
    UI.LightBox._initialize();
    element = element || DIV();
    this.element = $(element);
    this.cssClass = 'uilightbox';
    this.register();
    this.NAME = this.element.id + "(UI.LightBox)";
    appendChildNodes('uilightbox_box', this.element);
}

UI.LightBox._initialized = false;
// Is it right or should we allow multiple lightboxes per page?
UI.LightBox._initialize = function() {
    if (UI.LightBox._initialized) {
        return;
    }
    var doc = currentDocument();
    var overlay = DIV({'id':'uilightbox_overlay', 'class':'invisible'});
    var lb      = DIV({'id':'uilightbox_box', 'class':'invisible'});
    appendChildNodes(doc.body, overlay);
    appendChildNodes(doc.body, lb);
    UI.LightBox._initialized = true;
};


UI.LightBox.prototype = update(new UI.Widget(), {
    _stopEvent : function(e) {
      e.stop();
    },  
    
    show : function() {
	if (computedStyle('uilightbox_box', 'position') != 'fixed') {
            //IE and who-knows-if-some-other-browser-too don't knows about
            //fixed positions
	    this.getScroll();
	    this.prepareIE('100%', 'hidden');
	    this.setScroll(0,0);
	    this.hideSelects('hidden');
	}
        showElement(this.element);
	showElement('uilightbox_overlay');
	showElement('uilightbox_box');
    },
    
    //Workarounds and/or non ported(but working without Prototype) stuff 
    getScroll: function(){
	if (self.pageYOffset) {
	    this.yPos = self.pageYOffset;
	} else if (document.documentElement && document.documentElement.scrollTop){
	    this.yPos = document.documentElement.scrollTop; 
	} else if (document.body) {
	    this.yPos = document.body.scrollTop;
	}
    },
    setScroll: function(x, y){
	window.scrollTo(x, y); 
    },

    // Ie requires height to 100% and overflow hidden or else you can scroll down past the lightbox
    prepareIE: function(height, overflow){
    	bod = document.getElementsByTagName('body')[0];
    	bod.style.height = height;
    	bod.style.overflow = overflow;
    
    	htm = document.getElementsByTagName('html')[0];
    	htm.style.height = height;
    	htm.style.overflow = overflow; 
    },
    
    // In IE, select elements hover on top of the lightbox
    hideSelects: function(visibility){
    	selects = document.getElementsByTagName('select');
    	for(i = 0; i < selects.length; i++) {
    		selects[i].style.visibility = visibility;
    	}
    },    
    
    hide: function() {
	if (computedStyle('uilightbox_box', 'position') != 'fixed') {
            //IE and who-knows-if-other-browser-too don't knows about
            //fixed positions
	    this.setScroll(0,this.yPos);
	    this.prepareIE("auto", "auto");
	    this.hideSelects("visible");
	}
 	hideElement(this.element);
	hideElement('uilightbox_box');
	hideElement('uilightbox_overlay');
    }
});

/***

Automatic widget construction details
-------------------------------------

Lightboxes can be constructed using HTML, declaring them as follows::


    <div class="uilightbox">
     <!-- Box contents goes here -->
    </div>

In other words, it's so simple that it hasn't special attributes or structure.

***/
UI.LightBox._fromElement = function(element) {
    new UI.LightBox(element);
}
/***

Authors
=======

- Leonardo Soto M. <lsoto@imagemaker.cl>

Copyright
=========

Copyright 2005-2006 Leonardo Soto M. <leo.soto@gmail.com> and
Imagemaker IT <http://www.imagemaker.cl>.

This program is licensed under the CDDL v1.0 license, see
`<http://www.sun.com/cddl/cddl.html>`_.
***/



/**********  auto.js  ***********/

/***
Automatic Widget creation
=========================

Elements having special tagnames and classes are recognized automatically by
UI4W as widgets, and constructed on load time by the library. The following is
the correspondence between elements, css classes and widgets.

+----------+-------------+-----------------+
| Tag name | CSS class   | Widget          |
+----------+-------------+-----------------+
| div      | uislider    | UI.Slider       |
+----------+-------------+-----------------+
| div      | uitable     | UI.Table        |
+----------+-------------+-----------------+
| form     | uiform      | UI.Form         |
+----------+-------------+-----------------+
| div      | uiwindow    | UI.Window       |
+----------+-------------+-----------------+
| div      | uiaccordion | UI.Accordion    |
+----------+-------------+-----------------+
| div      | uicalendar  | UI.Calendar     |
+----------+-------------+-----------------+
| div      | uilightbox  | UI.LightBox     |
+----------+-------------+-----------------+


For details about special attributtes recognized by each widget when parsing
this special html elements, see each widget documentation.

***/
/*
addLoadEvent(function() {
    var sliders = getElementsByTagAndClassName('div', 'uislider');
    map(UI.Slider._fromElement, sliders);

    var tables = getElementsByTagAndClassName('div', 'uitable');
    map(UI.Table._fromElement, tables);

    var forms = getElementsByTagAndClassName('form', 'uiform');
    map(UI.Form._fromElement, forms);

    var windows = getElementsByTagAndClassName('div', 'uiwindow');
    map(UI.Window._fromElement, windows);

    var accordions = getElementsByTagAndClassName('div', 'uiaccordion');
    map(UI.Accordion._fromElement, accordions);

    var calendars = getElementsByTagAndClassName('div', 'uicalendar');
    map(UI.Calendar._fromElement, calendars);

    var lightboxes = getElementsByTagAndClassName('div', 'uilightbox');
    map(UI.LightBox._fromElement, lightboxes);
});
*/
