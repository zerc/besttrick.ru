# coding: utf-8
from flask import render_template, request, jsonify, session, url_for, make_response, flash

from project import app, connection, db, markdown
from apps.users import user_only, adding_user, get_user
from apps.tricks import get_tricks
from apps.utils import render_to, redirect


@app.route('/', subdomain="m")
#@render_to(template='mobile/index.html')
@adding_user
def mobile_index(*args, **context):
    """
    Мобильная стартовая страничка
    """
    r = render_template('mobile/index.html', **context)
    return make_response(r)


@app.route('/tricks/', methods=['GET'], subdomain="m")
@adding_user
def mobile_tricks(*args, **context):
    """
    Список трюков в мобильной версии.
    """
    context['tricks'] = get_tricks(*args, **context)
    
    r = render_template('mobile/tricks.html', **context)
    return make_response(r)


@app.route('/ido/', methods=['GET'], subdomain="m")
@adding_user
@user_only
def mobile_checkin_page(*args, **context):
    """
    Мобильная страничка чекина.
    """
    if not context['user']:
        return 'Must login', 403

    context.update({
        'tricks': get_tricks(simple=True),
    })

    r = render_template('mobile/checkin_page.html', **context)

    return make_response(r)




@app.route('/ido/check/', methods=['POST'], subdomain="m")
@adding_user
@user_only
def mobile_checkin(*args, **context):
    """
    Чекинит пользователя
    """
    #TODO объеденить в функцией checktrick
    form_data = request.form.to_dict()
    user_id = context['user']['id']
    trick_id = form_data.pop('trick_id')
    
    checkin_result = checkin_user(trick_id, user_id, form_data)

    if isinstance(checkin_result, tuple):
        flash(checkin_result[0], 'error')
    else:
        flash(u'Вы успешно зачекинились', 'success')

    return redirect(url_for('mobile_checkin_page'))


