# -*- coding: utf-8 -*-
"""
Defines views.
"""

import calendar
from flask import redirect, url_for
from flask.ext.mako import render_template

from presence_analyzer.main import app
from presence_analyzer.utils import (
    jsonify,
    get_data,
    get_user_additional_data,
    mean,
    group_by_weekday,
    group_by_weekday_start_end)

import logging
log = logging.getLogger(__name__)  # pylint: disable=C0103


@app.route('/')
def mainpage():
    """
    Redirects to front page.
    """
    return redirect(url_for('presence_weekday_view'))


@app.route('/presence_weekday.html')
def presence_weekday_view():
    """
    Renders presence weekday view.
    """
    return render_template('presence_weekday.html')


@app.route('/presence_mean_time.html')
def presence_mean_time_view():
    """
    Renders mean time view.
    """
    return render_template('presence_mean_time.html')


@app.route('/presence_start_end.html')
def presence_start_end_view():
    """
    Renders presence start end view.
    """
    return render_template('presence_start_end.html')


@app.route('/api/v1/users', methods=['GET'])
@jsonify
def users_view():
    """
    Users listing for dropdown.
    """
    data = get_data()
    additional_data = get_user_additional_data()

    return [{
        'user_id': i,
        'name': additional_data[str(i)]["name"],
        'avatar': additional_data[str(i)]["url"]
        }
        for i in data.keys() if str(i) in additional_data]


@app.route('/api/v1/mean_time_weekday/', methods=['GET'])
@app.route('/api/v1/mean_time_weekday/<int:user_id>', methods=['GET'])
@jsonify
def mean_time_weekday_api_view(user_id):
    """
    Returns mean presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], mean(intervals))
              for weekday, intervals in weekdays.items()]

    return result


@app.route('/api/v1/presence_weekday/', methods=['GET'])
@app.route('/api/v1/presence_weekday/<int:user_id>', methods=['GET'])
@jsonify
def presence_weekday_api_view(user_id):
    """
    Returns total presence time of given user grouped by weekday.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday(data[user_id])
    result = [(calendar.day_abbr[weekday], sum(intervals))
              for weekday, intervals in weekdays.items()]

    result.insert(0, ('Weekday', 'Presence (s)'))
    return result


@app.route('/api/v1/presence_start_end/', methods=['GET'])
@app.route('/api/v1/presence_start_end/<int:user_id>', methods=['GET'])
@jsonify
def presence_start_end_api_view(user_id):
    """
    Returns mean office entry and leave hour, grouped by weekdays.
    """
    data = get_data()
    if user_id not in data:
        log.debug('User %s not found!', user_id)
        return []

    weekdays = group_by_weekday_start_end(data[user_id])
    result = [(calendar.day_abbr[weekday], interval['start'], interval['end'])
              for weekday, interval in weekdays.items()]
    return result
    