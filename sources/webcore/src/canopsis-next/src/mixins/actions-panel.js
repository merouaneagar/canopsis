import modalMixin from '@/mixins/modal/modal';
import eventActionsMixin from '@/mixins/event-actions';
import { EVENT_ENTITY_TYPES, MODALS } from '@/constants';

/**
 * @mixin Mixin for the alarms list actions panel, show modal of the action
 */
export default {
  mixins: [modalMixin, eventActionsMixin],
  methods: {
    showActionModal(name) {
      return () => this.showModal({
        name,
        config: this.modalConfig,
      });
    },

    showAckRemoveModal() {
      this.showModal({
        name: MODALS.createCancelEvent,
        config: {
          ...this.modalConfig,
          title: 'modals.createAckRemove.title',
          eventType: EVENT_ENTITY_TYPES.ackRemove,
        },
      });
    },
  },
};
