// $Id$

zeit.cms.workingcopy = {}

zeit.cms.workingcopy.event_id = connect(
    window, 'onload', function(event) {
        var event_id = connect(
            'workingcopycontents', 'onmouseover', function(event) {
                forEach(getElementsByTagAndClassName(
                    'tr', null, 'workingcopycontents'),
                        function(row) {
                            new Draggable(row, {
                                starteffect: null,
                                endeffect: null});
                      });
                disconnect(event_id);
            });
    disconnect(zeit.cms.workingcopy.event_id);
});
