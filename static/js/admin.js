/*global jQuery, window, document */
/*jslint nomen: true, maxerr: 50, indent: 4 */

/*
 * Админка. Подключается в шаблоне, если пользователь имеет админские права.
 */
window.BTAdmin = {};

/*** Общие штуки ***/

Backbone.Form.validators.errMessages.required = 'Обязательное поле';

/*
 * Поле для вставки видео с Ютуба. 
 * Валидирует url и позволяет выбрать тумбу, 
 * для чего в options нужно передать имя поля в моделе, хранящее номер тумбы.
 */
Backbone.Form.editors.YouTube = Backbone.Form.editors.Text.extend({
    tagName: 'div',

    events: {
        'click a.show_thumbs' : 'show_thumbs',
        'click img'           : 'select_thumb'
    },

    initialize: function(options) {
        Backbone.Form.editors.Base.prototype.initialize.call(this, options);
      
        var schema = this.schema;
      
        //Allow customising text type (email, phone etc.) for HTML5 browsers
        var type = 'text';
          
        if (schema && schema.editorAttrs && schema.editorAttrs.type) type = schema.editorAttrs.type;
        if (schema && schema.dataType) type = schema.dataType;


        this.$el.html('<input type="'+type+'"/>\
            <a href="#" title="Показать превью" class="show_thumbs">&nbsp;</a>\
            <div class="thumb_holder"></div>'
        );

        this.$el.find('input')
            .attr('name', this.$el.attr('name'))
            .attr('id', this.$el.attr('id'));

        this.$el.removeAttr('name').removeAttr('id');

        this.thumb_fieldname = this.schema.options.thumb_fieldname;
        if (!this.thumb_fieldname) throw 'Set thumb fieldname in options for YouTube field';
    },

    show_thumbs: function () {
        var holder = this.$el.find('div.thumb_holder'),
            thumb_tmpl = _.template('<img class="<%= cls %>" src="http://img.youtube.com/vi/<%= video_id %>/<%= i %>.jpg" num=<%= i %> />'),
            video_id = this.getVideoId(),
            selected_thumb;
             
        if (video_id) {
            holder.html('');
            selected_thumb = this.getThumbNum();
            _.each([1,2,3], function (i) {
                holder.append(thumb_tmpl({video_id: video_id, i: i, cls: selected_thumb === i ? 'selected_thumb' : ''}));
            });
            holder.append('<div class="clear"></div>');
        } else {
            alert('Не удалось распознать url. Проверьте правильность ссылки на видео.')
        }

        return false;
    },

    select_thumb: function (e) {
        var thumb = $(e.target).closest('img');

        this.$el.find('img').removeClass('selected_thumb');
        thumb.addClass('selected_thumb');

        this.setThumbNum(thumb.attr('num'));
    },

    getThumb: function () {
        if (this.form) {
            return this.form.fields[this.thumb_fieldname];
        }

        if (this.fields) {
            return this.fields[this.thumb_fieldname];
        }
    },

    getVideoId: function () {
        var raw_data = this.getValue();

        if (/embed|youtu\.be/.test(raw_data)) return raw_data.split('/').pop();
        if (/\/watch\?v=/.test(raw_data)) return /\?v=([^&]+)/.exec(raw_data).pop();

        return false;
    },

    getThumbNum: function () {
        var raw_data = this.getThumb().getValue() || '-1';
        return parseInt(/\-(\d+)/.exec(raw_data).pop(), 10);
    },

    setThumbNum: function (num) {
        this.getThumb().setValue(num);
    },

    render: function() {
        this.setValue(this.value);
        return this;
    },

    getValue: function() {
      return this.$el.find('input').val();
    },
    
    setValue: function(value) { 
      this.$el.find('input').val(value);
    }
});


/*
 * Поле чекбоксов, заточенное под Skeleton
 */
Backbone.Form.editors.Checkboxes = Backbone.Form.editors.Checkboxes.extend({
    tagName: 'div',

    _arrayToHtml: function (array) {
        var html = [], 
            self = this;

        _.each(array, function(option, index) {
            var itemHtml = '';
            if (_.isObject(option)) {
              var val = option.val ? option.val : '';
              itemHtml += ('<label for="'+self.id+'-'+index+'">');
              itemHtml += ('<input type="checkbox" name="'+self.id+'" value="'+val+'" id="'+self.id+'-'+index+'" />');
              itemHtml += ('<span>'+option.label+'</span></label>');
            }
            else {
              itemHtml += ('<label for="'+self.id+'-'+index+'">');
              itemHtml += ('<input type="checkbox" name="'+self.id+'" value="'+option+'" id="'+self.id+'-'+index+'" />');
              itemHtml += ('<span>'+option+'</span></label>');
            }
            html.push(itemHtml);
        });

        return html.join('');
    }
});


/*** Models ***/
window.BTAdmin.User = window.BTUsers.UserModel.extend({
    url: function () {
        return '/admin/user/' + this.get('id') + '/';
    }
});


window.BTAdmin.UsersCollection = window.BTUsers.UsersCollection.extend({
    model: window.BTAdmin.User
});


window.BTAdmin.Trick = window.BTTricks.Trick.extend({
    url: '/admin/trick/',

    schema: {
        title: {type: 'Text', validators: ['required'], title: 'Название'},
        direction: {type: 'Select', options: ['', 'forward', 'backward'], title: 'Направ.'},
        videos: {type: 'YouTube', validators: ['required', 'url'], options: {'thumb_fieldname': 'thumb'}, title: 'Видео'},
        thumb: {type: 'Hidden'},
        score: {type: 'Text', validators: ['required'], title: 'Коэф. сложности'},
        tags: {type: 'Checkboxes', validators: ['required'], title: 'Тэги',
            // TODO: динамически их подгружать :D
            options: [
                {val: 'jumping',  label: 'прыжковый'},
                {val: 'sitting',  label: 'сидячий'},
                {val: 'spinning', label: 'вращательный'},
                {val: 'wheeling', label: 'вилинговый'}
            ]
        },
        descr: {type: 'TextArea', validators: ['required'], title: 'Описание'}
    },

    get_url: function () {
        return '#admin/edit_trick/trick' + this.get('id');
    },

    validate: function () {}
});


window.BTAdmin.TricksCollection = window.BTTricks.TricksList.extend({
    model: window.BTAdmin.Trick
});


window.BTAdmin.CheckinModel = Backbone.Model.extend({
    url: function () {
        return '/admin/checkin/' + this.id + '/';
    },

    defaults: {
        user        : 0,
        username    : '',
        trick       : 0,
        trick_title : '',
        cones       : 0,
        approved    : 0,
        video_url   : ''
    }
});


window.BTAdmin.CheckinCollection = Backbone.Collection.extend({
    url    : '/admin/checkins/',
    model  : window.BTAdmin.CheckinModel
});


/*** Views ***/
/*
 * Форма добавления или редактирования трюка.
 */
window.BTAdmin.trickForm = Backbone.View.extend({
    tagName     : 'div',
    className   : 'trick_add_form_container',
    template    : new EJS({url: '/static/templates/admin/trick_add_form.ejs'}),
    form        : undefined,

    events: {
        'click button.trick_add__save'  : 'save',
        'click button.trick_add__close' : 'close'
    },

    initialize: function (args) {
        _.bindAll(this, 'render', 'save', 'close');
        this.overflow = $('div.modal_form_overflow');
        this.body = $('body');
        this.doc = $(document);
        this.overflow.css('z-index', '11');;
    },

    render: function (trick) {
        var self = this;

        this.form = new Backbone.Form({
            model: trick
        }).render();

        this.$el.html(this.template.render({trick: trick}));
        this.$el.find('form').replaceWith(this.form.$el);
        this.$el.insertAfter(this.overflow).show();

        this.doc.bind('keydown', function (e) {
            var key = e.keyCode || e.which;
            if (key === 27) {
                self.close();
            }
        });

        return this;
    },

    close: function () {
        this.doc.unbind('keydown');
        this.overflow.css('z-index', '0');
        delete this.form;
        this.$el.remove();
        app.navigate('admin/tricks/', {trigger: false});
    },

    save: function () {
        var self = this,
            errors = this.form.commit();

        if (errors) return false;

        this.form.model.save(null, {
            success: function (model, response) {self.close();},
        });
    }
});


window.BTAdmin.CheckinView = Backbone.View.extend({
    tagName: 'tr',
    className: 'notice_video',
    template: new EJS({url: '/static/templates/admin/checkin.ejs'}),

    events: {
        'click a.notice_ok'          : 'notice_ok',
        'click a.notice_bad'         : 'notice_bad'
    },

    initialize: function (opts) {
        _.bindAll(this, 'render', 'notice_ok', 'notice_bad');
        this.model.on('change', function () {
            this.model.save();
            this.render();
            app.navigate('!', {trigger: true});
        }, this);
    },

    render: function (i) {
        this.$el.addClass(i % 2 === 0 ? 'odd' : 'edd');
        this.$el.html(this.template.render({checkin: this.model}));
        return this;
    },

    notice_ok: function () {
        this.model.set({'approved': 1});
        return false;
    },

    notice_bad: function () {
        this.model.set({'approved': 2});
        return false;
    }
});


/*
 * Базовая вью для отображения одного элемента в списке.
 * Отображает ссылку на его редактирование и удаление.
 */
window.BTAdmin.baseItemView = Backbone.View.extend({
    tagName     : 'tr',
    className   : 'base_item',
    template    : new EJS({url: '/static/templates/admin/base_item.ejs'}),
    extraFields : [], // какие дополнительные поля объекта выводить

    events: {
        'click a.delete_item': 'delete_item'
    },

    initialize: function (opts) {
        _.bindAll(this, 'render', 'delete_item');
        this.def
    },

    render: function (i) {
        this.$el.addClass(i % 2 === 0 ? 'odd' : 'edd');
        this.$el.html(this.template.render({item: this.model, i: i, extraFields: this.extraFields}));
        return this;
    },

    delete_item: function () {
        var self = this;

        if (confirm("Точно удалить?")) {
            this.model.destroy({
                data: JSON.stringify({id: this.model.get('id')}),
                success: function () {
                    self.remove();
                }
            });
        }
    }
});

/*
 * Базовая страница списка объектов
 * Нужно обязательно определить следующие поля:
 * - collection
 * - itemView (вью для рендера одно объекта)
 */
window.BTAdmin.baseItemsView = Backbone.View.extend({
    tagName     : 'div',
    template    : new EJS({url: '/static/templates/admin/base_items_page.ejs'}),
    events      : {'click button' : 'close'},

    page_title  : '',
    collection  : false,
    itemView    : window.BTAdmin.baseItemView,

    initialize: function (options) {
        _.bindAll(this, 'render', 'close');
        if (!this.collection) throw 'Setup collection items';
        
        this.body = $('body');
        this.doc  = $(document);
        
        this.overflow = $('div.modal_form_overflow');
        this.overflow.height(this.doc.height());
        
        // попробуем удалить ранее открытую страничку
        $('div.base_page_container').remove();

        this.$el.addClass('base_page_container');
    },

    render: function () {
        var self = this, left, container; 

        if (!this.collection.fetched) {
            this.collection.fetch({
                success: function (collection, response) {
                    self.collection.fetched = true;
                    return self.render();
                }
            });
        }

        this.overflow.show();
        this.$el.html(this.template.render({
            page_title   : this.page_title,
            add_item_url : this.add_item_url
        }));

        container = this.$el.find('table');
        this.collection.each(function (m, i) {
            if (i === 0) container.html('');
            container.append(new self.itemView({model: m}).render(i).$el);
        });

        this.$el.insertAfter(this.overflow);

        left = ($(window).width() - parseInt(this.$el.css('width'), 10)) / 2;
        this.$el.css('left', left + 'px');

        this.doc.bind('keydown', function (e) {
            var key = e.keyCode || e.which;
            if (key === 27) {
                self.close();
            }
        });

        return this;
    },

    close: function () {
        this.overflow.hide();
        this.doc.unbind('keydown');
        this.$el.remove();
        if (app.ref) location.href = app.ref;
        else app.navigate('', {trigger: true});
    }
});


/*
 * Страница для списка уведомлений о видеоподтверждениях
 */
window.BTAdmin.CheckinsView = window.BTAdmin.baseItemsView.extend({
    className   : 'notice_page_container',
    page_title  : 'Уведомления о новых видеоподверждениях',
    collection  : new window.BTAdmin.CheckinCollection(),
    itemView    : window.BTAdmin.CheckinView,
});


/*
 * Пользователь
 */
window.BTAdmin.userView = Backbone.View.extend({
    tagName: 'tr',
    className: 'a_user',
    template: new EJS({url: '/static/templates/admin/user_row.ejs'}),

    events: {
        'click a.a_user__ban'    : 'ban',
        'click a.a_user__unban'  : 'unban'
    },

    initialize: function (opts) {
        var self = this;
        _.bindAll(this, 'render', 'ban', 'unban');

        this.model.on('sync', function () {
            this.render();
        }, this);
    },

    render: function (i) {
        if (this.model.get('banned')) {
            this.$el.removeClass('odd edd').addClass('user_banned');
        } else {
            this.$el.removeClass('user_banned').addClass(i % 2 === 0 ? 'odd' : 'edd');
        }

        this.$el.html(this.template.render({
            user: this.model
        }));
        return this;
    },

    ban: function () {
        this.model.save({'banned': true})
        return false;
    },

    unban: function () {
        this.model.save({'banned': false});
        return false;
    }
});


/*
 * Список пользователей
 */
window.BTAdmin.usersListView = window.BTAdmin.baseItemsView.extend({
    className   : 'users_page_container',
    page_title  : 'Пользователи',
    collection  : new window.BTAdmin.UsersCollection(),
    itemView    : window.BTAdmin.userView
});


/*
 * Отображение трюка в админке
 */
window.BTAdmin.trickView = window.BTAdmin.baseItemView.extend({
    extraFields: ['score']
});


/*
 * Cписок трюков
 */
window.BTAdmin.tricksListView = window.BTAdmin.baseItemsView.extend({
    className    : 'tricks_page_container',
    page_title   : 'Трюки',
    add_item_url : '#admin/add_trick/',
    collection   : new window.BTAdmin.TricksCollection(),
    itemView     : window.BTAdmin.trickView
});


/*
 * Панель админки.
 */
window.BTAdmin.panel = Backbone.View.extend({
    tagName     : 'div',
    className   : 'admin_panel',
    template    : new EJS({url: '/static/templates/admin/admin_panel.ejs'}),
    events      : {'click a.toggle_panel': 'toggle'},

    initialize  : function () {
        $('div.container').prepend(this.$el);
    },

    toggle: function () {
        this.$el.toggleClass('admin_panel_opened');
        return false;
    },

    render: function () {
        _.bindAll(this, 'render', 'get_checkins_count');
        this.$el.html(this.template.render({
            'checkins_count': this.get_checkins_count()
        }));
    },

    get_checkins_count: function () {
        var checkins_count;

        $.ajax({
            url: '/admin/checkins_count/',
            dataType: 'json',
            async: false,
            success: function (response) {
                checkins_count = response.count;
            }
        });

        return checkins_count;
    }
});


var AdminApp = App.extend({
    routes      : (function () {
        return _.extend({
            'admin/users/'                  : 'users',
            'admin/videos/'                 : 'videos',
            'admin/tricks/'                 : 'tricks',
            'admin/add_trick/'              : 'add_trick',
            'admin/edit_trick/trick:trick'  : 'edit_trick'
        }, App.prototype.routes);
    }()),

    initialize  : function (args) {
        App.prototype.initialize.call(this, args);
        this.admin_panel = new window.BTAdmin.panel();
        this.admin_panel.render();
    },

    tricks: function () {
        return new window.BTAdmin.tricksListView().render();
    },

    users : function () {
        return new window.BTAdmin.usersListView().render();
    },

    videos : function () {
        return new window.BTAdmin.CheckinsView().render();
    },

    add_trick : function () {
        return new window.BTAdmin.trickForm().render(new window.BTAdmin.Trick());
    },

    edit_trick : function (trick_id) {
        var trick = this.tricksView.collection.get(trick_id);
        return new window.BTAdmin.trickForm().render(new window.BTAdmin.Trick(trick.toJSON()));
    }
});
