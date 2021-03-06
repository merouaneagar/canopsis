<template lang="pug">
  v-tabs(v-model="activeTab" slider-color="blue darken-4" centered)
    v-tab(:disabled="isRequestStringChanged") {{$t('filterEditor.tabs.visualEditor')}}
    v-tab-item
      v-container
        filter-group(
        @update:group="updateFilter",
        :group="filter",
        :possibleFields="possibleFields",
        isInitial
        )
    v-tab(@click="openAdvancedTab") {{$t('filterEditor.tabs.advancedEditor')}}
    v-tab-item
      v-text-field(
      v-model="requestString",
      :label="$t('filterEditor.tabs.advancedEditor')",
      @input="updateRequestString",
      rows="10",
      textarea,
      )
      v-layout(justify-center)
        v-flex(xs10 md-6)
          v-alert(:value="parseError", type="error") {{ parseError }}
      v-btn(@click="parse", :disabled="!isRequestStringChanged") {{$t('common.parse')}}
    v-tab(@click="openResultsTab", :disabled="isRequestStringChanged") {{$t('filterEditor.tabs.results')}}
    v-tab-item
      filter-results(:filter="request")
</template>


<script>
import cloneDeep from 'lodash/cloneDeep';
import isEmpty from 'lodash/isEmpty';

import EventBus from '@/event-bus';
import { FILTER_DEFAULT_VALUES } from '@/constants';

import parseGroupToFilter from '@/helpers/filter-editor/parse-group-to-filter';
import parseFilterToRequest from '@/helpers/filter-editor/parse-filter-to-request';

import FilterGroup from '@/components/other/filter-editor/partial/filter-group.vue';
import FilterResults from '@/components/other/filter-editor/partial/filter-results.vue';

/**
 * Component to create new MongoDB filter
 *
 * @prop {string} value - Initial value for filter
 *
 * @event input
 */
export default {
  components: {
    FilterGroup,
    FilterResults,
  },
  props: {
    value: {
      type: String,
      default: '',
    },
  },
  data() {
    let filter = cloneDeep(FILTER_DEFAULT_VALUES.group);

    if (this.value !== '') {
      const valueObject = JSON.parse(this.value);

      if (!isEmpty(valueObject)) {
        filter = parseGroupToFilter(valueObject);
      }
    }

    return {
      filter,
      activeTab: 0,
      requestString: '',
      parseError: '',
      isRequestStringChanged: false,
      possibleFields: ['component_name', 'connector_name', 'connector', 'resource'],
    };
  },
  computed: {
    request() {
      try {
        return parseFilterToRequest(this.filter);
      } catch (err) {
        return err.message;
      }
    },
  },
  methods: {
    updateFilter(value) {
      this.filter = value;
      this.$emit('input', JSON.stringify(parseFilterToRequest(value)));
    },

    updateRequestString() {
      this.isRequestStringChanged = true;
    },

    openAdvancedTab() {
      if (!this.isRequestStringChanged) {
        this.requestString = JSON.stringify(this.request, undefined, 4);
      }
    },

    openResultsTab() {
      EventBus.$emit('filter-editor:results:fetch');
    },

    parse() {
      this.parseError = '';

      try {
        if (this.requestString !== '') {
          this.updateFilter(parseGroupToFilter(JSON.parse(this.requestString)));
          this.isRequestStringChanged = false;
        } else {
          this.requestString = JSON.stringify(this.request, undefined, 4);
          this.isRequestStringChanged = false;
        }
      } catch (err) {
        this.parseError = this.$t('filterEditor.errors.invalidJSON');
      }
    },
  },
};
</script>
