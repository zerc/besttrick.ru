/* 
 * users.views.checkins
 *
 * All about checkins views on user side
 * :copyright: (c) 2013 by zero13cool
 */

Besttrick.module('Users.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.Checkin = App.Tricks.Views.Checkin.extend({
        className: 'trick__user',
        tagName: 'tr',
        template: '#user_page_checkin'
    });

    Views.Checkins = App.Tricks.Views.Checkins.extend({
        itemView: Views.Checkin,
    });
});
