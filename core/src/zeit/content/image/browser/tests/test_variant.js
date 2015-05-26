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
            this.slider = $('<div id="slider"/>');
            $('body').append(this.container);
            $('body').append(this.slider);

            // Mock AJAX calls to return hard coded response
            spyOn($, 'ajax').andCallFake(function (options) {
                var d = $.Deferred(),
                    response = {
                        focus_x: 0.5,
                        focus_y: 0.5,
                        zoom: 0.3,
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
            this.slider.remove();
        });

        it("should display circle relative to given focus point", function () {
            var self = this;
            runs(function() {
                expect(self.view.circle.position()).toEqual({left: 110, top: 62});
            });
        });

        it("should save focus point after drag", function () {
            var self = this;
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "save").andCallThrough();
                self.view.circle.css('left', '55px');
                self.view.circle.css('top', '31px');
                self.view.circle.trigger('dragstop');
                expect(spy).toHaveBeenCalledWith(
                    {"focus_x": 0.25, "focus_y": 0.25});
            });
        });

        it("should display stored zoom value on load", function() {
            runs(function() {
                expect($('#slider').slider('value')).toEqual(30);
            });
        });

        it("should store zoom value on change", function() {
            runs(function() {
                var spy = spyOn(Backbone.Model.prototype, "save").andCallThrough();
                $('#slider').slider('value', 60);
                expect(spy).toHaveBeenCalledWith({zoom: 0.6});
            });
        });
    });
}(jQuery));
