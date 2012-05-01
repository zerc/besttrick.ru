/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

EJS.Helpers.prototype.set_title = function (title) {
    $('h1 span').text(title);
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
}

window.app = function (tricks, user) {
    'use strict';

    var App,
        Trick, TrickView, TrickFullView, TricksList, TricksView,
        UserModel, UserView, UserProfile,
        Login, FeedBack;

    Trick = Backbone.Model.extend({
        url: '/trick/',

        defaults: {
            _id         : '',
            title       : '',
            thumb       : '',
            videos      : [],
            descr       : '',
            score       : 0,
            wssa_score  : 0,

            can_mark    : true,  // может ли пользователь отметится
            users       : 0,     // сколько пользователей делает этот трюк
            cones       : 0,
            best_user   : '',
            best_user_cones : 0,
            users_full  : []
        },

        validate: function (attrs) {
            if (_.isNaN(attrs.cones) || attrs.cones < 0) {
                return 'укажите число конусов';
            }

        }
    });

    TrickView = Backbone.View.extend({
        tagName     : 'div',
        className   : 'trick',
        template    : new EJS({url: '/static/templates/trick.ejs'}),
        events      : {'click a': 'router'},

        initialize: function () {
            var self = this;
            _.bindAll(this, 'render');
            this.model.on('sync', this.render, this);
        },

        render: function () {
            var context = this.model.attributes;
            context.user_id = user ? user.id : false;
            this.$el.html(this.template.render(context));
            return this;
        },

        router: function (e) {
            var el = $(e.target);
            if (el.attr('bind')) {
                this[el.attr('bind')]();
            } else {
                app.navigate(el.attr('href').replace('#', ''), true);
            }
            
            return false;
        },

        toggle_dialog: function () {
            this.$el.toggleClass('showing_dialog');
        },

        save: function () {
            var cones = parseInt(this.$el.find('#dialog__cones').val(), 10);
            
            this.model.set('cones', cones, {silent: true});
            if (this.model.get('can_mark')) {
                this.model.set('users', this.model.get('users')+1, {silent: true});
            }

            if (this.model.hasChanged() && this.model.isValid()) {
                this.model.save();
            }

            this.toggle_dialog();
        }
    });

    TrickFullView = Backbone.View.extend({
        el: 'div.content',

        events: {
            'click .trick_video_preview': 'load_video',
        },

        template: new EJS({url: '/static/templates/trick_full.ejs'}),

        initialize: function () {
            _.bindAll(this, 'render', 'load_video');
        },

        render: function (options) {
            var self = this;
            _.extend(self, options);

            $.ajax({
                url: '/trick/full/' + self.model.get('id') + '/',
                dataType: 'json',
                success: function (response) {
                    self.$el.html(self.template.render({
                        'users': response,
                        'trick': self.model
                    }));
                },
                error: function () {
                    alert('error');
                }
            })
            
            return self;
        },

        load_video: function () {
            var html = '<iframe width="315" height="190" src="'+this.model.get('videos')[0]+'" frameborder="0" allowfullscreen></iframe>';
            this.$el.find('.trick_video_preview').replaceWith(html);
        }
    }); 

    TricksList = Backbone.Collection.extend({
        url: '/?json=tricks',
        model: Trick
    });

    TricksView = Backbone.View.extend({
        el: 'div.content',

        initialize: function () {
            _.bindAll(this, 'render');
            this.collection = new TricksList(tricks);

        },

        render: function () {
            var el = $('<div class="tricks_list"></div>');
            this.$el.html(el);
            _(this.collection.models).each(function (item) {               
                el.append(
                    new TrickView({model: item}).render().el
                );
            }, this);
        },
    });

    Login = Backbone.View.extend({
        el: 'div.user_container',

        events: {
            'click a.my': 'my',
        },

        initialize: function () {
            _.bindAll(this, 'render', 'my');
            this.render();
        },

        render: function () {
            this.$el.html(new EJS({url: '/static/templates/user_container.ejs'}).render({'user': user}));
        },

        my: function () {
            if (user) {
                app.navigate('u' + user.id + '/', true);
            }
            return false;
        }
    });

    FeedBack = Backbone.View.extend({
        el: 'div.feedback',

        events: {
            'click a'      : 'toggle_form',
            'click button' : 'send'
        },

        initialize: function () {
            _.bindAll(this, 'render', 'toggle_form', 'send');
            this._container = this.$el.find('div');
        },

        render: function (success) {
            var self = this;
            if (success) {
                this._container.html('<div class="success">Ваш отзыв успешно отправлен.</div>');
                this._container.fadeOut(2500);
            } else {
                this._container.html(new EJS({url: '/static/templates/feedback.ejs'}).render({'user': user}));
            }
        },

        toggle_form: function () {
            this._container.hasClass('as_block') ? this.hide() : this.show();
            return false;
        },

        show: function () {
            this.render();
            this._container.addClass('as_block');
        },

        hide: function () {
            this._container.removeClass('as_block');
        },

        send: function () {
            var data = {},
                errors = 0,
                self = this;

            _.map(this.$el.find('input, textarea'), function (el) {
                var $el = $(el);

                if (!$el.val()) {
                    if ($el.attr('type') === 'text') $el.addClass('error');
                } else {
                    data[$el.attr('id').replace('id_', '')] = $el.val();
                    $el.removeClass('error');
                }
            });

            if (!this.$el.find('.error').length) {
                $.ajax({
                    url: '/feedback/',
                    data: data,
                    context: this,
                    type: 'POST',
                    success: function () {
                        this.render({success: true});        
                    },
                    error: function () {
                        alert('Произошла непредвиденная ошибка.');
                    }
                });
            } else {    
                return false;
            }
        }
    });

    UserModel = Backbone.Model.extend({
        url: '/user/',

        defaults: {
            id       : 0,
            uid      : '',
            nick     : '',
            team     : '',
            photo    : '',
            admin    : '',
            identity : '',
            provider : '',
            email    : '',
            city     : '',
            icq      : '',
            skype    : '',
            phone    : '',
            bio      : ''
        },

        validate: function (attrs) {
            if (!attrs.nick) {
                return 'укажите свой ник';
            }
        }
    });

    UserView = Backbone.View.extend({
        el: 'div.content',

        events: {
            'click div.user__data button.save': 'update_data'
        },

        initialize: function () {
            _.bindAll(this, 'render');
            this.template = new EJS({url: '/static/templates/user.ejs'});
        },

        render: function () {
            var self = this,
                context = {user: this.model, save_status_text: '', profile: false};

            $.ajax({
                url: '/my/tricks/',
                dataType: 'json',
                success: function (response) {
                    context['tricks'] = response;
                    self.$el.html(self.template.render(context));        
                },
                error: function () {
                    alert('error');
                }
            });
        },

        update_data: function () {
            var data = this.$el.find('input, textarea'),
                self = this,
                show_save_status;

            show_save_status = function(status, text) {
                var text = text || (status === 'done' ? 'сохранено' : 'ошибка');
                $(self.el).find('.save_status')
                    .addClass(status).text(text).fadeOut(2000, function () {
                        $(this).text('').show();
                    });
            }

            _.each(data, function (el) {
                self.model.set($(el).attr('name'), $(el).val(), {silent:true});
            });

            if (!self.model.hasChanged()) { return; }

            self.model.save(true, true, {
                success: function (model, response) { show_save_status('done'); },
                error: function (model, response) {
                    show_save_status('error', response);
                }
            });
        }
    });

    UserProfile = Backbone.View.extend({
        el: 'div.content',

        initialize: function () {
            _.bindAll(this, 'render');
        },

        render: function (user_id) {
            var template = new EJS({url: '/static/templates/user.ejs'}),
                el = $('<div class="user__profile"></div>'),
                self = this;
            
            this.$el.html(el);

            $.ajax({
                url: '/profile/'+user_id+'/',
                dataType: 'json',
                success: function (response) {
                    response.user = new UserModel(response.user);
                    response.profile = true;
                    el.html(template.render(response));
                }
            });
        }
    });

    App = Backbone.Router.extend({
        routes: {
            ''                          : 'index',
            '!'                         : 'fresh_index',
            'u:user_id/'                : 'my',
            'trick/:trick'              : 'trick',
            'profile-:user_id'          : 'profile'
        },

        initialize: function () {
            var self = this;

            this.user       = user ? new UserView({model: new UserModel(user)}) : false;
            this.profile    = new UserProfile();
            this.loginView  = new Login();
            this.tricksView = new TricksView();
            this.trickFull  = new TrickFullView();
            this.feedback   = new FeedBack();

            // Назначаю общие действия при переходе по страницам
            this.bind('all', function () {
                self.feedback.hide();
            });

        },

        my: function () {
            if (this.user) this.user.render();
        },

        index: function () {
            window.document.title = 'Besttrick';
            $('h1 span').text('');
            this.tricksView.render();
        },

        fresh_index: function () {
            this.tricksView.collection.fetch();
            this.index();
        },

        profile: function (user_id) {
            this.profile.render(user_id);
        },

        trick: function (trick) {
            return this.trickFull.render({model: this.tricksView.collection.get(trick)});
        }
    });
    
    // приделать перехват ошибок
    var app = new App();
    Backbone.history.start();

    return {};
};
