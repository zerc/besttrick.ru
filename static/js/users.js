/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */
var UserModel, UserView, UserProfile,
    Login, FeedBack;

Login = Backbone.View.extend({
    el: 'div.user_container',

    events: {
        'click a.my': 'my',
    },

    initialize: function (args) {
        _.bindAll(this, 'render', 'my');
        this.user = args.user;
        this.render();
    },

    render: function () {
        this.$el.html(new EJS({url: '/static/templates/user_container.ejs'}).render({'user': this.user}));
    },

    my: function () {
        if (this.user) {
            app.navigate('u' + this.user.get('id') + '/', true);
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

    initialize: function (args) {
        var self = this;
        self.user = args.user;

        _.bindAll(this, 'render', 'toggle_form', 'send');
        this._container = this.$el.find('div');

        $(document).bind('click', function (e) {
            if ($(e.target).closest('div.' + self.$el.attr('class')).length === 0 && self._container.hasClass('as_block')) self.toggle_form();
        });

    },

    render: function (success) {
        var self = this;
        if (success) {
            this._container.html('<div class="success">Ваш отзыв успешно отправлен.</div>');
            this._container.fadeOut(2500);
        } else {
            this._container.html(new EJS({url: '/static/templates/feedback.ejs'}).render({'user': self.user}));
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
                if ($el.attr('type') === 'text' || $el.attr('id') === 'id_text') $el.addClass('error');
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
