/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * TODO: Все в неймспейс.
 * Все, что связано с пользователем.
 */
window.BTUsers = {};

var UserModel, UserView, UserProfile,
    TitulModel, TitulCollection,
    Login, FeedBack;

Backbone.Form.editors.SpecialSelect = Backbone.Form.editors.Select.extend({
    tagName: 'ul',

    events: {'click li': 'select'},

    select: function (e) {
        if (this.options.disable_select) return;
        var target = $(e.currentTarget);
        if (target.hasClass('disable') || target.hasClass('hint')) return;

        this.$el.find('li').removeClass('selected');
        this.setValue(
            target.addClass('selected').attr('data-id')
        );
    },

    setValue: function (val) {
        return this.$el.val(parseInt(val));
    },

    getValue: function() {
      return parseInt(this.$el.val());
    },

    renderOptions: function (options) {
        Backbone.Form.editors.Select.prototype.renderOptions.call(this, options);
        var $el = $('<li class="hint" title="\
            По мере освоения вами сложных достижений, вы будете получать различные звания. \
            Все они будут отображаться в вашем профиле. \
            Вы можете выбрать одно звание, которое будет отображаться везде с вашим ником.">?</li>');
        this.$el.append($el.tooltip({trigger: 'hover'}));
    },

    _collectionToHtml: function(collection) {
        var html = [],
            opts = {},
            self = this;

        collection.each(function(model) {
            opts.id = model.get('id');
            opts.title = model.get('title');
            opts.short_title = model.get('short_title');
            opts.disable = model.get('level') === 0 ? 'disable' : '';
            opts.cls = model.get('id') === self.model.get('selected_titul') ? 'selected' : '';
            opts.description = model.get('level') === 0 ? 'Чтобы открыть бадж нужно получить достижение ' : '';
            opts.description += model.get('title');

            html.push(_.template('\
                <li title="<%= description %>" data-id="<%= id %>" class="<%= cls %> <%= disable %>">\
                    <span><%= short_title %></span>\
                </li>')(opts));
        });
        
        return html.join('');
    }
});

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
window.BTUsers.TitulModel = TitulModel = Backbone.Model.extend({
    // url: '/users/tituls/',

    defaults: {
        'title': '',
        'short_title': '',
        'level': 0
    }
});

window.BTUsers.TitulCollection = TitulCollection = Backbone.Collection.extend({
    url: '/users/tituls/',
    model: TitulModel,
    parse: function (response) {
        return response.tituls;
    }
});


window.BTUsers.UserModel = UserModel = Backbone.Model.extend({
    url: '/user/',

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
        banned   : false,

        selected_titul   : 0,
        titul: ''
    },

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

    initialize: function () {
        var self = this;

        this.schema.selected_titul = {
            type: 'SpecialSelect',
            editorAttrs: {'class': 'tituls_list'},
            options: function (callback) {
                var tituls = new TitulCollection().fetch({
                    'data': 'user_id=' + self.get('id'),
                    'success': function (response) {
                        callback(response);
                    }
                });
            }
        }

        this.schema = _.clone(this.schema);
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
            tricks  : this.options.tricks,
            profile_page: false,
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

        _.extend(this.context, {'profile_page': true});
        self.$el.html(self.template.render(this.context));
        form_el = self.$el.find('form');
        form_el.parent().addClass('user_pofile');

        _.each(self.form.fields, function (e) {
            if (!e.editor.value) return;
            if (e.key === 'selected_titul') {
                e.editor.options['disable_select'] = true;
                form_el.append(e.editor.render().el);
            } else {   
                form_el.append(
                    '<p><strong>' + e.schema.editorAttrs.placeholder + ':</strong> ' + e.editor.value + '</p>'
                );
            }
        });

        form_el.children().unwrap();
    }
});
