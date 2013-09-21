/* 
 * users.views.checkins
 *
 * All about checkins views on user side
 * :copyright: (c) 2013 by zero13cool
 */

Besttrick.module('Users.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.Checkins = App.Tricks.Views.Checkins.extend({
        get_middle_side_content: function (model) {
            return {
                href: model.get('trick').get_href(),
                title: model.get('trick').get_title()
            }
        },
        get_middle_side_hint: function (model) {},
        get_right_side: function (model) {
            return '<img src="' + model.get('trick').get_thumb() + '" />';
        }
    });
});
