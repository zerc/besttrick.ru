/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */
var Trick, TrickView, TrickFullView, TricksList, TricksView, CheckTrickView,
    UploadVideoForm, video_form, remove_tooltips, init_tooltips;

remove_tooltips = function () {
    $('div.tooltip').remove(); // удалим все тултипы
}

init_tooltips = function (el) {
    el.find('input.cones')
        .tooltip({trigger: 'focus'})
        .errortip({trigger: 'manual'});

    el.find('input.video_url')
        .tooltip({trigger: 'focus', placement: 'bottom'})
        .errortip({trigger: 'manual', placement: 'bottom'});
}

UploadVideoForm = function () {
    var body = $('body'),
        doc  = $(document),
        overflow = $('<div class="upload_video_form_overflow"></div>'),
        container = $('<div class="upload_video_form_container"></div>'),
        template = new EJS({url: '/static/templates/upload_video_form.ejs'});;

    overflow.height(doc.height());
    body.append(overflow, container);

    function get_params(trick_id) {
        var params = false;

        $.ajax({
            url: '/prepare_youtube_upload/',
            data: {'trick_id': trick_id},
            dataType: 'json',
            async: false,

            success: function (response) {
                params = response;
            },
            error: function () {
                alert('Ошибка получения параметров загрузки. Попробуйте еще раз.');
            }
        });

        return params;
    };

    function print_error(form, text) {
        form.find('div.error_holder').html(text);
    };


    /*
     * Показывает форму загрзки. Умеет получать параметры загрызки видео.
     * После успешной загрузки вызывает callback функцию, куда передает id video.
     */
    this.show = function (trick_id, callback) {
        var params = get_params(trick_id),
            form;

        if (!params) return;

        container.html(template.render(params));

        form = container.find('form');

        form.find('button.upload_form__close').bind('click', this.hide);

        form.ajaxForm({
            iframe: true, // так как ютуб использует редирект, нам нужно прогрузить его через iframe
            dataType: 'json',

            beforeSubmit: function (arr, form, options) {
                var file_selected = false; // выбран ли файл?

                if (!form.find('input[type="checkbox"]').is(':checked')) {
                    print_error(form, 'Вы должны согласиться с правилами загрузки.');
                    return false;
                }

                _(arr).each(function (el) {
                    if (el.name === "file" && el.value) file_selected = true;
                });

                if (!file_selected) {
                    print_error(form, 'Выберите файл для загрузки.');
                    return false;
                }

                // валидация пройдена, дисайблим кнопку, показываем лоадер, все дела
                print_error(form, '');
                form.find('button').addClass('disabled').attr('disabled', 'disabled');
                form.find('div.upload_form__loader').show();
                body.css('cursor', 'wait');

                return true;
            },

            complete: function (xhr) {
                var response = JSON.parse(xhr.responseText);

                if (response.status[0] !== '200') {
                    alert('Ошибка загрузки видео со стороны YouTube.');
                    return;
                }
                callback(response.id[0]);
            }
        });

        body.addClass('show_upload_form');
    },
    this.hide = function () {
        body.removeClass('show_upload_form').css('cursor', 'default');
    }

    return this;
}


$(function () {
    video_form = new UploadVideoForm();
});


CheckTrickView = Backbone.View.extend({
    template    : new EJS({url: '/static/templates/checktrick_form.ejs'}),
    events      : {
        'click a.toggle_dialog'         : 'toggle_dialog',
        'click a.dialog__save'          : 'save',
        'click a.check_full_trick_icon' : 'toggle_dialog',
        'click a.upload_video_link'     : 'show_upload_form'
    },

    initialize: function (args) {
        _.bindAll(this, 'render', 'save');
        this.user = args.user;
    },

    show_upload_form: function () {
        var self = this;

        video_form.show(this.model.get('id'), function (video_id) {
            var url = 'http://youtu.be/' + video_id
            self.$el.find('#dialog__video_url').val(url);
            //self.save();
            video_form.hide();
        });

        return false;
    },

    toggle_dialog: function () {
        this.$el.toggleClass('showing_dialog').
            find('input').errortip('hide');
        return false;
    },

    render: function (view_type) {
        var context;
        
        this.view_type = view_type || 'minify';
        context = {
            'model' : this.model,
            'user'  : this.user,
            'view'  : this.view_type
        };
        
        return this.template.render(context);
    },

    // принимает ошибку "вида поле_с_ошибкой::текст ошибки"
    // и рендерит это дело в тултип
    show_error: function (error) {
        var error_field, error_text;

        error = error.split('::');
        error_field = error[0];
        error_text  = error[1];

        this.$el.find('input.' + error_field)
            .attr('data-error-title', error_text)
            .tooltip('disable').errortip('enable').errortip('show')
            .one('focusout, keydown', function () {
                $(this).errortip('hide').errortip('disable').tooltip('enable');
            });
    },

    save: function (callback) {
        var self = this,
            cones = parseInt(this.$el.find('#dialog__cones').val(), 10) || -1,
            video_url = this.$el.find('#dialog__video_url').val();

        if (cones) this.model.set('cones', cones, {silent: true});
        if (video_url) this.model.set('video_url', video_url, {silent: true});

        if (!this.model.get('user_do_this')) {
            this.model.set('users', this.model.get('users')+1, {silent: true});
        }

        if (this.model.hasChanged() && this.model.isValid()) {
            this.model.save(null, {success: function (model, response) {
                self.toggle_dialog();
                // в заивисимости от типа формы триггерем нужное событие
                model.trigger('sync::' + self.view_type);
                self.user.fetch(); // обновим рейтинг пользователя
            }});
        } else if (this.model.hasChanged()) {
            this.show_error(this.model.validate(this.model.changedAttributes()));
            this.model.set(this.model.previousAttributes(), {silent: true});
        }

        return false;
    }
})

Trick = Backbone.Model.extend({
    url: '/checktrick/',

    defaults: {
        _id         : '',
        title       : '',
        thumb       : '',
        videos      : [],
        descr       : '',
        direction   : '',
        score       : 0,
        wssa_score  : 0,

        // параметры о чекине/чекинах пользователей
        user_do_this    : false, // делает ли пользователь этот трюк
        users           : 0,     // сколько пользователей делает этот трюк
        cones           : 0,
        video_url       : '',    // сслыка на подтверждающий видос
        best_user       : '',
        best_user_cones : 0,
        users_full      : []
    },

    validate: function (attrs) {
        if (_.isNaN(attrs.cones) || attrs.cones <= 0) {
            return 'cones::введите положительное число';
        }

        if (attrs.cones >= 1000) {
            return 'cones::не верим :)';
        }

        if (attrs.video_url && !/^(http|https):\/\/(www\.youtube\.com|youtu.be)\/[a-zA-Z0-9\?&\/=\-]+$/gmi.test(attrs.video_url)) {
            return 'video_url::укажите ссылку на видео с YouTube';
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

    initialize: function (args) {
        _.bindAll(this, 'render');
        this.model.on('sync::minify', this.render, this);
        this.user = args.user;
        this.checktrick = new CheckTrickView({
            el    : this.el,
            user  : this.user,
            model : this.model
        });
    },

    render: function () {
        var context = {
                'model'     : this.model,
                'user_id'   : this.user ? this.user.get('id') : false
            };

        this.$el.html(this.template.render(context) + this.checktrick.render());

        if (this.model.get('user_do_this')) this.$el.addClass('user_do_this');

        init_tooltips(this.$el);
        

        return this;
    }
});

TrickFullView = Backbone.View.extend({
    el: 'div.content',

    events: {
        'click .trick_video_preview': 'load_video',
    },

    template: new EJS({url: '/static/templates/trick_full.ejs'}),

    initialize: function (args) {
        _.bindAll(this, 'render', 'load_video');
        this.checktrick = new CheckTrickView({user: args.user, el: this.el});
    },

    render: function (options) {
        var self = this;

        // кэшируем последние опции, с которыми вызывался рендер
        this.last_options = options;
        _.extend(self, options || this.last_options || {});

        // манки-патчим форму чекина
        this.checktrick.model = this.model;
        
        // TODO: обрабатывать данные на клиенте, для этого у нас уже есть
        // список пользователей с их результатами. Добавляем-изменяем свой,
        // сортируем все дела :)
        this.model.on('sync::full', this.render, this);

        $.ajax({
            url: '/trick/full/' + self.model.get('id') + '/',
            dataType: 'json',
            success: function (response) {
                self.$el.html(self.template.render({
                    'users': response,
                    'trick': self.model,
                    'checktrick': self.checktrick
                }));

                init_tooltips(self.$el);
            },
            error: function () {
                alert('Network error');
            }
        });

        return self;
    },

    load_video: function () {
        var html = '<iframe width="315" height="190" src="'+this.model.get('videos')[0]+'" frameborder="0" allowfullscreen></iframe>';
        this.$el.find('.trick_video_preview').replaceWith(html);
        return false;
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

    initialize: function (args) {
        _.bindAll(this, 'render');
        this.collection         = new TricksList(args.tricks);
        this.tags               = args.tags;
        this.selected_tags      = [];
        this.activated_tricks   = [];
        this.user               = args.user;
        this.checktrick         = args.checktrick;
    },

    activate_tag: function (e) {
        $(e.target).toggleClass('tag__selected');

        this.selected_tags = _.map(this.tags_container.find('.tag__selected'), function (e) {
            return $(e).attr('href').replace('#', '');
        });

        this.filter();

        if (this.selected_tags.length > 0) {
            app.navigate('filter=' + this.selected_tags.join(','), false);
        } else {
            app.navigate('', true);
        }

        this.render_tricks();
        remove_tooltips();

        return false;
    },

    filter: function (tags_querystring) {
        if (tags_querystring) this.selected_tags = tags_querystring.split(',');
        this.activated_tricks = [];

        _.each(this.selected_tags, function (tag_name) {
            this.activated_tricks = _.union(this.activated_tricks, this.tags[tag_name]['tricks']);
        }, this);
    },

    reset_filter: function () {
        this.selected_tags      = [];
        this.activated_tricks   = [];
    },

    render_tricks: function () {
        this.tricks_container.html('');
        this.collection.each(function (m) {
            if (this.selected_tags.length === 0 || _.include(this.activated_tricks, m.get('id'))) {
                this.tricks_container.append(new TrickView({model: m, user: this.user, checktrick: this.checktrick}).render().el);
            }
        }, this);
    },

    render_tags: function () {
        var tag_html = _.template('<a class="tricks_filter__tag<% if (major) { %> major_tag<% } %><% if (selected) {%> tag__selected<% } %>" href="#<%= tag_id %>"><%= tag_title %></a>');
        this.tags_container.html('');
        _(this.tags).each(function (tag_info, tag_id) {
            var context = {
                major       : tag_info.major,
                tag_id      : tag_id,
                selected    : _.include(this.selected_tags, tag_id),
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
