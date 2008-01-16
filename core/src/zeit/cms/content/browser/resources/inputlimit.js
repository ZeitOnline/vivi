// Copyright (c) 2007-2008 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

zeit.cms.InputValidation = Class.extend({

    construct: function(field_name) {
        this.input = $(field_name);
        this.notify_div = getFirstElementByTagAndClassName(
            'div', 'show-input-limit', this.input.parentNode);
        this.max_length = getNodeAttribute(this.notify_div, 'maxlength');

        connect(this.input, 'onkeyup', this, 'check_length');
        connect(this.input, 'onchange', this, 'check_length');

    },

    check_length: function(event) {
        if (this.input.value.length > this.max_length) {
            this.input.value = this.input.value.substring(0, this.max_length);
        }
    },

});
