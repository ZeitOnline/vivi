// Copyright (c) 2007-2011 gocept gmbh & co. kg
// See also LICENSE.txt
// $Id$

zeit.cms.PanelHandler = gocept.Class.extend({

    construct: function(base_url) {
        this.url = base_url + '/panel_handlers';
    },

    registerPanelHandlers: function() {
        var panels = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'panel', 'sidebar');
        this.resizePanels(panels);
        this.registerFoldHandlers(panels);
        MochiKit.Signal.connect(
            'sidebar', 'panel-content-changed', this, this.resizeAllPanels);
        MochiKit.DOM.addElementClass('sidebar', 'sized');
    },

    resizeAllPanels: function() {
        MochiKit.Signal.signal('sidebar', 'zeit.cms.RememberScrollStateEvent');
        var panels = MochiKit.DOM.getElementsByTagAndClassName(
            'div', 'panel', 'sidebar');
        // Reset
        forEach(panels, function(panel) {
            var content_element = MochiKit.DOM.getFirstElementByTagAndClassName(
                'div', 'PanelContent', panel);
            if (!isNull(content_element)) {
                MochiKit.Style.setStyle(content_element, {'height': ''});
            }
        });
        this.resizePanels(panels);
        MochiKit.Signal.signal('sidebar', 'zeit.cms.RestoreScrollStateEvent');
    },

    resizePanels: function(panels) {
        var max_height = MochiKit.Style.getElementDimensions(
            'sidebar', true).h;
        var fixed_space = 0;
        var flex_sum = 0;

        // Compute flex_sum and fixed_space
        forEach(panels, function(panel) {
            // XXX: getAttributeNS doesn't work :(
            var flex = panel.getAttribute('panel:flex');
            var fixed;
            if (flex) {
                var content_element = getFirstElementByTagAndClassName(
                    'div', 'PanelContent', panel);
                panel._flex = new Number(flex);
                flex_sum += panel._flex;
                fixed = panel.clientHeight - content_element.clientHeight;
            } else {
                // A non flexible panel will not be shrunk
                fixed = panel.clientHeight;
            }
            log(panel.id, 'fixed =', fixed, 'flex =', flex);
            fixed_space += fixed;
        });

        // Fix up flex / fixed_space for not making panels larger than they'd
        // need to be
        var continue_ = true;
        while (continue_) {
            continue_ = false;
            log("Max height", max_height);
            log("Fixed space", fixed_space);
            var available_space = max_height - fixed_space;
            log("Available space", available_space);
            var space_per_flex = available_space / flex_sum;
            log("space per flex", space_per_flex, available_space, flex_sum);

            forEach(panels, function(panel) {
                if (panel._flex) {
                    var content_element = getFirstElementByTagAndClassName(
                        'div', 'PanelContent', panel);
                    var new_height = panel._flex * space_per_flex;
                    if (new_height >= content_element.clientHeight) {
                        flex_sum -= panel._flex;
                        fixed_space += content_element.clientHeight;
                        panel._flex = null;
                        continue_ = true;
                        log('Panel does not exceed flex size:', panel.id,
                            new_height);
                        throw MochiKit.Iter.StopIteration;
                    }
                }
            });
        }

        // Finally set the sizes
        forEach(panels, function(panel) {
            if (panel._flex) {
                var content_element = getFirstElementByTagAndClassName(
                    'div', 'PanelContent', panel);
                // compute padding and remove px from padding;
                // NOTE: this is quite expensive, maybe we can work around
                // calling getStyle somehow?
                var padding_top = MochiKit.Style.getStyle(
                    content_element, 'padding-top').slice(0, -2);
                var padding_bottom = MochiKit.Style.getStyle(
                    content_element, 'padding-bottom').slice(0, -2);
                var padding = (
                    new Number(padding_top) + new Number(padding_bottom));

                var height = panel._flex * space_per_flex - padding;
                log("Sizing", panel.id, "at", height, "flex =", panel._flex);
                MochiKit.Style.setStyle(
                    content_element, {'height': height + 'px'});
            }
        });
    },

    registerFoldHandlers: function(panels) {
        var self = this;
        forEach(panels, function(panel) {
            var foldmarker = MochiKit.DOM.getFirstElementByTagAndClassName(
                'h1', null, panel)
            if (isNull(foldmarker)) {
                return; // continue
            }
            MochiKit.Signal.connect(foldmarker, "onclick", function(event) {
                if (event.target() != foldmarker) {
                    return;
                }
                var new_state;
                if (hasElementClass(panel, 'folded')) {
                    removeElementClass(panel, 'folded');
                    addElementClass(panel, 'unfolded');
                } else {
                    removeElementClass(panel, 'unfolded');
                    addElementClass(panel, 'folded');
                }
                self.resizeAllPanels();
                self.storeState(panel.id);
            });
            var content_element = getFirstElementByTagAndClassName(
                'div', 'PanelContent', panel);
            var scroll_state = new zeit.cms.ScrollStateRestorer(
                content_element);
            scroll_state.connectWindowHandlers();
            connect(
                'sidebar', 'zeit.cms.RememberScrollStateEvent',
                scroll_state, 'rememberScrollState');
            connect(
                'sidebar', 'zeit.cms.RestoreScrollStateEvent',
                scroll_state, 'restoreScrollState');


        });

    },

    storeState: function(panel_id) {
        doSimpleXMLHttpRequest(this.url, {toggle_folding: panel_id});
    },

});



// Handler to close and open the sidebar making more space for the actual
// content area.

function SidebarDragger(base_url) {
    this.url = base_url + '/@@sidebar_folded';
    this.observe_ids = new Array('sidebar', 'sidebar-dragger',
        'visualContentSeparator', 'visualContentWrapper', 'header');
}

SidebarDragger.prototype = {

    classes: ['sidebar-folded', 'sidebar-expanded'],

    toggle: function(event) {
        var self = this;
        var folded = ! hasElementClass('sidebar', 'sidebar-folded');
        var d = doSimpleXMLHttpRequest(this.url, {folded: folded});
        d.addCallback(function(result) {
            var css_class = result.responseText;
            self.setClass(css_class);
        });
    },

    hide: function() {
        var self = this;
        self.setClass('sidebar-folded');
    },

    setClass: function(css_class) {
        var self = this;
        forEach(this.observe_ids,
            function(element_id) {
              forEach(self.classes, function(cls) {
                  var element = getElement(element_id);
                  removeElementClass(element, cls);
                  });
        var element = getElement(element_id);
        addElementClass(element, css_class);
        });
    },
}
