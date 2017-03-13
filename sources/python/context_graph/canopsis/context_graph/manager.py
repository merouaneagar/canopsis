# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from canopsis.middleware.registry import MiddlewareRegistry
from canopsis.configuration.configurable.decorator import conf_paths
from canopsis.configuration.configurable.decorator import add_category


@conf_paths('context_graph/manager.conf')
@add_category('CONTEXTGRAPH')
class ContextGraph(MiddlewareRegistry):
    """ContextGraph"""

    ENTITIES_STORAGE = 'entities_storage'
    ORGANISATIONS_STORAGE = 'organisations_storage'
    USERS_STORAGE = 'measurements_storage'

    def __init__(self, *args, **kwargs):
        """__init__

        :param *args:
        :param **kwargs:
        """
        super(ContextGraph, self).__init__(*args, **kwargs)

    def check_comp(self, comp_id):
        """_check_comp

        check if the component exists in database

        :param comp_id: id of component
        :return type: boolean
        """
        return len(list(self[ContextGraph.ENTITIES_STORAGE].get_elements(query={'_id': comp_id}))) > 0

    def get_entity(self,
                   id,
                   limit=0,
                   skip=0,
                   sort=None,
                   with_count=False,
                   extended=False,
                   context=None,
                   create_if_not_exists=False):
        """
        Retreive the entity identified by his id. If id is a list of id,
        get_entity return every entities who match the ids present in the list

        :param id the id of the entity. id can be a list
        :param int limit: Max number of elements to get. If 0 no limit.
        :param int skip: first element index among searched list.
        :type sort: list of {(str, {ASC, DESC}}), or str}
        :param bool with_count: If True (False by default), add
        count to the result.
        :param bool create_if_not_exists: Create the event entity if it does
            not exists (False by default).
        :return an entity as a dict
        :rtype: a dict or a None type.
        """
        #FIXME : guess the meaning of extended and add it in the doc
        #FIXME : guess the meaning of context and add it in the doc

        query = {"_id": None}
        if isinstance(id, type([])):
            ids = []
            for i in id:
                ids.append(i)
            query["_id"] = {"$in": ids}
        else:
            query["_id"] = id

        return list(self[ContextGraph.ENTITIES_STORAGE].get_elements(query=query))

    def put_entities(self, entities):
        """
        Store entities into database.
        """
        self[ContextGraph.ENTITIES_STORAGE].put_elements(entities)

    def check_re(self, re_id):
        """_check_re

        :param re_id:
        """
        return len(list(self[ContextGraph.ENTITIES_STORAGE].get_elements(query={'_id': re_id}))) > 0

    def check_conn(self, conn_id):
        """_check_conn

        :param conn_id:
        """
        return len(list(self[ContextGraph.ENTITIES_STORAGE].get_elements(query={'_id': conn_id}))) > 0

    def check_links(self, conn_id, comp_id, re_id):
        """_check_links

        :param conn_id:
        :param comp_id:
        :param re_id:
        """
        raise NotImplementedError

    def manage_comp_to_re_link(self, re_id, comp_id):
        """Update component-resource link"""
        comp = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': comp_id}))
        for i in comp:
            if re_id not in i['depends']:
                tmp = i
                tmp['depends'].append(re_id)
                self[ContextGraph.ENTITIES_STORAGE].put_element(element=tmp)

    def manage_re_to_conn_link(self, conn_id, re_id):
        """Update resource-connector link"""
        re = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': re_id}))
        for i in re:
            if conn_id not in i['depends']:
                tmp = i
                tmp['depends'].append(conn_id)
                self[ContextGraph.ENTITIES_STORAGE].put_element(element=tmp)

    def manage_comp_to_conn_link(self, conn_id, comp_id):
        """Update component-connector link"""
        comp = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': comp_id}))
        for i in comp:
            if conn_id not in i['depends']:
                tmp = i
                tmp['depends'].append(conn_id)
                self[ContextGraph.ENTITIES_STORAGE].put_element(element=tmp)

    def _check_conn_comp_link(self, conn_id, comp_id):
        """_check_conn_comp_link

        :param conn_id:
        :param comp_id:
        """
        conn = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': conn_id}))
        comp = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': comp_id}))
        for i in conn:
            for j in comp:
                if comp_id not in i['impact']:
                    tmp = i
                    tmp['impact'].append(comp_id)
                    self[ContextGraph.ENTITIES_STORAGE].put_element(
                        element=tmp)
                if conn_id not in j['depends']:
                    tmp = j
                    tmp['depends'].append(conn_id)
                    self[ContextGraph.ENTITIES_STORAGE].put_element(
                        element=tmp)

    def _check_conn_re_link(self, conn_id, re_id):
        """_checks_conn_re_link

        :param conn_id:
        :param re_id:
        """
        conn = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': conn_id}))
        re = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={'_id': re_id}))
        for i in conn:
            for j in re:
                if re_id not in i['impact']:
                    tmp = i
                    tmp['impact'].append(re_id)
                    self[ContextGraph.ENTITIES_STORAGE].put_element(
                        element=tmp)
                if conn_id not in j['depends']:
                    tmp = j
                    tmp['depends'].append(conn_id)
                    self[ContextGraph.ENTITIES_STORAGE].put_element(
                        element=tmp)

    def _check_comp_re_link(self, comp_id, re_id):
        """_check_com_re_link

        :param comp_id:
        :param re_id:
        """

    def add_comp(self, comp):
        """add_comp

        :param comp:
        """
        self[ContextGraph.ENTITIES_STORAGE].put_element(element=comp)

    def add_re(self, re):
        """add_re

        :param re:
        """
        self[ContextGraph.ENTITIES_STORAGE].put_element(element=re)

    def add_conn(self, conn):
        """add_conn

        :param conn:
        """
        self[ContextGraph.ENTITIES_STORAGE].put_element(element=conn)

    def get_all_entities(self):
        """
            get all entities ids by types
        """
        entities = list(self[ContextGraph.ENTITIES_STORAGE].get_elements(
            query={}))
        ret_val = set([])
        for i in entities:
            ret_val.add(i['_id'])
        # pritn(ret_val)
        return ret_val

    def get(_type, names, context, extended):
        """
            function in context v1 ws
        """

    def get_by_id(ids, limit, skip, sort, with_count):
        """
            function in context v1 ws
        """
        result = self[ContextGraph.ENTITIES_STORAGE].get_elements(
            ids=ids, 
            limit=limit, 
            skip=skip,
            sort=sort,
            with_count=with_count
        )

        return result 


    def find(_type, context, _filter, extended, limit, skip, sort, with_count):
        """
            function in context v1 ws
        """

    def put(ids, _type, context, extended):
        """
            function in ws context v1
        """

    def unify_entities(entities, extended):
        """
            function in ws context v1
        """

    def split_id(self, eid):
        """
            split an eid to get a dict with conn_id, comp_id and re_id
        """

        re_id = None
        comp_id = None
        conn_id = None

        tab_id = eid.split('/')
        
        conn_id = '{0}/{1}'.format(tab_id[0], tab_id[1])
        comp_id = '{0}'.format(tab_id[2])

        if len(tab_id) == 4: 
            re_id = '{0}/{1}'.format(tab_id[3], tab_id[2])
        
        result={
            'conn_id': conn_id,
            'comp_id': comp_id,
            're_id': re_id
        }
        return result
