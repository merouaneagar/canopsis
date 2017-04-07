# -*- coding: utf-8 -*-
# --------------------------------
# Copyright (c) 2015 "Capensis" [http://www.capensis.com]
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

__version__ = '0.1'

from enum import Enum


class AlarmField(Enum):
    # Possible fields for an alarm
    ack = 'ack'
    ackremove = 'ackremove'
    canceled = 'canceled'  # != cancel
    comment = 'comment'
    snooze = 'snooze'
    state = 'state'
    status = 'status'
    ticket = 'ticket'
    # TODO : extend to other fields (steps, extra, resolved, tags, resource...)

    def __str__(self):
        return str(self.value)
