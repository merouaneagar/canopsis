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

from canopsis.common.ws import route
from canopsis.context_graph.manager import ContextGraph
from canopsis.context_graph.import_ctx import ContextGraphImport
from uuid import uuid4
import json as j
import os

manager = ContextGraph()
import_manager = ContextGraphImport()

__FILE = "/opt/canopsis/tmp/import-{0}.json"
__IMPORT_ID = "import_id"
__ERROR = "error"
__STORE_ERROR = "Impossible to store the file on the disk : {0}."
__OTHER_ERROR = "An error occured : {0}."
__CANNOT_EXEC_IMPORT = "Error while calling the process responsible"\
                       " of the import"

def get_uuid():
    """Return an UUID never used for an import. If the generated UUID is already
    used, try again until an UUID not used is created"""

    uuid = uuid4()
    while import_manager.check_id(uuid):
        uuid = uuid4()

    return str(uuid)

def exports(ws):

    @route(ws.application.get, name='contextgraph/all')
    def all():
        """
            :return all json for d3 representation
        """
        return manager.get_entities()

    @route(
        ws.application.put,
        payload=['entity']
    )
    def put_entities(entity):
        """
            put entities in db
        """
        return manager.create_entity(entity)

    @route(
        ws.application.post,
        payload=['entity']
    )
    def update_entity(id_, entity):
        """
            update entity in db
        """
        return manager.update_entity(id_, entity)


    @route(
        ws.application.delete,
        payload=['id_']
    )
    def delete_entity(id_):
        """
            remove  etity
        """
        return manager.delete_entity(id_)


    @route(
        ws.application.get,
        payload=['query', 'projection', 'limit', 'sort', 'with_count']
    )
    def get_entities(
            query={},
            projection={},
            limit=0,
            sort=False,
            with_count=False
    ):
        return get_entities(
            query=query,
            projection=projection,
            limit=limit,
            sort=sort,
            with_count=with_count
        )

    @route(
        ws.application.put,
        name='api/contextgraph/import',
        payload=['json']
    )
    def put_graph(json='{}'):
        uuid = get_uuid()
        try:
            file_ = __FILE.format(uuid)


            if os.path.exists(file_):
                return {__ERROR: __STORE_ERROR.format("A file with the same "\
                                                      "name already exists")}

            with open(file_, 'w') as fd:
                j.dump(json, fd)

            status = os.spawnl(os.P_NOWAIT, "import.py", file_)

            if status == 127:
                return {__ERROR: __CANNOT_EXEC_IMPORT}

            return {__IMPORT_ID : str(uuid)}

        except IOError as ioerror:
            return {__ERROR: __STORE_ERROR.format(str(ioerror))}

        except Exception as error:
            return {__ERROR: __OTHER_ERROR.format(str(error))}

    @route(
        ws.application.get,
        name='api/contextgraph/d3graph'
    )
    def get_graph():
        entities_list = manager.get_entities()

        ret_json = {
            'links':[],
            'nodes':[]
        }

        for i in entities_list:
            ret_json['nodes'].append({'group':1, 'id': i['_id']})

        for i in entities_list:
            source = i['_id']
            for target in i['depends']:
                ret_json['links'].append({'value': 1, 'source': source, 'target': target})

        directory = '/opt/canopsis/var/www/src/canopsis/d3graph'
        if not os.path.exists(directory):
            os.makedirs(directory)
            l = ['<!DOCTYPE html>\n', '<meta charset="utf-8">\n', '<style>\n', '\n', '.links line {\n', '  stroke: #999;\n', '  stroke-opacity: 0.6;\n', '}\n', '\n', '.nodes circle {\n', '  stroke: #fff;\n', '  stroke-width: 1.5px;\n', '}\n', '\n', '</style>\n', '<svg width="1000" height="900"></svg>\n', '<script src="https://d3js.org/d3.v4.min.js"></script>\n', '<script>\n', '\n', 'var svg = d3.select("svg"),\n', '    width = +svg.attr("width"),\n', '    height = +svg.attr("height");\n', '\n', 'var color = d3.scaleOrdinal(d3.schemeCategory20);\n', '\n', 'var simulation = d3.forceSimulation()\n', '    .force("link", d3.forceLink().id(function(d) { return d.id; }))\n', '    .force("charge", d3.forceManyBody())\n', '    .force("center", d3.forceCenter(width / 2, height / 2));\n', '\n', 'd3.json("graph.json", function(error, graph) {\n', '  if (error) throw error;\n', '\n', '  var link = svg.append("g")\n', '      .attr("class", "links")\n', '    .selectAll("line")\n', '    .data(graph.links)\n', '    .enter().append("line")\n', '      .attr("stroke-width", function(d) { return Math.sqrt(d.value); });\n', '\n', '  var node = svg.append("g")\n', '      .attr("class", "nodes")\n', '    .selectAll("circle")\n', '    .data(graph.nodes)\n', '    .enter().append("circle")\n', '      .attr("r", 5)\n', '      .attr("fill", function(d) { return color(d.group); })\n', '      .call(d3.drag()\n', '          .on("start", dragstarted)\n', '          .on("drag", dragged)\n', '          .on("end", dragended));\n', '\n', '  node.append("title")\n', '      .text(function(d) { return d.id; });\n', '\n', '  simulation\n', '      .nodes(graph.nodes)\n', '      .on("tick", ticked);\n', '\n', '  simulation.force("link")\n', '      .links(graph.links);\n', '\n', '  function ticked() {\n', '    link\n', '        .attr("x1", function(d) { return d.source.x; })\n', '        .attr("y1", function(d) { return d.source.y; })\n', '        .attr("x2", function(d) { return d.target.x; })\n', '        .attr("y2", function(d) { return d.target.y; });\n', '\n', '    node\n', '        .attr("cx", function(d) { return d.x; })\n', '        .attr("cy", function(d) { return d.y; });\n', '  }\n', '});\n', '\n', 'function dragstarted(d) {\n', '  if (!d3.event.active) simulation.alphaTarget(0.3).restart();\n', '  d.fx = d.x;\n', '  d.fy = d.y;\n', '}\n', '\n', 'function dragged(d) {\n', '  d.fx = d3.event.x;\n', '  d.fy = d3.event.y;\n', '}\n', '\n', 'function dragended(d) {\n', '  if (!d3.event.active) simulation.alphaTarget(0);\n', '  d.fx = null;\n', '  d.fy = null;\n', '}\n', '\n', '</script>\n', '\n']
            a = open('/opt/canopsis/var/www/src/canopsis/d3graph/index.html', 'a')
            for i in l:
                a.write(i)
            a.close()
        f = open('/opt/canopsis/var/www/src/canopsis/d3graph/graph.json', 'w')
        f.write(j.dumps(ret_json))
        f.close()

        return ret_json

    @route(
        ws.application.get,
        name='api/contextgraph/graphimpact',
        payload=['_id', 'deepness']
    )
    def get_graph_impact(_id, deepness=None):
        return manager.get_graph_impact(_id, deepness)

    @route(
        ws.application.get,
        name='api/contextgraph/graphdepends',
        payload=['_id', 'deepness']
    )
    def get_graph_depends(_id, deepness=None):
        return manager.get_graph_depends(_id, deepness)

    @route(
        ws.application.get,
        name='api/contextgraph/leavesdepends',
        payload=['_id', 'deepness']
    )
    def get_leaves_depends(_id, deepness=None):
        return manager.get_leaves_depends(_id, deepness)

    @route(
        ws.application.get,
        name='api/contextgraph/leavesimpact',
        payload=['_id', 'deepness']
    )
    def get_leaves_impact(_id, deepness=None):
        return manager.get_leaves_impact(_id, deepness)

    @ws.application.get('/api/contextgraph/import/status/<cid>')
    def get_status(cid):
        return import_manager.get_import_status(cid)
