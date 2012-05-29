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
        if (/\/watch\?v=/.test(raw_data)) return /\?v=([a-zA-Z0-9\?\/=\-]+)&/.exec(raw_data).pop();

        return false;
    },

    getThumbNum: function () {
        var raw_data = this.getThumb().getValue() || '1';
        return parseInt(/\d/.exec(raw_data).pop(), 10);
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

        this.overflow.height(this.doc.height());
    },

    render: function (trick) {
        var self = this;

        this.form = new Backbone.Form({
            model: trick
        }).render();

        this.$el.html(this.template.render({trick: trick}));
        this.$el.find('form').replaceWith(this.form.$el);
        this.$el.insertAfter(this.overflow);

        this.body.addClass('show_trick_add_form');
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
        this.body.removeClass('show_trick_add_form');
        delete this.form;
        this.$el.remove();
    },

    save: function () {
        var self = this,
            errors = this.form.commit();

        if (errors) return false;

        this.form.model.save(null, {
            success: function (model, response) {self.close();},
            url: '/admin/trick/'
        });
    }
});

/*
 * Панель админки.
 */
window.BTAdmin.panel = Backbone.View.extend({
    tagName     : 'div',
    className   : 'admin_panel',
    template    : new EJS({url: '/static/templates/admin/admin_panel.ejs'}),
    
    active_form: null,

    // HOOK: если указан - позволяем его отредактировать
    current_trick : null,
    trick_url     : '/admin/trick/',

    events: {'click a': '_router'},

    _router: function (e) {
        var el = $(e.target).closest('a'),
            bind = el.attr('bind');
        
        if (!bind) return true;
        
        this[bind]();
        return false;
    },

    set_current_trick: function (trick) {
        this.current_trick = _.extend({}, trick, {url: this.trick_url});
    },

    drop_current_trick: function () {
        this.current_trick = null;
    },

    initialize: function (args) {
        _.bindAll(this, 'render');
        $('div.container').prepend(this.$el);
    },

    toggle: function () {
        this.$el.toggleClass('admin_panel_opened');
    },

    add_trick: function () {
        var trick = new Trick();
        trick.url = this.trick_url;
        if (this.active_form) this.active_form.close();
        this.active_form = new window.BTAdmin.trickForm().render(trick);
    },

    edit_trick: function () {
        if (this.active_form) this.active_form.close();
        this.active_form = new window.BTAdmin.trickForm().render(this.current_trick);
    },

    delete_trick: function () {
        if (confirm("Удалить трюк?")) {
            this.current_trick.destroy({
                data: JSON.stringify({id: this.current_trick.get('id')}),
                success: function () {
                    app.navigate('', {trigger: true});
                }
            });
        }
    },

    render: function () {
        this.$el.html(this.template.render({
            current_trick: this.current_trick
        }));
    }
});