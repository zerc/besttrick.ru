# coding: utf-8
from flask import render_template, request, jsonify, session, url_for, make_response, flash, g

from project import app, connection, db, markdown
from apps.users import user_only, get_user
from apps.tricks import get_tricks, get_trick
from apps.utils import render_to, redirect






