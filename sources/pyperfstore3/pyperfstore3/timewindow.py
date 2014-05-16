#!/usr/bin/env python
#--------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
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

from time import time
from datetime import datetime as dt, timedelta as td
from dateutil.relativedelta import relativedelta as rd
import calendar


class Period(object):
	"""
	Period management with a value and an unitself.
	"""

	__slots__ = ['unit_values']

	MICROSECOND = 'microsecond'
	SECOND = 'second'
	MINUTE = 'minute'
	HOUR = 'hour'
	DAY = 'day'
	WEEK = 'week'
	MONTH = 'month'
	YEAR = 'year'
	CENTURY = 'century'
	MILLENARY = 'millenary'

	UNITS = (MICROSECOND, SECOND, MINUTE, HOUR, DAY, WEEK, MONTH, YEAR)

	UNIT = 'unit'
	VALUE = 'value'

	def __init__(self, **unit_values):

		super(Period, self).__init__()

		self.unit_values = unit_values

	def get_delta(self):
		"""
		Get a delta object in order to add/remove a period on a datetime.
		"""

		parameters = {
			name + 's': value
			for name, value in self.unit_values.iteritems()
		}

		result = rd(**parameters)

		return result

	def next_period(self):
		"""
		Get next period with input step or none if next period can't be associated to a specific unit.
		"""

		result = None

		counts_with_unit = list(Period.MAX_VALUE_WITH_UNITS)
		previous_unit, previous_count = counts_with_unit.pop(-1)
		counts_with_unit.reverse()

		for unit, count in counts_with_unit:
			value = self.unit_values.get(unit)

			if value is not None:
				next_value = value / count
				self.unit_values[previous_unit] = next_value
				del self.unit_values[unit]

			previous_unit = unit

		return result

	def sliding_timestamp(self, timestamp, normalize=False):
		"""
		Get round timestamp relative to an input timestamp.
		"""

		datetime = dt.utcfromtimestamp(float(timestamp))
		datetime = self.sliding_datetime(datetime=datetime, normalize=normalize)

		utctimetuple = datetime.utctimetuple()
		result = calendar.timegm(utctimetuple)

		# restore microsecond because utctimetuple() does not
		microseconds = datetime.microsecond * 0.000001
		result += microseconds

		return result

	def sliding_datetime(self, datetime, normalize=False):
		"""
		Calculate roudtime relative to an UTC date.
		normalize unsure to set to 0 for not given units under the minimal unit.
		"""

		result = None

		parameters = dict()

		for unit, value in self.unit_values.iteritems():
			if unit is Period.WEEK:
				monthcalendar = calendar.monthcalendar(datetime.year, datetime.month)
				for week_index, week in enumerate(monthcalendar):
					if datetime.day in week:
						datetime_value = week_index
						break
			else:
				datetime_value = getattr(datetime, unit)
			sliding_period_value = datetime_value % value
			parameters[unit] = sliding_period_value

		sliding_period = Period(**parameters)
		#print sliding_period
		delta = sliding_period.get_delta()

		result = datetime - delta

		if normalize:  # set to minimal value for all units before self minimal unit
			parameters = dict()
			if Period.MICROSECOND not in self.unit_values:
				parameters[Period.MICROSECOND] = 0
				if Period.SECOND not in self.unit_values:
					parameters[Period.SECOND] = 0
					if Period.MINUTE not in self.unit_values:
						parameters[Period.MINUTE] = 0
						if Period.HOUR not in self.unit_values:
							parameters[Period.HOUR] = 0
							if Period.DAY not in self.unit_values:
								parameters[Period.DAY] = 1
								if Period.MONTH not in self.unit_values:
									parameters[Period.MONTH] = 1
			result = result.replace(**parameters)

		return result

	def get_max_unit(self):
		"""
		Get a dictionary which contains a unit and a value
		where unit is the last among Period.UNITS.
		"""

		result = None

		units = list(Period.UNITS)
		units.reverse()

		for unit in units:
			if unit in self.unit_values:
				result = {Period.UNIT: unit, Period.VALUE: self.unit_values[unit]}

		return result

	def __repr__(self):

		return "Period{0}".format(self.unit_values)

from collections import Iterable
from operator import itemgetter


class Interval(object):
	"""
	Manage points interval with sub intervals which are tuple of two numbers.
	"""

	class IntervalError(Exception):
		pass

	__slots__ = ['sub_intervals']

	_NUMBER = (float, long, int, complex)

	def __init__(self, *intervals):

		super(Interval, self).__init__()

		self.sub_intervals = Interval.sort_and_join_intersections(*intervals)

	def __repr__(self):

		result = "Interval{0}".format(self.sub_intervals)

		return result

	def __contains__(self, numbers_or_intervals):
		"""
		True iif input values or intervals are in this interval.
		values_or_interval must be numbers or Intervals.
		"""

		# return False by default.
		result = False

		def check_number_or_interval(number_or_interval, pos=None):
			"""
			Check if input number_or_interval is in self.sub_intervals.
			"""

			result = False

			if isinstance(number_or_interval, Iterable) and len(number_or_interval) == 2:

				result = number_or_interval[0] in self and number_or_interval[1] in self

			elif isinstance(number_or_interval, Interval):
				result = True

				for sub_interval in number_or_interval:
					if sub_interval[0] not in self or sub_interval[1] not in self:
						result = False
						break

			elif isinstance(number_or_interval, Interval._NUMBER):

				for sub_interval in self:
					if number_or_interval >= sub_interval[0] and number_or_interval <= sub_interval[1]:
						result = True
						break

			else:
				raise Interval.IntervalError(
					"Wrong input parameter {0}({1}){2}."
					.format(
						number_or_interval,
						type(number_or_interval),
						"" if pos is None else "at pos {0}".format(pos)))

			return result

		if isinstance(numbers_or_intervals, Iterable):
			result = len(numbers_or_intervals) > 0

			for index, number_or_interval in enumerate(numbers_or_intervals):
				if not check_number_or_interval(number_or_interval, index):
					result = False
					break

		else:
			result = check_number_or_interval(numbers_or_intervals)

		return result

	def __len__(self):
		"""
		Get number of values between all sub intervals.
		"""
		result = 0

		for sub_interval in self:
			result += sub_interval[1] - sub_interval[0]

		return result

	def __or__(self, interval):

		result = None

		if isinstance(interval, Interval):
			result = Interval(self.sub_intervals + interval.sub_intervals)

		else:
			raise NotImplementedError()

		return result

	def __ior__(self, interval):

		if isinstance(interval, Interval):
			self.sub_intervals = (self | interval).sub_intervals

	def __and__(self, interval):

		raise NotImplementedError()

	def __sub__(self, interval):

		raise NotImplementedError()

	def __iter__(self):
		"""
		Get self sub_intervals iterator.
		"""

		return iter(self.sub_intervals)

	def min(self):
		"""
		Get minimal point or None if no sub intervals.
		"""

		return self.sub_intervals[0][0] if len(self.sub_intervals) > 0 else None

	def max(self):
		"""
		Get maximal point or None if no sub intervals.
		"""

		return self.sub_intervals[-1][1] if len(self.sub_intervals) > 0 else None

	def is_empty(self):
		"""
		True iif this interval does not contain sub intervals.
		"""

		result = len(self.sub_intervals) == 0

		return result

	@staticmethod
	def sort_and_join_intersections(*intervals):
		"""
		Get intervals which are the result of a clean, sort and a join intersection \
		operation on input intervals.
		Get an interval which is a cleanable version of all input intervals.

		Input intervals can be empty or contains Intervals or Iterable of two float.
		"""

		result = []

		for index, interval in enumerate(intervals):

			if isinstance(interval, Interval):
				result += interval.sub_intervals

			elif isinstance(interval, Iterable):
				if len(interval) != 2:
					raise Interval.IntervalError(
						"Iterable interval {0} at pos {1} must contain only two elements"
						.format(interval, index))

				if isinstance(interval[0], Interval._NUMBER) and isinstance(interval[1], Interval._NUMBER):
					result.append(tuple(interval))

				else:
					raise Interval.IntervalError(
						"Wrong input interval {0} at pos {1}"
						.format(interval, index))

			elif isinstance(interval, Interval._NUMBER):
				sub_interval = (0, interval) if interval > 0 else (interval, 0)
				result.append(sub_interval)

			else:
				raise Interval.IntervalError(
					"Wrong input interval {0} at pos {1}"
					.format(interval, index))

		# sort intervals
		result, _result = [], sorted(result, key=itemgetter(0))

		index = 0

		while index < len(_result):
			interval = _result[index]

			index += 1

			for _index in range(index, len(_result)):
				_interval = _result[_index]

				index = _index

				if _interval[0] >= interval[0] and _interval[0] <= interval[1]:
					interval = (interval[0], max(interval[1], _interval[1]))
					index += 1

				else:
					break

			result.append(interval)

		result = tuple(result)

		return result


class TimeWindow(object):
	"""
	Manage second intervals with a timezone.
	"""

	class TimeWindowError(Exception):
		pass

	DEFAULT_DURATION = 60 * 60 * 24  # one day

	__slots__ = ['interval', 'timezone']

	def __init__(self, interval=None, timezone=0):
		"""
		interval is an Interval of timestamps, or one minimal timestamp until now or
		else a couple of timestamp.
		"""

		super(TimeWindow, self).__init__()

		if interval is None:
			stop = int(time())
			interval = Interval((stop - TimeWindow.DEFAULT_DURATION, stop))

		self.interval = interval if isinstance(interval, Interval) \
			else Interval(interval)

		if self.interval.is_empty():
			raise TimeWindow.TimeWindowError("Interval can not be empty")

		self.interval = TimeWindow.convert_to_seconds_interval(self.interval)

		self.timezone = timezone

	def __repr__(self):

		message = "TimeWindow(tz:{0}):{1}"
		result = message.format(self.timezone, self.interval)

		return result

	def __contains__(self, *timestamps):
		"""
		True if input timestamps are in this timewindow.
		"""

		result = timestamps in self.interval

		return result

	def start(self):
		"""
		Get first timestamp.
		"""

		result = float(self.interval.min())

		return result

	def stop(self):
		"""
		Get last timestamp.
		"""

		result = float(self.interval.max())

		return result

	def total_seconds(self):
		"""
		Returns seconds inside this timewindow.
		"""

		result = len(self.interval)

		return result

	def get_next_date(self, date, period, delta=None):
		"""
		Get next date of input date with timewindow parameters,
		period and optionaly a previous calculated delta.
		"""

		if delta is None:
			delta = period.get_delta(date)
		# check if next date is in exclusion dates of the input timewindow
		result = date + delta

		return result

	def get_previous_date(self, date, period, delta=None):
		"""
		Get previous date of input date with timewindow parameters,
		period and optionaly a previous calculated delta.
		"""

		if delta is None:
			delta = period.get_delta(date)
		# check if next date is in exclusion dates of the input timewindow
		result = date - delta

		return result

	@staticmethod
	def get_datetime(timestamp, timezone=0):
		"""
		Get the datetime corresponding to both input timestamp and timezone.
		"""

		td = td(seconds=timezone)
		result = dt.fromtimestamp(timestamp, td)

		return result

	@staticmethod
	def convert_to_seconds_interval(interval):
		"""
		Get interval in seconds from an interval.
		"""

		sub_intervals = []

		for sub_interval in interval:
			sub_intervals.append((int(sub_interval[0]), int(sub_interval[1])))

		result = Interval(*sub_intervals)

		return result
