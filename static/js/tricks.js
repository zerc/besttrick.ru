/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */
var Trick, TrickView, TrickFullView, TricksList, TricksView, CheckTrick;

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

    initialize: function (args) {
        var self = this;
        _.bindAll(this, 'render');
        this.model.on('sync', this.render, this);
        this.user = args.user;
    },

    render: function () {
        var context = {
            'model'     : this.model,
            'user_id'   : this.user ? this.user.get('id') : false
        }
        this.$el.html(this.template.render(context));
        if (this.model.get('user_do_this')) {
            this.$el.addClass('user_do_this');
        }

        return this;
    },

    router: function (e) {
        var el = $(e.target).closest('a');

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
        // TODO: предусмотреть вывод сообшения об ошибке ввода
        if (cones <= 0) { return; }

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

    initialize: function (args) {
        _.bindAll(this, 'render');
        this.collection         = new TricksList(args.tricks);
        this.tags               = args.tags;
        this.selected_tags      = [];
        this.activated_tricks   = [];
        this.user               = args.user;
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
        _(this.collection.models).each(function (m) {
            if (this.selected_tags.length === 0 || _.include(this.activated_tricks, m.get('id'))) {
                this.tricks_container.append(new TrickView({model: m, user: this.user}).render().el);
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
