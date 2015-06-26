/*global expect, describe, it, beforeEach, spyOn, afterEach, runs, waitsFor */
/*global Backbone, jQuery, zeit*/
(function ($) {
    "use strict";

    describe("Focuspoint Test", function () {
        beforeEach(function() {
            var self = this,
                flag = false;

            // Create temporary DOM
            this.container = $('<div id="variant-inner" style="width: 220px"/>');
            $('body').append(this.container);

            // Mock AJAX calls to return hard coded response
            spyOn($, 'ajax').andCallFake(function (options) {
                var d = $.Deferred(),
                    response = {
                        focus_x: 0.5,
                        focus_y: 0.5,
                        zoom: 0.3,
                        is_default: true,
                        url: '/fanstatic/zeit.content.image.test/master_image.jpg'
                    };
                d.resolve(response);
                options.success(response);
                return d.promise();
            });

            // Setup Editor and wait that it was rendered
            self.view = new zeit.content.image.browser.VariantEditor();

            runs(function() {
                self.view.on('render', function() {
                    flag = true;
                });
                self.view.prepare();
            });

            waitsFor(function () {
                return flag;
            }, "VariantEditor did not render", 500);
        });

        afterEach(function () {
            this.container.remove();
        });

        it("should display circle relative to given focus point", function () {
            var self = this;
            runs(function() {
                expect(self.view.focuspoint.position()).toEqual({left: 110, top: 62});
            });
        });

        it("should save focus point after drag", function () {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "save").andCallThrough();
                self.view.focuspoint.css('left', '55px');
                self.view.focuspoint.css('top', '31px');
                self.view.focuspoint.trigger('dragstop');
                expect(spy).toHaveBeenCalledWith(
                    {"focus_x": 0.25, "focus_y": 0.25, "zoom": 0.3}
                );
            });
        });

        it("should display stored zoom value on load", function() {
            var self = this;
            runs(function() {
                expect(self.view.zoom_bar.slider('value')).toEqual(30);
            });
        });

        it("should store zoom value on change", function() {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "save").andCallThrough();
                self.view.zoom_bar.slider('value', 60);
                self.view.zoom_bar.trigger('slidestop');
                expect(spy).toHaveBeenCalledWith(
                    {"focus_x": 0.5, "focus_y": 0.5, "zoom": 0.6}
                );
            });
        });
    });
}(jQuery));
