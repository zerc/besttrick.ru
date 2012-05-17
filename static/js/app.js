/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/* EJS view helpers */

// если в имени пользователя больше двух слов - первое выводим полностью, а второе сокращаем
EJS.Helpers.prototype.format_username = function (username) {
    var parts = username.trim().split(' ');
    return parts[1] ? parts[0] + ' ' + parts[1].charAt(0).toUpperCase() + '.' : parts[0];
}

EJS.Helpers.prototype.row_if_exists = function (row, label) {
    if (row) {
        return '<p><strong>' + label + ':</strong> ' + row + '</p>';
    }
};

EJS.Helpers.prototype.set_title = function (title) {
    window.document.title = 'Besttrick - ' + title;

};

EJS.Helpers.prototype.plural = function(number, one, two, five) {
    var n = number;
    number = Math.abs(number);
    number %= 100;
    if (number >= 5 && number <= 20) {
        return n + ' ' + five;
    }
    number %= 10;
    if (number == 1) {
        return n + ' ' + one;
    }
    if (number >= 2 && number <= 4) {
        return n + ' ' + two;
    }
    return n + ' ' + five;
};

EJS.Helpers.prototype.browser_info = function () {
    var data = {
        Screen  : window.screen.width + 'x' + window.screen.height,
        Window  : window.outerWidth   + 'x' + window.outerHeight,
        Browser : $.browser
    }
    return _.escape(JSON.stringify(data));
};


var App = Backbone.Router.extend({
    routes: {
        ''                          : 'index',
        '!'                         : 'fresh_index',
        'u:user_id/'                : 'my',
        'trick/:trick'              : 'trick',
        'profile-:user_id'          : 'profile',
        'filter=:tags_selected'     : 'filter'
    },

    initialize: function (args) {
        var self = this,
            userModel = args.user ? new UserModel(args.user) : false;

        this.user       = userModel ? new UserView({model: userModel}) : false;
        this.profile    = new UserProfile();
        this.loginView  = new Login({user: userModel});
        this.tricksView = new TricksView({tricks: args.tricks, tags: args.tags, user: userModel});
        this.trickFull  = new TrickFullView({user: userModel});
        this.feedback   = new FeedBack({user: userModel});

        // Назначаю общие действия при переходе по страницам
        this.bind('all', function () {
            self.feedback.hide();
            remove_tooltips();
            $('div.content').attr('class', 'content'); // обнулим все навешаенные на главный див стили
        });

        Backbone.history.start();
    },

    filter: function (tags_selected) {
        this.tricksView.filter(tags_selected);
        this.index();
    },

    my: function () {
        if (this.user) this.user.render();
    },

    index: function (tags_selected) {
        window.document.title = 'Besttrick';
        $('h1 span').text('');
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

    trick: function (trick) {
        return this.trickFull.render({model: this.tricksView.collection.get(trick)});
    }
});
