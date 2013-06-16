/* 
 * triks.views.checkins
 *
 * All about checkins views
 * :copyright: (c) 2013 by zero13cool
 */

Besttrick.module('Tricks.Views', function (Views, App, Backbone, Marionette, $, _) {
    Views.Checkin = Marionette.ItemView.extend({
        className: 'trick__user',
        tagName: 'tr',
        template: '#checkin'
    });

    Views.Checkins = Marionette.CollectionView.extend({
        tagName: 'table',
        itemView: Views.Checkin,

        // TODO: mb rewrite table>tr>td to div?
        appendHtml: function (collectionView, itemView, index) {
            if (index === 0) itemView.$el.addClass('trick__user_king');
            this.$el.append(itemView.el);
            if (index !== this.collection.length-1) {
                this.$el.append('<tr><td colspan="4" class="trick__breaker">&nbsp;</td></tr>');
            }
        }
    });

    Views.CheckinForm = Backbone.Form.extend({
        className: 'trick__dialog',

        events: {
            'click a.dialog__close i': 'close',
            'click a.dialog__save': 'save'
        },

        render: function (args) {
            Backbone.Form.prototype.render.call(this, args);
            this.trigger('after:render');
   
            this.$el.find('input')
                .tooltip({trigger: 'focus'})
                .errortip({trigger: 'manual'});

            return this;
        },

        initialize: function (args) {
            Backbone.Form.prototype.initialize.call(this, args);
            
            this.model.on('change', function () {
                this.model.save();
                this.render()
            }, this);

            this.on('after:render', function () {
                var w = args.parent.width(),
                    h = args.parent.height();
                this.$el.width(w+2).height(h-21);
            }, this);
        },

        save: function () {
            var self = this,
                errors = this.commit();

            if (!errors) { return false; }

            _.each(errors, function (k, v) {
                self.fields[v].editor.$el.addClass('error')
                    .tooltip('disable').errortip('enable').errortip('show')
                    .one('blur, keydown', function () {
                        $(this).errortip('hide').errortip('disable').tooltip('enable');
                    });
            });

            return false;
        },

        close: function () {
            $('div.tooltip').remove();
            this.remove();
            return false;
        }
    });
});