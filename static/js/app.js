/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Глобальный лоадер. Используется для показа "занятости"
 * приложения. Например, если при переходе по страницам будет
 * затуп - покажется лоадер - чтобы пользователь не паниковал.
 */
var Loader = function() {
    var overflow_div = $('div.global_overflow'),
        loader_div = $('div.global_loader'),
        win = $(window);

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
        '!trick/:trick'              : 'old_trick', // старый урл
        '!profile-:user_id'          : 'profile',
        'filter=:tags_selected'      : 'filter', // no index for search engines
        '!about'                     : 'about',
        '!top'                       : 'top_users'
    },

    initialize: function (args) {
        var self = this,
            userModel = args.user ? new UserModel(args.user) : false;
            tricks = new TricksList(args.tricks),
            
            tmp_trick_cookie_name = window.BTCommon.vars.tmp_trick_cookie_name,
            next_name = window.BTCommon.vars.next_url_cookie_name;

        this.default_page_title = window.document.title;
        this.active_route = 'route:index';

        /*
         * Работаем с сессиоными куками 
         * чекиним пользователя, редиректим на страницу откуда логинился и пр.
         * хоть куки и сессионные - удалим их руками для подстраховки:
         * Chrome 19 у меня сохранял сессионныю куку после перезапуска
         */
        if (userModel && $.cookie(tmp_trick_cookie_name)) {
            $.cookie(tmp_trick_cookie_name, null);
        }

        if ($.cookie(next_name)) {
            location.hash = decodeURIComponent($.cookie(next_name));
            $.cookie(next_name, null);
        }

        this.$el        = $('div.content');
        this.user       = userModel ? new UserView({model: userModel}) : false;
        this.profile    = new UserProfile();
        this.loginView  = new Login({user: userModel});
        this.tricksView = new TricksView({tricks: tricks, tags: args.tags, user: userModel});
        this.trickFull  = new TrickFullView({user: userModel});
        this.feedback   = new FeedBack({user: userModel});
        this.loader     = new Loader();

        // Общие действия при переходе по страницам
        this.bind('all', function (a, b, c) {
            self.active_route = a;
            self.feedback.hide();
            remove_tooltips();
            $('div.content').attr('class', 'content'); // обнулим все навешаенные на главный див стили

            // google analytics event push
            if (/#!/.test(location.hash)) _gaq.push(['_trackPageview', '/' + location.hash]);
        });

        Backbone.history.start();
    },

    top_users: function () {
        var self = this,
            template = new EJS({url: '/static/templates/top_users.ejs'});
        
        self.loader.show();

        $.ajax({
            url: '/rating/',
            dataType: 'json',
            success: function (response) {
                self.$el.html(template.render(response));
                self.loader.hide();
            },
            error: function () {
                alert('Network error');
                self.loader.hide();
            }
        });
    },

    about: function () {
        this.loader.show();

        var template = new EJS({url: '/static/templates/about.ejs'});
        this.$el.html(template.render());

        this.loader.hide();
    },

    filter: function (tags_selected) {
        this.tricksView.filter(tags_selected);
        this.index();
    },

    my: function () {
        if (this.user) {
            this.loader.show();
            this.user.render();
            this.loader.hide();
        } else {
            this.navigate('', {trigger: true});
        }
    },

    index: function (tags_selected) {
        this.loader.show();

        window.document.title = this.default_page_title;
        this.tricksView.render();

        this.loader.hide();
    },

    fresh_index: function () {
        var self = this;
        this.tricksView.reset_filter();
        this.tricksView.collection.fetch({success: function () {
            self.index();
            self.loader.hide();
        }});
    },

    profile: function (user_id) {
        this.loader.show();
        this.profile.render(user_id);
        this.loader.hide();
    },

    trick: function (trick_id) {
        this.loader.show();
        var trick = this.tricksView.collection.get(trick_id);
        this.loader.hide();
        return this.trickFull.render({model: trick});
    },

    old_trick: function (trick_id) {
        var mapping = {
            'kazachok-f'    : 0,
            'korean-spin'   : 1,
            'russian-spin'  : 2,
            'chicken-leg-b' : 3,
            'toe-machine'   : 4,
            'day-night'     : 5,
            'footgun-toe-f' : 6,
            'onewheel-f'    : 7,
            'confraglide'   : 8,
            'cobra-b'       : 9,
            'seven-f'       : 10,
            'no-wiper'      : 11,
            'foot-spin'     : 12
        };

        return this.trick(mapping[trick_id]);
    }
});
