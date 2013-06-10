/*
 * Besttrick application here
 */

var Besttrick = new Backbone.Marionette.Application();

Besttrick.addRegions({
  header : '#header',
  main   : '#main',
  footer : '#footer'
});


Besttrick.addInitializer(function (options) {
    var tricks = new this.Tricks.Models.Tricks(options.tricks);
    Besttrick.main.show(new this.Tricks.Views.Tricks({
        collection: tricks
    }));
});


Besttrick.module('Common', function (Common, App, Backbone, Marionette, $, _) {
    Common.Functions = {
        plural: function(number, one, two, five) {
            var n = Math.abs(number);

            n %= 100;
            if (n >= 5 && n <= 20) return number + ' ' + five;

            n %= 10;
            if (n == 1) return number + ' ' + one;

            if (n >= 2 && n <= 4) return number + ' ' + two;

            return number + ' ' + five;
        }
    };

    Common.Model = Backbone.Model.extend({
        wrappers: {},
        methods: [],

        extend_methods: function (obj) {
            _.each(this.methods, function (method) {
                obj[method.split('get_').pop()] = this[method]();
            }, this)
        },

        initialize: function () {
            _.each(this.wrappers, function (w, k) {
                this.set(k, _.isEmpty(this.get(k)) ? false : new w(this.get(k)));
            }, this);
        }
    });
});

Backbone.Form.validators.errMessages = {
    required: 'Обязательное поле',
    regexp: 'Некорректное значение',
    email: 'Некорректный e-mail адрес',
    url: 'Некорректный url',
    youtube: 'Введите ссылку на видео с YouTube',
    positive_int: 'Введите положительное число'
};

Backbone.Form.validators.youtube = function(options) {
    options = _.extend({
      type: 'youtube',
      message: this.errMessages.youtube,
      regexp: /^(http|https):\/\/(www\.youtube\.com|youtu.be)\/[a-zA-Z0-9\?&\/=\-]+$/gmi
    }, options);
    
    return Backbone.Form.validators.regexp(options);
};

Backbone.Form.validators.positive_int = function(options) {
    options = _.extend({
      type: 'positive_int',
      message: this.errMessages.positive_int
    }, options);
     
    return function positive_int(value) {
      options.value = value;
      
      var err = {
        type: options.type,
        message: options.message
      };
      
      if (value === null || value === undefined || value === false || value === '' || value <= 0) return err;
    };
  };
