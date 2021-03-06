<template lang="pug">
  v-card
    v-card-title
      span.headline {{ $t('modals.createAckEvent.title') }}
    v-card-text
      v-container
        v-layout(row align-center)
          v-flex.text-xs-center
            alarm-general-table(:items="items")
        v-layout(row)
          v-divider.my-3
        v-layout(row)
          v-text-field(
          :label="$t('modals.createAckEvent.fields.ticket')",
          :error-messages="errors.collect('ticket')",
          v-model="form.ticket",
          v-validate="rules",
          data-vv-name="ticket"
          )
        v-layout(row)
          v-text-field(
          :label="$t('modals.createAckEvent.fields.output')",
          :error-messages="errors.collect('output')",
          v-model="form.output",
          v-validate="rules",
          data-vv-name="output",
          multi-line
          )
        v-layout(row)
          v-tooltip(top)
            v-checkbox(
            slot="activator",
            v-model="ack_resources",
            :label="$t('modals.createAckEvent.fields.ackResources')"
            )
              span(slot-name="label") {{  }}
            span {{ $t('modals.createAckEvent.tooltips.ackResources') }}
    v-card-actions
      v-btn(@click.prevent="submit", color="primary") {{ $t('common.actions.acknowledge') }}
      v-btn(
      @click.prevent="submitWithDeclare",
      color="warning"
      ) {{ $t('common.actions.acknowledgeAndReport') }}
</template>

<script>
import AlarmGeneralTable from '@/components/other/alarm/alarm-general-list.vue';
import modalInnerItemsMixin from '@/mixins/modal/modal-inner-items';
import eventActionsMixin from '@/mixins/event-actions';
import { EVENT_ENTITY_TYPES, MODALS } from '@/constants';

/**
 * Modal to create an ack event
 */
export default {
  name: MODALS.createAckEvent,
  $_veeValidate: {
    validator: 'new',
  },
  components: {
    AlarmGeneralTable,
  },
  mixins: [modalInnerItemsMixin, eventActionsMixin],
  data() {
    return {
      showValidationErrors: false,
      ack_resources: false,
      form: {
        ticket: '',
        output: '',
      },
    };
  },
  computed: {
    rules() {
      return this.showValidationErrors ? 'required' : '';
    },
  },
  methods: {
    async create(withDeclare) {
      const ackEventData = this.prepareData(EVENT_ENTITY_TYPES.ack, this.items, this.form);

      await this.createEventAction({
        data: ackEventData,
      });

      if (withDeclare) {
        const declareTicketEventData = this.prepareData(EVENT_ENTITY_TYPES.declareTicket, this.items, this.form);

        await this.createEventAction({
          data: declareTicketEventData,
        });
      }

      await this.fetchAlarmListWithPreviousParams();

      this.hideModal();
    },

    async submitWithDeclare() {
      const formIsValid = await this.$validator.validateAll();

      if (formIsValid) {
        await this.create(true);
      }
    },

    async submit() {
      this.showValidationErrors = false;
      this.errors.clear();

      await this.create();
    },
  },
};
</script>

<style scoped>
  .tooltip {
    flex: 1 1 auto;
  }
</style>
