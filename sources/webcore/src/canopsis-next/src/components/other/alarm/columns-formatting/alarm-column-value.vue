<template lang="pug">
  div
    div(v-if="component", :is="component", :alarm="alarm") {{ component.value }}
    ellipsis(
      v-else,
      :text="$options.filters.get(alarm, property.value, property.filter) || ''",
      :maxLetters="property.maxLetters"
    )
    info-popup-button(v-if="columnName", :columnName="columnName", :alarm="alarm", :widget="widget")
</template>

<script>
import State from '@/components/other/alarm/columns-formatting/alarm-column-value-state.vue';
import ExtraDetails from '@/components/other/alarm/columns-formatting/alarm-column-value-extra-details.vue';
import InfoPopupButton from '@/components/other/info-popup/popup-button.vue';
import Ellipsis from '@/components/tables/ellipsis.vue';

const PROPERTIES_COMPONENTS_MAP = {
  'v.state.val': 'state',
  extra_details: 'extra-details',
};

/**
 * Component to format alarms list columns
 *
 * @module alarm
 *
 * @prop {Object} alarm - Object representing the alarm
 * @prop {Object} widget - Object representing the widget
 * @prop {Object} property - Property concerned on the column
 */
export default {
  components: {
    State,
    ExtraDetails,
    InfoPopupButton,
    Ellipsis,
  },
  props: {
    alarm: {
      type: Object,
      required: true,
    },
    widget: {
      type: Object,
      required: true,
    },
    property: {
      type: Object,
      required: true,
    },
  },
  computed: {
    component() {
      return PROPERTIES_COMPONENTS_MAP[this.property.value];
    },
    columnName() {
      return this.property.value.split('.')[1];
    },
  },
};
</script>
