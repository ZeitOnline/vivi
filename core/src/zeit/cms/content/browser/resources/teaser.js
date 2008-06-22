var TeaserCopy = Class.extend({
    construct: function(source, target) {
        this.source = source;
        this.target = target;
        
        if ($(source) == undefined | $(target) == undefined) {
            return;
        }

        connect(source, 'onkeyup', this, 'copy_text');
        connect(target, 'onfocus', this, 'mark_changed');

    },

    copy_text: function(event) {
        var target = $(this.target);
        if (target.value == '') {
            target.can_copy_text = true;
        } else if (!target.can_copy_text) {
            return;
        }

        target.value = $(this.source).value
        signal(target, 'onchange');
    },

    mark_changed: function(event) {
       $(this.target).can_copy_text = false; 
    },

});


connect(window, 'onload', function(event) {
    new TeaserCopy('form.title', 'form.teaserTitle');
    new TeaserCopy('form.supertitle', 'form.shortTeaserTitle');
    new TeaserCopy('form.subtitle', 'form.teaserText');
    new TeaserCopy('form.title', 'form.shortTeaserText');
})

