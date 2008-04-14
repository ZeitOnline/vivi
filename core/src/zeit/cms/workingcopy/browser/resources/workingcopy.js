// $Id$

connect(window, 'onload', function(event) {
    forEach(getElementsByTagAndClassName('tr', null, 'workingcopycontents'),
            function(row) {
                new Draggable(row, {
                    starteffect: null,
                    endeffect: null});
          });
                
});
