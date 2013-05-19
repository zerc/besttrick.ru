/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Глобальный лоадер. Используется для показа "занятости"
 * приложения. Например, если при переходе по страницам будет
 * затуп - покажется лоадер - чтобы пользователь не паниковал.
 */
var Loader = function() {
    var win          = $(window),
        doc          = $(document),
        overflow_div = $('div.global_overflow'),
        loader_div   = $('div.global_loader');

    overflow_div.height(win.height());
    
    this.show = function() {
        overflow_div.show();
        loader_div.show(); 
    }

    this.hide = function() {
        overflow_div.hide(); 
        loader_div.hide (); 
    }
}

/*
 * Роутер, осуществляющий инициализацию и руление приложением.
 */

var App = Backbone.Router.extend({
    routes: {
        ''                           : 'index',
        '!'                          : 'fresh_index',
        '!u'                         : 'my',
        '!trick:trick'               : 'trick',
        '!users/user:user_id'        : 'profile',
        'filter=:tags_selected'      : 'filter', // no index for search engines
        '!about'                     : 'about',
        '!users/rating'              : 'top_users',
        
        '!u/achives'                 : 'achives',
        '!users/user:user_id/achives': 'achives'
    },

    initialize: function (args) {
        var self = this,
                        
            tmp_trick_cookie_name = window.BTCommon.vars.tmp_trick_cookie_name,
            next_name = window.BTCommon.vars.next_url_cookie_name;

        this.user = args.user ? new UserModel(args.user) : false;
        this.tricks = window.BTTricks.tricks = new TricksList(args.tricks);

        this.default_page_title = window.document.title;
        this.active_route = 'route:index';

        /*
         * Работаем с сессиоными куками 
         * чекиним пользователя, редиректим на страницу откуда логинился и пр.
         * хоть куки и сессионные - удалим их руками для подстраховки:
         * Chrome 19 у меня сохранял сессионныю куку после перезапуска
         */
        if (this.user && $.cookie(tmp_trick_cookie_name)) {
            $.cookie(tmp_trick_cookie_name, null);
        }

        if ($.cookie(next_name)) {
            location.hash = decodeURIComponent($.cookie(next_name));
            $.cookie(next_name, null);
        }

        this.$el        = $('div.content');

        this.loginView  = new Login({user: this.user});
        this.tricksView = new TricksView({tricks: this.tricks, tags: args.tags, user: this.user});
        this.trickFull  = new TrickFullView({user: this.user});
        this.feedback   = new FeedBack({user: this.user});
        this.loader     = new Loader();
        this.achives    = new window.BTAchives.AchivesView();
        
        // Общие действия при переходе по страницам
        this.bind('all', function (a, b, c) {
            self.active_route = a;
            self.feedback.hide();
            remove_tooltips();
            $('div.content').attr('class', 'content'); // обнулим все навешаенные на главный див стили

            // google analytics event push
            if (/#!/.test(location.hash)) _gaq.push(['_trackPageview', '/' + location.hash]);
        });
        
        window.BTCommon.on('ajax_done render_done', this.callbacks, this);        
        Backbone.history.start();
    },

    route: function(route, name, callback) {
        var f = callback || this[name],
            self = this;

        return Backbone.Router.prototype.route.call(this, route, name, _.wrap(f, function (f, args) {
            self.loader.show();
            return f.call(self, args);
        }));
    },

    callbacks: function () {
        this.loader.hide();
    },

    achives: function (user_id) {
        var self = this;
        this.achives.collection.user_id = user_id;
        this.achives
            .reset_filter().base_render()
            .collection.fetch({
            success: function () {
                self.achives.render();
                window.BTCommon.trigger('render_done');
            }
        });
    },

    top_users: function () {
        var self = this,
            template = new EJS({url: '/static/templates/top_users.ejs'});        

        window.BTCommon.ajax(this, {
            url: '/users/rating/',
            dataType: 'json',
            success: function (response) {
                self.$el.html(template.render({
                    users: new window.BTUsers.UsersCollection(response.users)
                }));
            },
            error: function () { alert('Network error'); }
        });
    },

    about: function () {
        var template = new EJS({url: '/static/templates/about.ejs'});
        this.$el.html(template.render());
        window.BTCommon.trigger('render_done');
    },

    filter: function (tags_selected) {
        this.tricksView.filter(tags_selected);
        this.index();
    },

    my: function () {
        if (!this.user) return this.navigate('', {trigger: true});

        var view = new UserView({
            model  : this.user, 
            tricks : new TricksList(this.tricks.filter(function (t) { return t.get('user_do_this'); })) 
        });

        view.render();
        window.BTCommon.trigger('render_done');
    },

    profile: function (user_id) {
        window.BTCommon.ajax(this, {
            url: '/users/user'+user_id+'/',
            dataType: 'json',
            success: function (response) {
                var profile    = new UserProfile({
                        model  : new UserModel(response.user),
                        tricks : new window.BTTricks.TricksList(response.tricks)
                    });

                return profile.render();
            }
        });
    },

    index: function (tags_selected) {
        window.document.title = this.default_page_title;
        this.tricksView.render();
        window.BTCommon.trigger('render_done');
    },

    fresh_index: function () {
        var self = this;
        this.tricksView.reset_filter();
        this.tricksView.collection.fetch({success: function () {
            self.index();
        }});
    },

    trick: function (trick_id) {
        var trick = this.tricksView.collection.get(trick_id);        
        this.trickFull.render({model: trick});
    }
});
