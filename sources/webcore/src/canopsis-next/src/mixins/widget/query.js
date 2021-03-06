import omit from 'lodash/omit';
import isEqual from 'lodash/isEqual';

import Pagination from '@/components/tables/pagination.vue';
import queryMixin from '@/mixins/query';
import dateIntervals from '@/helpers/date-intervals';
import { convertWidgetToQuery, convertUserPreferenceToQuery } from '@/helpers/query';
import { WIDGET_TYPES } from '@/constants';

/**
 * @mixin Add query logic
 */
export default {
  components: {
    Pagination,
  },
  mixins: [queryMixin],
  computed: {
    query: {
      get() {
        return this.getQueryById(this.widget.id);
      },
      set(query) {
        return this.updateQuery({ id: this.widget.id, query });
      },
    },

    vDataTablePagination: {
      get() {
        const descending = this.query.sortDir !== null ? this.query.sortDir === 'DESC' : null;

        return { sortBy: this.query.sortKey, descending };
      },
      set(value) {
        const isNotEqualSortBy = value.sortBy !== this.vDataTablePagination.sortBy;
        const isNotEqualDescending = value.descending !== this.vDataTablePagination.descending;

        if (isNotEqualSortBy || isNotEqualDescending) {
          this.query = {
            ...this.query,
            sortKey: value.sortBy,
            sortDir: value.descending ? 'DESC' : 'ASC',
          };
        }
      },
    },
  },
  watch: {
    query(value, oldValue) {
      if (!isEqual(value, oldValue)) {
        this.fetchList();
      }
    },
  },
  async mounted() {
    await this.fetchUserPreferenceByWidgetId({ widgetId: this.widget.id });

    this.query = {
      ...this.query,
      ...convertWidgetToQuery(this.widget),
      ...convertUserPreferenceToQuery(this.userPreference),
    };

    await this.fetchList(); // TODO: remove it when we will finish settings integration for weather
  },
  methods: {
    getQuery() {
      const query = omit(this.query, [
        'page',
        'interval',
        'sortKey',
        'sortDir',
      ]);

      const { page, interval } = this.query;

      if (interval && interval !== 'custom') {
        try {
          const { tstart, tstop } = dateIntervals[interval]();

          query.tstart = tstart;
          query.tstop = tstop;
        } catch (err) {
          console.warn(err);
        }
      }

      if (this.query.sortKey) {
        query.sort_key = this.query.sortKey;
        query.sort_dir = this.query.sortDir;
      }

      query.limit = this.query.limit;
      query.skip = ((page - 1) * this.query.limit) || 0;

      return query;
    },
    fetchList() {
      const fetchListMethodsMap = {
        [WIDGET_TYPES.context]: 'fetchContextEntitiesList',
        [WIDGET_TYPES.alarmList]: 'fetchAlarmsList',
      };

      this[fetchListMethodsMap[this.widget.xtype]]({
        widgetId: this.widget.id,
        params: this.getQuery(),
      });
    },
  },
};
