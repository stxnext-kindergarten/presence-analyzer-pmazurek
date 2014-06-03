# -*- coding: utf-8 -*-
"""
Helper functions used in views.
"""

import csv
import os
from json import dumps
from functools import wraps
from datetime import datetime
from lxml import etree

from flask import Response

from presence_analyzer.main import app

import logging
log = logging.getLogger(__name__)  # pylint: disable=C0103


def jsonify(function):
    """
    Creates a response with the JSON representation of wrapped function result.
    """
    @wraps(function)
    def inner(*args, **kwargs):
        """
        Wrapper function for returning json data type.
        """
        return Response(dumps(function(*args, **kwargs)),
                        mimetype='application/json')
    return inner


def get_data():
    """
    Extracts presence data from CSV file and groups it by user_id.

    It creates structure like this:
    data = {
        'user_id': {
            datetime.date(2013, 10, 1): {
                'start': datetime.time(9, 0, 0),
                'end': datetime.time(17, 30, 0),
            },
            datetime.date(2013, 10, 2): {
                'start': datetime.time(8, 30, 0),
                'end': datetime.time(16, 45, 0),
            },
        }
    }
    """
    data = {}
    with open(app.config['DATA_CSV'], 'r') as csvfile:
        presence_reader = csv.reader(csvfile, delimiter=',')
        for i, row in enumerate(presence_reader):
            if len(row) != 4:
                # ignore header and footer lines
                continue

            try:
                user_id = int(row[0])
                date = datetime.strptime(row[1], '%Y-%m-%d').date()
                start = datetime.strptime(row[2], '%H:%M:%S').time()
                end = datetime.strptime(row[3], '%H:%M:%S').time()
            except (ValueError, TypeError):
                log.debug('Problem with line %d: ', i, exc_info=True)

            data.setdefault(user_id, {})[date] = {'start': start, 'end': end}

    return data


def group_by_weekday(items):
    """
    Groups presence entries by weekday.
    """
    result = {i: [] for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()].append(interval(start, end))
    return result


def group_by_weekday_start_end(items):
    """
    Groups presence entries by arrival/leave hour for each weekday.
    """
    result = {i: {'start': 0, 'end': 0, 'items': 0} for i in range(7)}
    for date in items:
        start = items[date]['start']
        end = items[date]['end']
        result[date.weekday()]['start'] += seconds_since_midnight(start)
        result[date.weekday()]['end'] += seconds_since_midnight(end)
        result[date.weekday()]['items'] += 1

    for day in result.values():
        try:
            day['start'] = day['start'] / day['items']
        except ZeroDivisionError:
            pass

        try:
            day['end'] = day['end'] / day['items']
        except ZeroDivisionError:
            pass

        del day['items']

    return result


def seconds_since_midnight(time):
    """
    Calculates amount of seconds since midnight.
    """
    return time.hour * 3600 + time.minute * 60 + time.second


def interval(start, end):
    """
    Calculates inverval in seconds between two datetime.time objects.
    """
    return seconds_since_midnight(end) - seconds_since_midnight(start)


def mean(items):
    """
    Calculates arithmetic mean. Returns zero for empty lists.
    """
    return float(sum(items)) / len(items) if len(items) > 0 else 0


def get_user_additional_data():
    """
    Gets user data from XML.
    """
    filename = app.config['DATA_XML']
    users = {}
    with open(filename, 'r') as xmlfile:
        xml = etree.parse(xmlfile)
        intranet = xml.getroot()
        server = intranet.find('server')
        server_url = '{0}://{1}:{2}'.format(
            server.find('protocol').text,
            server.find('host').text,
            server.find('port').text)
        for xml_user in intranet.find('users'):
            user = {
                'name': xml_user.find('name').text,
                'url': server_url + xml_user.find('avatar').text,
                }
            users[xml_user.get('id')] = user

        return users
