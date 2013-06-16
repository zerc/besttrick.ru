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
            'filter=:tags_selected': 'filter',
            '!trick:trick': 'trick_page',
            '!u': 'user_page',
        }
    });

    Main.Controller = function (tricks, tags, user) {
        var view_tricks = new App.Tricks.Views.Tricks({collection: tricks}),
            view_filter = new App.Tricks.Views.TricksFilter({templateHelpers: {'tags': tags}});

        user ? App.user_container.show(new App.Users.Views.UserBar({model: user}))
             : App.user_container.show(new App.Users.Views.LoginBar());

        this.user_page = function () {
            if (!user) App.router.navigate('!');
            App.menu_container.reset();
            App.main.show(new App.Users.Views.User({model: user}))
        },

        this._render_index = function () {
            App.menu_container.show(view_filter);
            App.main.show(view_tricks);
        },

        this.filter = function (tags_querystring) {
            var tags_ids = tags_querystring.split(','),
                filter_tricks_ids = [];

            _.each(tags_ids, function (ti) { 
                filter_tricks_ids = _.union(tags[ti]['tricks'], filter_tricks_ids); 
            });
            
            if (App.main.currentView !== view_tricks) { 
                view_tricks.set_filter(filter_tricks_ids, false);
                this._render_index();
            } else {
                view_tricks.set_filter(filter_tricks_ids, true);
            }
        },

        this.index_page = function () {
            view_tricks.set_filter();
            this._render_index();
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
    });
});
