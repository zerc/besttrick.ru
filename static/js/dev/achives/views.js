/*
 * Views for achives module
 */
Besttrick.module('Achives.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.Filter = Marionette.ItemView.extend({
        template: '#achives_filter',
        className: 'button-bar achives_filter',
        tagName: 'div',

        events: {
            'click a.filter_item': 'update_filter',
            'click a.toggle_all': 'toggle_all'
        },

        update_filter: function (e) {
            var $el = $(e.target),
                level = parseInt($el.attr('data-level'));

            this.$el.find('a').removeClass('active');
            
            if (this.collection.show_level === level) {
                this.collection.show_level = -1;
            } else {
                this.collection.show_level = level;
                $el.toggleClass('active');
            }

            this.collection.trigger('change');

            return false;
        },

        toggle_all: function (e) {
            var $el = $(e.target),
                clss = ['icon-download', 'icon-upload'];
            
            $el.hasClass(clss[0]) ? '' : clss.reverse();
            $el.removeClass(clss[0]).addClass(clss[1]);
            this.collection.trigger('toggle');
            
            return false;
        }
    }); 

    Views.Achive = Marionette.ItemView.extend({
        tagName     : 'div',
        className   : 'achive',
        template    : '#achive_item',
        _cached     : false,

        templateHelpers : {
            childrens: []
        },

        events: {
            'click div.achive__header' : 'toggle',
            'click a.more_link' : 'toggle'
        },

        initialize: function () {
            this.$el.addClass('achive__lvl_' + this.model.get('level'));
            this.listenTo(this.model, 'change', this.render);
        },

        toggle: function () {
            // TODO: переписать так, чтобы от родителя можно было добраться до детей (поле childrens) =()
            var self = this,
                toggle_cls = 'showing_progress';

            if (this.$el.hasClass(toggle_cls)) {
                this.$el.removeClass(toggle_cls);
                return false;
            } else if (!this._cached) {
                this.templateHelpers.childrens = this.model.get_childrens();
                this._cached = true;
                this.render();
            }

            this.$el.addClass(toggle_cls);
            return false;
        },
    });

    Views.Achives = Marionette.CollectionView.extend({
        tagName: 'div',
        className: 'achives_page grid',
        itemView: Views.Achive,
        
        initialize: function () {
            this.listenTo(this.collection, 'change', this.render);
            this.listenTo(this.collection, 'toggle', this.toggle);
        },

        toggle: function () {
            this.children.invoke('toggle');
            return false;
        },

        appendHtml: function(collectionView, itemView, index) {
            // var side = (index % 2 === 0) ? this.left_side : this.right_side;
            if (!itemView.model.is_complex()) return

            if (this.collection.show_level < 0)
                collectionView.$el.append(itemView.el);
            else if (this.collection.show_level === itemView.model.get('level'))
                collectionView.$el.append(itemView.el);
        },
    });
 });
