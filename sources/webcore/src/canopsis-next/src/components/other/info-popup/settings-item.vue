<template lang="pug">
  div
    v-container(v-for="(popup, index) in popups", :key="`info-popup-${index}`")
      v-card
        v-container
          v-layout(class="text-md-center")
            v-flex
              v-btn(color="error", @click="remove(index)") Delete
          v-layout
            v-flex(:justify-center="true")
              v-text-field(placeholder="Column", v-model="popup.column")
          v-layout
            v-flex(:justify-center="true")
              v-text-field(placeholder="Template", :multi-line="true", v-model="popup.template")
    v-btn(color="success", @click="add") Add
    v-btn(color="info", @click="save") Save

</template>

<script>
import entitiesWidgetMixin from '@/mixins/entities/widget';

/**
 * Component to add/remove info popup on a column of the alarms list
 *
 * @prop {Object} widget - Object representing the widget
 */
export default {
  mixins: [
    entitiesWidgetMixin,
  ],
  props: {
    widget: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      popups: [...this.widget.popup],
    };
  },
  methods: {
    remove(index) {
      this.popups.splice(index, 1);
    },
    add() {
      this.popups.push({
        column: '',
        template: '',
      });
    },
    save() {
      this.updateWidget({ widget: { ...this.widget, popup: this.popups } });
    },
  },
};
</script>
