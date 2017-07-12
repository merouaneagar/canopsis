# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2017 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

from __future__ import unicode_literals

from canopsis.common.enumerations import DefaultEnum

"""
Some enumerations linked to Alarms.
"""


class AlarmField(DefaultEnum):
    # Possible fields for an alarm
    _id = '_id'
    ack = 'ack'
    ackremove = 'ackremove'
    canceled = 'canceled'  # != cancel
    comment = 'comment'
    extra = 'extra'
    hard_limit = 'hard_limit'
    linklist = 'linklist'
    pbehaviors = 'phbehaviors'
    resolved = 'resolved'
    snooze = 'snooze'
    state = 'state'
    status = 'status'
    steps = 'steps'
    tags = 'tags'
    ticket = 'ticket'
    alarmfilter = 'alarmfilter'  # see AlarmFilterField


class States(DefaultEnum):
    # Possible values for alarm states

    # TODO: apply with other values like stateinc, statetdec, ack, ackremove,
    # cancel, uncancel, declareticket, assocticket, snooze...
    changestate = 'changestate'


class AlarmFilterField(DefaultEnum):
    # Possible values for alarm filters

    runs = 'runs'  # trace runs
    next_run = 'next_run'  # stamp of the next run
