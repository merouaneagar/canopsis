/*
 * Copyright (c) 2015 "Capensis" [http://www.capensis.com]
 *
 * This file is part of Canopsis.
 *
 * Canopsis is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Canopsis is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Canopsis. If not, see <http://www.gnu.org/licenses/>.
 */

window.bricks['core'].schemasArray = ["text!canopsis/core/schemas/crecord.loggedaccount.json","text!canopsis/core/schemas/crecord.userview.json","text!canopsis/core/schemas/crecord.userviewsimplemodel.json","text!canopsis/core/schemas/jsruntimeconfiguration.json","text!canopsis/core/schemas/livereporting.json","text!canopsis/core/schemas/mixin.criticitylevels.json","text!canopsis/core/schemas/mixin.json","text!canopsis/core/schemas/notification.json","text!canopsis/core/schemas/widget.containerwidget.json","text!canopsis/core/schemas/widget.json","text!canopsis/core/schemas/widget.wgraph.json","text!canopsis/core/schemas/widgetwrapper.json"];

define(window.bricks['core'].schemasArray, function () {
    for (var i = 0; i < arguments.length; i++) {
        var schemaName = window.bricks['core'].schemasArray[i];
        var urlPrefix = 'canopsis/core/schemas/';

        //remove "text!" and the brick schema folder prefix
        schemaName = schemaName.slice(5 + urlPrefix.length);
        //remove ".json at the end"
        schemaName = schemaName.slice(0, -5);
        schema = JSON.parse(arguments[i]);
        record = {
            id: schemaName,
            _id: schemaName,
            crecord_name: schemaName.split('.'),
            schema: schema
        };
        record.crecord_name = record.crecord_name[record.crecord_name.length -1];

        window.schemasToLoad.push(record);
    }
 });
