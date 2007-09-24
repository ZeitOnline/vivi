var KeywordsWidget = ObjectSequenceWidgetBase.extend({

    initialize: function() {
        arguments.callee.$.initialize.call(this);
        var new_li = LI({'class': 'new'},
                        INPUT({'type': 'button',
                               'name': 'new_keyword', 
                               'value': 'Schlüsselwort hinzufügen'})); 
        appendChildNodes(this.ul_element, new_li);
        this.drop_target = new_li;
    },

    showAddKeyword: function() {
        alert('Add-Keyword-Dialog');
    },

    handleClick: function(event) {
        var target = event.target();
        if (target.getAttribute('name') == 'new_keyword') {
            showAddKeyword();
        }
        arguments.callee.$.handleClick.call(this, event);
    },

});

