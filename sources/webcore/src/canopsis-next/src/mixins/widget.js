import { createNamespacedHelpers } from 'vuex';

import viewMixin from './view';

const { mapGetters, mapActions } = createNamespacedHelpers('view/widget');

/**
 * @mixin Helpers for widget
 * @see src/mixins/view.js
 */
export default {
  mixins: [
    viewMixin,
  ],
  computed: {
    ...mapGetters({
      getWidget: 'getItem',
    }),
  },
  methods: {
    ...mapActions({
      saveWidget: 'saveItem',
    }),
  },
};
