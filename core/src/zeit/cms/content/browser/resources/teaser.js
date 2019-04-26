var TeaserCopy = gocept.Class.extend({
    construct: function(source, target) {
        this.source = source;
        this.target = target;

        if ($(source) == undefined | $(target) == undefined) {
            return;
        }

        MochiKit.Signal.connect(source, 'onkeyup', this, 'copy_text');
        MochiKit.Signal.connect(target, 'onfocus', this, 'mark_changed');

    },

    copy_text: function(event) {
        var target = $(this.target);
        if (target.value == '') {
            target.can_copy_text = true;
        } else if (!target.can_copy_text) {
            return;
        }

        target.value = $(this.source).value;
        MochiKit.Signal.signal(target, 'onchange');
    },

    mark_changed: function(event) {
       $(this.target).can_copy_text = false;
    }

});


MochiKit.Signal.connect(window, 'onload', function(event) {
    new TeaserCopy('form.title', 'form.teaserTitle');
    new TeaserCopy('form.subtitle', 'form.teaserText');
});

