var CalendarDayDND = Class.extend({

    construct: function(base_url, id) {
        this.base_url = base_url;
        this.contentElement = getElement(id);

        var cal_dnd = this;
        new Droppable(this.contentElement, {
            hoverclass: 'calendar-drop-hover',
            ondrop: function(element, last_active_element, event) {
                cal_dnd.handleDrop(element);
            },
        });
    },

    handleDrop: function(element) {
        var keys = ['form.related.0.', 
                    'form.related.count'];
        var values = [element.uniqueId,  1];

        var qs = queryString(keys, values);

        // redirect
        window.location = this.base_url + '&' + qs
    },

})

