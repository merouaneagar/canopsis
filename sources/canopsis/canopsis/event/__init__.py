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

from socket import setdefaulttimeout, getfqdn, gethostname, gethostbyaddr
from time import time
from re import compile as re_compile
from logging import getLogger

from canopsis.old.storage import get_storage
from canopsis.old.account import Account


class Event(object):
    """
    Manage event content

    An event contains information and require a type and source_type.
    """

    SOURCE_TYPE = 'source_type'
    SOURCE = 'source'
    EVENT_TYPE = 'event_type'
    DATA = 'data'
    META = 'meta'
    RESOURCE = 'resource'
    COMPONENT = 'component'
    CONNECTOR = 'connector'
    CONNECTOR_NAME = 'connector_name'
    ENTITY = 'entity'  #: entity id item name

    __slots__ = (EVENT_TYPE, SOURCE, DATA, META)

    def __init__(self, source, data, meta, _type=None):

        super(Event, self).__init__()

        self.type = type(self).__name__.lower() if _type is None else _type
        self.source = source
        self.data = data
        self.meta = meta

    @classmethod
    def new_event(event_class, **old_event):
        """
        Create an Event from an old event (ficus and older version).
        """

        _type = event_class.__name__.lower()
        _type = old_event.pop(Event.EVENT_TYPE, _type)
        source = old_event.pop(Event.SOURCE)
        data = old_event.pop(Event.DATA, None)
        meta = old_event.pop(Event.META, None)

        result = Event(
            _type=_type,
            source=source,
            data=data,
            meta=meta)

        return result

    @classmethod
    def get_type(cls):
        """
        Get unique event type name
        """

        result = cls.__name__.lower()

        return result


# Change default timeout from 1 to 3 , conflict with gunicorn
setdefaulttimeout(3)

regexp_ip = re_compile(
    "([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})")

dns_cache = {}
cache_time = 60 * 30  # 30min

logger = getLogger('event')


def forger(
    event_type,
    entity=None,
    connector=Event.CONNECTOR,
    connector_name=Event.CONNECTOR_NAME,
    source_type='component',
    component=None,
    resource=None,
    timestamp=None,
    state=0,
    state_type=1,
    output=None,
    long_output=None,
    perf_data=None,
    perf_data_array=None,
    address=None,
    domain=None,
    reverse_lookup=True,
    display_name=None,
    tags=[],
    ticket=None,
    ref_rk=None,
    component_problem=False,
    author=None,
    perimeter=None,
    keep_state=None,
    **kwargs
):
    """
    Build an event from scratch.
    """

    if not timestamp:
        timestamp = int(time())

    if not component:
        component = getfqdn()
        if not component:
            component = gethostname()

    if not state:
        state = 0

    if not address:
        if bool(regexp_ip.match(component)):
            address = component
            if reverse_lookup:
                dns = None

                # get from cache
                try:
                    (timestamp, dns) = dns_cache[address.replace('.', '-')]
                    logger.info("Use DNS lookup from cache")
                    if (timestamp + cache_time) < int(time()):
                        logger.info(" + Cache is too old")
                        del dns_cache[address.replace('.', '-')]
                        dns = None
                except Exception:
                    logger.info(" + '%s' not in cache" % address)

                # reverse lookup
                if not dns:
                    try:
                        logger.info(
                            "DNS reverse lookup for '%s' ..." % address)
                        dns = gethostbyaddr(address)
                        logger.info(" + Succes: '%s'" % dns[0])
                        dns_cache[address.replace('.', '-')] = \
                            (int(time()), dns)
                    except Exception:
                        logger.info(" + Failed")

                # Dns ok
                if dns:
                    # Split FQDN
                    fqdn = dns[0]
                    component = fqdn.split('.', 1)[0]
                    if not domain:
                        try:
                            domain = fqdn.split('.', 1)[1]
                        except Exception:
                            pass

                if dns:
                    logger.info(" + Component: %s" % component)
                    logger.info(" + Address:   %s" % address)
                    logger.info(" + Domain:    %s" % domain)

    dump = {
        'connector': connector,
        'connector_name': connector_name,
        'event_type': event_type,
        'source_type': source_type,
        'component': component,
        'timestamp': timestamp,
        'state': state,
        'state_type': state_type,
        'output': output,
        'long_output': long_output,
    }

    if entity:
        dump[Event.ENTITY] = entity

    if resource:
        dump[Event.SOURCE_TYPE] = Event.RESOURCE
        dump[Event.RESOURCE] = resource

    if author is not None:
        dump["author"] = author

    if perimeter:
        dump["perimeter"] = perimeter

    if keep_state:
        dump["keep_state"] = keep_state

    if perf_data:
        dump["perf_data"] = perf_data

    if perf_data_array:
        dump["perf_data_array"] = perf_data_array

    if address:
        dump["address"] = address

    if domain:
        dump["domain"] = domain

    if tags:
        dump["tags"] = tags

    if display_name:
        dump["display_name"] = display_name

    if ticket:
        dump["ticket"] = ticket

    if ref_rk:
        dump["ref_rk"] = ref_rk

    if event_type == 'check' and resource:
        dump['component_problem'] = component_problem

    if kwargs:
        dump.update(kwargs)

    return dump


def get_routingkey(event):
    """
    Build the routing key from an event.

    If the key 'resource' is present and != '', 'source_type' is forced to
    'resource', otherwise 'component'.

    This function mutates the 'source_type' field if necessary.

    :raise KeyError: on missing required info
    """
    event[Event.SOURCE_TYPE] = Event.COMPONENT
    if event.get(Event.RESOURCE, ''):
        event[Event.SOURCE_TYPE] = Event.RESOURCE

    rk = u"{}.{}.{}.{}.{}".format(
        event[Event.CONNECTOR],
        event[Event.CONNECTOR_NAME],
        event[Event.EVENT_TYPE],
        event[Event.SOURCE_TYPE],
        event[Event.COMPONENT]
    )

    if event.get(Event.RESOURCE, ''):
        rk = u"{}.{}".format(rk, event[Event.RESOURCE])

    return rk


def is_component_problem(event):
    if event.get(Event.RESOURCE, '') and event['state'] != 0:
        storage = get_storage(
            namespace='entities',
            account=Account(user='root', group='root')).get_backend()

        component = storage.find_one({
            'type': 'component',
            'name': event[Event.COMPONENT]
        })

        if component and 'state' in component and component['state'] != 0:
            return True

    return False


def is_host_acknowledged(event):
    if is_component_problem(event):
        storage = get_storage(
            namespace='entities',
            account=Account(user='root', group='root')).get_backend()

        ack = storage.find_one({
            'type': 'ack',
            'component': event[Event.COMPONENT],
            'resource': None
        })

        if ack:
            return True

    return False
