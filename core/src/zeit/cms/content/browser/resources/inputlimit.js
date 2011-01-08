// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

zeit.cms.InputValidation = Class.extend({

    construct: function(field_name) {
        this.input = $(field_name);
        this.notify_div = getFirstElementByTagAndClassName(
            'div', 'show-input-limit', this.input.parentNode);
        this.max_length = getNodeAttribute(this.notify_div, 'maxlength');
        this.timer = null;

        replaceChildNodes(
            this.notify_div,
            SPAN({class: 'current-length'}, this.input.value.length),
            '/',
            SPAN({class: 'max-length'}, this.max_length));
        this.current_length = getFirstElementByTagAndClassName(
            'span', 'current-length', this.notify_div);

        connect(this.input, 'onkeyup', this, 'check_length');
        connect(this.input, 'onchange', this, 'check_length');
    },

    check_length: function(event) {
        if (this.input.value.length > this.max_length)
            this.input.value = this.input.value.substring(0, this.max_length);

        if (this.timer != null) {
            this.timer.cancel();
        }
        this.timer = callLater(0.4, this.update_notification, this);
    },

    update_notification: function(self) {
        self.current_length.innerHTML = self.input.value.length;
    },

});
