jQuery(document).ready(function(){
    function create_sortable(element, onUpdate) {
        MochiKit.Sortable.create(element, {
            handle: 'handle',
            ghosting: true,
            onUpdate
        })
        MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'start', ({element}) => {
            element.classList.add('sortable-dragging')
        })
        MochiKit.Signal.connect(MochiKit.DragAndDrop.Draggables, 'end', ({element}) => {
            element.classList.remove('sortable-dragging')
            element.style = ""
        })
    }

    const list = document.querySelector('.gallery-overview');
    if (!list) return;

    // Trigger InlineForm setup
    MochiKit.Signal.signal(window, 'script-loading-finished', self);
    create_sortable(list, () => {
        list.classList.add('dirty');
        const entries = Array.from(list.querySelectorAll('[data-entry-name]')).map(e => e.dataset.entryName);
        const d = zeit.cms.locked_xhr(document.location, {
            'method': 'POST',
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'sendContent': 'form.actions.save_sorting&' + entries.map(v => `images:list=${v}`).join('&'),
        });
        d.addCallbacks(result => {
            list.classList.remove('dirty');
            list.classList.add('submitted-successfully');
            setTimeout(() => list.classList.remove('submitted-successfully'), 2500);
        }, error => {
            alert('Ein Systemfehler ist aufgetreten: ' + error.req.responseText);
        });
    });
});
