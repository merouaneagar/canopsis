#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------
# Copyright (c) 2011 "Capensis" [http://www.capensis.com]
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

from canopsis.engines import Engine

from bson import BSON
from json import loads
from time import time


class engine(Engine):
    etype = "cleaner"

    def work(self, body, msg, *args, **kargs):
        ## Sanity Checks
        rk = msg.delivery_info['routing_key']
        if not rk:
            raise Exception("Invalid routing-key '%s' (%s)" % (rk, body))

        #self.logger.info( body )
        ## Try to decode event
        if isinstance(body, dict):
            event = body
        else:
            self.logger.debug(" + Decode JSON")
            try:
                if isinstance(body, str):
                    try:
                        event = loads(body)
                        self.logger.debug("   + Ok")
                    except Exception as err:
                        try:
                            self.logger.debug(" + Try hack for windows string")
                            # Hack for windows FS -_-
                            event = loads(body.replace('\\', '\\\\'))
                            self.logger.debug("   + Ok")
                        except Exception as err:
                            try:
                                self.logger.debug(" + Decode BSON")
                                bson = BSON(body)
                                event = bson.decode()
                                self.logger.debug("   + Ok")
                            except Exception as err:
                                raise Exception(err)

            except Exception as err:
                self.logger.error("   + Failed (%s)" % err)
                self.logger.debug("RK: '%s', Body:" % rk)
                self.logger.debug(body)
                raise Exception("Impossible to parse event '%s'" % rk)

        event['rk'] = rk

        if "resource" in event:
            if not isinstance(event['resource'], basestring):
                event['resource'] = ''
            else:
                if isinstance(event['resource'], unicode):
                    event['resource'] = event['resource'].encode("utf-8")

        # Clean tags field
        event['tags'] = event.get('tags', [])

        tags = event['tags']

        if isinstance(tags, str) and tags != "":
            event['tags'] = [event['tags']]

        elif not isinstance(tags, list):
            event['tags'] = []

        event["timestamp"] = int(event.get("timestamp", time()))

        event["state"] = event.get("state", 0)
        event["state_type"] = event.get("state_type", 1)
        event["event_type"] = event.get("event_type", "check")

        default_status = 0 if not event["state"] else 1
        event["status"] = event.get("status", default_status)

        return event