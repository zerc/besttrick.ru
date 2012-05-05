/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

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

window.app = function (tricks, tags, user) {
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
            direction   : '',
            score       : 0,
            wssa_score  : 0,

            user_do_this : false, // делает ли пользователь этот трюк
            users        : 0,     // сколько пользователей делает этот трюк
            cones        : 0,
            best_user    : '',
            best_user_cones : 0,
            users_full  : []
        },

        validate: function (attrs) {
            if (_.isNaN(attrs.cones) || attrs.cones < 0) {
                return 'укажите число конусов';
            }
        },

        get_title: function () {
            return (this.get('title') + ' ' + (this.get('direction') || '')).trim();
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
            var context = {
                'model'     : this.model,
                'user_id'   : user ? user.id : false
            }
            this.$el.html(this.template.render(context));
            if (this.model.get('user_do_this')) {
                this.$el.addClass('user_do_this');
            }

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
            if (!this.model.get('user_do_this')) {
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

        events: {
            'click a.tricks_filter__tag': 'activate_tag'
        },

        initialize: function () {
            _.bindAll(this, 'render');
            this.collection         = new TricksList(tricks);
            this.selected_tags      = [];
            this.activated_tricks   = [];
        },

        activate_tag: function (e) {
            $(e.target).toggleClass('tag__selected');

            this.selected_tags = _.map(this.tags_container.find('.tag__selected'), function (e) {
                return $(e).attr('href').replace('#', '');
            });
            console.log(this.selected_tags);
            this.filter();

            if (this.selected_tags.length > 0) {
                app.navigate('filter=' + this.selected_tags.join(','), false);
            } else {
                app.navigate('', true);
            }

            this.render_tricks();

            return false;
        },

        filter: function (tags_querystring) {
            if (tags_querystring) this.selected_tags = tags_querystring.split(',');
            this.activated_tricks = [];

            _.each(this.selected_tags, function (tag_name) {
                this.activated_tricks = _.union(this.activated_tricks, tags[tag_name]['tricks']);
            }, this);
        },

        reset_filter: function () {
            this.selected_tags      = [];
            this.activated_tricks   = [];
        },

        render_tricks: function () {
            this.tricks_container.html('');
            _(this.collection.models).each(function (m) {
                if (this.selected_tags.length === 0 || _.include(this.activated_tricks, m.get('id'))) {
                    this.tricks_container.append(new TrickView({model: m}).render().el);
                }
            }, this);
        },

        render_tags: function () {
            var tag_html = _.template('<a class="tricks_filter__tag<% if (major) { %> major_tag<% } %><% if (selected) {%> tag__selected<% } %>" href="#<%= tag_id %>"><%= tag_title %></a>');
            this.tags_container.html('');
            _(tags).each(function (tag_info, tag_id) {
                var context = {
                    major       : tag_info.major,
                    tag_id      : tag_id,
                    selected    : _.include(this.tags_selected, tag_id),
                    tag_title   : tag_info.title
                };
                this.tags_container.append(tag_html(context));
            }, this);
            this.tags_container.append('<div class="clear"></div>');
        },

        render: function () {
            var exists_containers = this.$el.find('div.tricks_filter, div.tricks_list');

            if (exists_containers.length !== 2) {
                this.$el.html('');
                this.tags_container   = $('<div class="tricks_filter"></div>');
                this.tricks_container = $('<div class="tricks_list"></div>');

                this.$el.append(this.tags_container, this.tricks_container);
            } else {
                this.tags_container   = $(exists_containers[0]);
                this.tricks_container = $(exists_containers[1]);
            }

            this.render_tags();
            this.render_tricks();
        }
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
            bio      : '',
            rolls    : '',
            epxs     : ''
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
            'profile-:user_id'          : 'profile',
            'filter=:tags_selected'     : 'filter'
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
            this.tricksView.reset_filter();
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
