/*
 * Users rating page
 */

Besttrick.module('Users.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.UsersRating = App.Common.ItemsView.extend({
        get_left_side: function (model) {
            return model.get('rating');
        },

        get_middle_side_content: function (model) {
            return {
                href: model.get_profile_url(),
                title: model.get('nick')
            }
        },

        get_right_side: function (model) {
            return '<img width="50" src="' + model.get("photo") + '" />';
        }
    });
});
