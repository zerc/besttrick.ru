/*
 * Besttrick application here
 */

// Common
if (typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, ''); 
    }
};


var Besttrick = new Backbone.Marionette.Application();

Besttrick.addRegions({
    header : '#header',
    main   : '#main',
    footer : '#footer',
    user_container : '#user_container',
    menu_container : '#menu_container'
});


Besttrick.on('initialize:after', function(){
  Backbone.history.start();
});


Besttrick.module('Main', function (Main, App, Backbone, Marionette, $, _) {
    Main.Router = Marionette.AppRouter.extend({
        appRoutes : {
            '': 'index_page',
            '!': 'index_page',
            'filter=:tags_selected': 'index_page',
            '!trick:trick': 'trick_page',
            '!u': 'user_page',
            '!users/user:user_id': 'user_profile_page',
            '!users/rating' : 'users_rating'
        }
    });

    Main.Controller = function (tricks, tags, user) {
        user ? App.user_container.show(new App.Users.Views.UserBar({model: user}))
             : App.user_container.show(new App.Users.Views.LoginBar());

        this.user_profile_page = function (user_id) {
            var user = new App.Users.Models.User({id: user_id});
            App.menu_container.reset();
            user.fetch({
                success: function (model) {
                    App.main.show(new App.Users.Views.UserProfile({model: model}));
                }
            });
        },

        this.user_page = function () {
            if (!user) App.router.navigate('!');
            App.menu_container.reset();
            App.main.show(new App.Users.Views.User({model: user}))
        },

        this.users_rating = function () {
            var users = new App.Users.Models.Users();
            App.menu_container.reset();
            users.fetch({
                data: 'sort=rating,1',
                success: function (collection) {
                    App.main.show(new App.Users.Views.UsersRating({
                        collection: collection
                    }));
                }
            })
        },

        this._parse_filter_query = function (querystring) {
            if (!querystring) return;

            var tags_ids = querystring.split(','),
                filter_tricks_ids = [];

            _.each(tags_ids, function (ti) { 
                filter_tricks_ids = _.union(tags[ti]['tricks'], filter_tricks_ids); 
            });

            return filter_tricks_ids;
        },

        this.index_page = function (querystring) {
            var view_tricks = new App.Tricks.Views.Tricks({collection: tricks}),
                view_filter = new App.Tricks.Views.TricksFilter({templateHelpers: {'tags': tags}});

            view_tricks.set_filter(this._parse_filter_query(querystring), true);               

            App.menu_container.show(view_filter);
            App.main.show(view_tricks);
        },

        this.trick_page = function (trick_id) {
            var model = tricks.get(trick_id),
                trick_view = new App.Tricks.Views.TrickPage({model: model});
            if (!model) return false;
            App.main.show(trick_view);
            App.menu_container.reset();
        }
    }

    App.addInitializer(function (options) {
        var tricks = new this.Tricks.Models.Tricks(options.tricks),
            tags = options.tags,
            user = options.user ? new App.Users.Models.User(options.user) : false;

        /*
         * If we have next_url in cookies - set this and go
         */
        if ($.cookie(App.Common.Vars.next_url_cookie_name)) {
            location.hash = decodeURIComponent($.cookie(App.Common.Vars.next_url_cookie_name));
            $.cookie(App.Common.Vars.next_url_cookie_name, null);
        }

        this.router = new Main.Router({
            controller: new Main.Controller(tricks, tags, user)
        });

        App.Common.init_feedback(options.feedback_opts, user);
    });
});
