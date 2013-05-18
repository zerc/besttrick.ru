/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * TODO: Все в неймспейс.
 * Все, что связано с пользователем.
 */
window.BTUsers = {};

var UserModel, UserView, UserProfile,
    Login, FeedBack;


window.BTUsers.Loginza = {
    href: "https://loginza.ru/api/widget?token_url=http://"
        + location.host 
        + "/login/&providers_set=vkontakte,twitter,facebook",

    // Просто обертка метода библиотеки
    show_login_form: function () {
        if (!LOGINZA || !LOGINZA.show) {
            return alert('Cant find LOGINZA widget :/');
        }

        LOGINZA.show.call(this);
    }
};
    

/*** Модельки ***/
window.BTUsers.UserModel = UserModel = Backbone.Model.extend({
    url: '/my/',

    defaults: {
        id       : 0,
        uid      : '',
        nick     : '',
        team     : '',
        photo    : '',
        admin    : '',
        email    : '',
        city     : '',
        icq      : '',
        skype    : '',
        phone    : '',
        bio      : '',
        rolls    : '',
        epxs     : '',
        rating   : 0.0,
        banned   : false
    },
    // <input placeholder="ник" type="text" id="id_nick" name="nick" value="klassnykh" >
    schema: {
        nick: {
            type        : 'Text', 
            validators  : ['required'],
            editorAttrs : {'placeholder': 'Ник', 'maxlength': '100'}
        },
        team: {
            type: 'Text', 
            editorAttrs : {'placeholder': 'Команда', 'maxlength': '100'}
        },
        phone: {
            type: 'Text',
            editorAttrs : {'placeholder': 'Телефон'}
        },
        city: {
            type: 'Text', 
            editorAttrs : {'placeholder': 'Город', 'maxlength': '100'}
        },
        icq: {
            type: 'Text', 
            editorAttrs : {'placeholder': 'ICQ', 'maxlength': '10'}
        },
        skype: {
            type: 'Text', 
            editorAttrs: {'placeholder': 'Skype', 'maxlength': '50'}
        },
        rolls: {
            type: 'Text',
            editorAttrs: {'placeholder': 'Ролики', 'maxlength': '50'}
        },
        epxs: {
            type: 'Text',
            editorAttrs: {'placeholder': 'Стаж', 'maxlength': '50'}
        },
        bio: {
            type: 'TextArea',
            editorAttrs: {'placeholder': 'Информация', 'maxlength': '300'}
        }
    },

    validate: function (attrs) {
        if (!attrs.nick) {
            return 'укажите свой ник';
        }

        if (attrs.nick.length >= 125) {
            return 'у вас нереально большой ник';
        }
    },

    get_profile_url: function () {
        return '#!users/user' + this.id;
    },

    parse: function(resp, xhr) {
      return resp.user;
    }
});


window.BTUsers.UsersCollection = Backbone.Collection.extend({
    url: '/users/',
    model: window.BTUsers.UserModel
});

/*** Вьюхи ***/

/* Вью формы логина, или инфы авторизованного пользователя */
Login = Backbone.View.extend({
    el: 'div.user_container',

    events: {
        'click a.loginza': 'save_path',
        'click a.logout' : 'save_path'
    },

    save_path: function (e) {
        var path = location.hash;
        if (!path) return;
        $.cookie(window.BTCommon.vars.next_url_cookie_name, encodeURIComponent(path));
    },


    initialize: function (args) {
        _.bindAll(this, 'render');
        this.user = args.user;
        if (this.user) this.user.on('change', this.render, this);
        this.render();
    },

    render: function () {
        this.$el.html(new EJS({url: '/static/templates/user_container.ejs'}).render({'user': this.user}));
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
                success: function () { this.render({success: true}); },
                error: function () { alert('Произошла непредвиденная ошибка.'); }
            });
        } else {
            return false;
        }
    }
});

/* Views */
UserView = Backbone.View.extend({
    el       : 'div.content',
    
    template : new EJS({url: '/static/templates/user.ejs'}),
    
    events   : {
        'click div.user__data button.save': 'update_data'
    },

    initialize: function () {
        var self = this,
            show_save_status;

        _.bindAll(this, 'render');
        
        // union this as smart save button
        this.button = $('<button>', {'type': 'button', 'class': 'save', 'text': 'Сохранить'});
        this.status_el = $('<span>', {'class': 'save_status'});

        this.form = new Backbone.Form({model: this.model}).render();
        this.context = {
            user    : this.model,
            form    : this.form,
            tricks  : this.options.tricks
        }

        show_save_status = function(status, text) {
            var text = text || (status === 'done' ? 'сохранено' : 'ошибка');
            $(self.el).find('.save_status')
                .addClass(status).text(text).fadeOut(2000, function () {
                    $(this).text('').show();
                });
        }         

        this.model.on('change', function () {
            self.model.save(null, {
                success: function (model, response) { show_save_status('done'); },
                error: function (model, response) { show_save_status('error', response); }
            });
        });            
        
    },


    render: function () {
        this.$el.html(this.template.render(this.context));
        
        this.$el.find('form').replaceWith(
            this.form.$el.append(this.button, this.status_el)
        );
    },

    update_data: function () {
        return this.form.commit();
    }
});


UserProfile = UserView.extend({
    render: function (user_id) {
        var self = this,
            form_el;
        
        self.$el.html(self.template.render(this.context));
        form_el = self.$el.find('form');

        _.each(self.form.fields, function (e) {
            if (!e.editor.value) return;

            form_el.append(
                '<p><strong>' + e.schema.title + ':</strong> ' + e.editor.value + '</p>'
            );
        });

        form_el.children().unwrap();
    }
});
