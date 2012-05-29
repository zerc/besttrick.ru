/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

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
        '!filter=:tags_selected'     : 'filter',
        '!about'                     : 'about',
        '!top'                       : 'top_users'
    },

    initialize: function (args) {
        var self = this,
            userModel = args.user ? new UserModel(args.user) : false;

        this.default_page_title = window.document.title;

        this.$el        = $('div.content');
        this.user       = userModel ? new UserView({model: userModel}) : false;
        this.profile    = new UserProfile();
        this.loginView  = new Login({user: userModel});
        this.tricksView = new TricksView({tricks: args.tricks, tags: args.tags, user: userModel});
        this.trickFull  = new TrickFullView({user: userModel});
        this.feedback   = new FeedBack({user: userModel});
        this.admin      = args.admin;
        
        if (this.admin) this.admin.render();

        // Общие действия при переходе по страницам
        this.bind('all', function (a, b, c) {
            self.feedback.hide();
            remove_tooltips();
            $('div.content').attr('class', 'content'); // обнулим все навешаенные на главный див стили
            
            // google analytics event push
            _gaq.push(['_trackPageview', '/' + location.hash]);
            
            if (this.admin && a !== 'route:trick' && this.admin.current_trick) {
                this.admin.drop_current_trick();
                this.admin.render();
            } else if (this.admin && a === 'route:trick') {
                this.admin.render();
            }
        });

        Backbone.history.start();
    },

    top_users: function () {
        var self = this,
            template = new EJS({url: '/static/templates/top_users.ejs'});
            
        $.ajax({
            url: '/rating/',
            dataType: 'json',
            success: function (response) {
                self.$el.html(template.render({'users': response}));
            },
            error: function () {
                alert('Network error');
            }
        });
    },

    about: function () {
        var template = new EJS({url: '/static/templates/about.ejs'});
        this.$el.html(template.render());
    },

    filter: function (tags_selected) {
        this.tricksView.filter(tags_selected);
        this.index();
    },

    my: function () {
        if (this.user) this.user.render();
    },

    index: function (tags_selected) {
        window.document.title = this.default_page_title;
        this.tricksView.render();
    },

    fresh_index: function () {
        var self = this;
        this.tricksView.reset_filter();
        this.tricksView.collection.fetch({success: function () {
            self.index();
        }});
    },

    profile: function (user_id) {
        this.profile.render(user_id);
    },

    trick: function (trick_id) {
        var trick = this.tricksView.collection.get(trick_id);
        if (this.admin) this.admin.set_current_trick(trick);
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
