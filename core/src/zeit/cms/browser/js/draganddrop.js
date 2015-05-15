(function() {

// Monkey-patch to use a dict instead of a list, which allows for faster
// removal of entries.

MochiKit.DragAndDrop.Droppables._drops = {};
MochiKit.DragAndDrop.Droppables._drop_id = 0;

MochiKit.DragAndDrop.Droppables.register = function(drop) {
    this.drops.push(drop);
    this._drop_id += 1;
    this._drops[this._drop_id] = drop;
    drop._id = this._drop_id;
};

MochiKit.DragAndDrop.Droppables.unregister = function(drop) {
    delete this._drops[drop._id];
    this.drops = [];
    var keys = Object.keys(this._drops);
    for (var i = 0; i < keys.length; i++) {
        this.drops.push(this._drops[keys[i]]);
    }
};

MochiKit.DragAndDrop.Droppables.remove = function(element) {
    element = MochiKit.DOM.getElement(element);
    var remove_keys = [];
    var keys = Object.keys(this._drops);
    for (var i = 0; i < keys.length; i++) {
        if (this._drops[keys[i]].element == element) {
            remove_keys.push(keys[i]);
        }
    }

    for (i = 0; i < remove_keys.length; i++) {
        this.unregister(this._drops[remove_keys[i]]);
    }
};


MochiKit.DragAndDrop.Draggables._drags = {};
MochiKit.DragAndDrop.Draggables._drag_id = 0;

MochiKit.DragAndDrop.Draggables.register = function(draggable) {
    if (this.drags.length === 0) {
        var conn = MochiKit.Signal.connect;
        this.eventMouseUp = conn(document, 'onmouseup', this, this.endDrag);
        this.eventMouseMove = conn(document, 'onmousemove', this,
                                   this.updateDrag);
        this.eventKeypress = conn(document, 'onkeypress', this,
                                  this.keyPress);
    }
    this.drags.push(draggable);
    this._drag_id += 1;
    this._drags[this._drag_id] = draggable;
    draggable._id = this._drag_id;
};

MochiKit.DragAndDrop.Draggables.unregister = function(draggable) {
    delete this._drags[draggable._id];
    this.drags = [];
    var keys = Object.keys(this._drags);
    for (var i = 0; i < keys.length; i++) {
        this.drags.push(this._drags[keys[i]]);
    }

    if (this.drags.length === 0) {
        var disc = MochiKit.Signal.disconnect;
        disc(this.eventMouseUp);
        disc(this.eventMouseMove);
        disc(this.eventKeypress);
    }
};


// Monkey-patch to deactivate last active droppable only if it is not affected
// anymore (this allows landing zones to enlarge on hover and stay that way
// until mouseout, for example).

MochiKit.DragAndDrop.Droppables.show = function (point, element) {
    if (!this.drops.length) {
        return;
    }
    var affected = [];

    // This is the only changed line, everything else is copy&paste, sigh.
    if (this.last_active && !this.last_active.isAffected(point, element)) {
        this.last_active.deactivate();
    }
    MochiKit.Iter.forEach(this.drops, function (drop) {
        if (drop.isAffected(point, element)) {
            affected.push(drop);
        }
    });
    if (affected.length > 0) {
        var drop = this.findDeepestChild(affected);
        MochiKit.Position.within(drop.element, point.page.x, point.page.y);
        drop.options.onhover(element, drop.element,
            MochiKit.Position.overlap(drop.options.overlap, drop.element));
        drop.activate();
    }
};


}());
