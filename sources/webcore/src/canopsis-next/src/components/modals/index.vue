<template lang="pug">
  div
    modal(
    v-for="(modal, key, index) in modals",
    :key="key",
    :modal="modal",
    :index="index",
    :dialogProps="dialogPropsMap[modal.name] || defaultDialogProps",
    )
      component(:is="modal.name", :modal="modal")
</template>

<script>
import { createNamespacedHelpers } from 'vuex';

import { MODALS } from '@/constants';

import Modal from './layouts/modal.vue';
import CreateAckEvent from './alarm/create-ack-event.vue';
import CreateAssociateTicketEvent from './alarm/create-associate-ticket-event.vue';
import CreateCancelEvent from './alarm/create-cancel-event.vue';
import CreateChangeStateEvent from './alarm/create-change-state-event.vue';
import CreateDeclareTicketEvent from './alarm/create-declare-ticket-event.vue';
import CreateSnoozeEvent from './alarm/create-snooze-event.vue';
import EditLiveReporting from './alarm/edit-live-reporting.vue';
import MoreInfos from './alarm/more-infos.vue';
import CreatePbehavior from './pbehavior/create-pbehavior.vue';
import PbehaviorList from './pbehavior/pbehavior-list.vue';
import Confirmation from './common/confirmation.vue';
import CreateWidget from './common/create-widget.vue';
import CreateWatcher from './context/create-watcher.vue';
import CreateEntity from './context/create-entity.vue';
import Watcher from './watcher/watcher.vue';

const { mapGetters: modalMapGetters } = createNamespacedHelpers('modal');

/**
 * Wrapper for all modal windows
 */
export default {
  components: {
    Modal,
    CreateAckEvent,
    CreateAssociateTicketEvent,
    CreateCancelEvent,
    CreateChangeStateEvent,
    CreateDeclareTicketEvent,
    CreateSnoozeEvent,
    CreatePbehavior,
    PbehaviorList,
    EditLiveReporting,
    MoreInfos,
    Confirmation,
    CreateEntity,
    CreateWatcher,
    CreateWidget,
    Watcher,
  },
  data() {
    return {
      dialogPropsMap: {
        [MODALS.pbehaviorList]: { maxWidth: 1280, lazy: true },
        [MODALS.createWidget]: { maxWidth: 500, lazy: true },
      },
      defaultDialogProps: { maxWidth: 700, lazy: true },
    };
  },
  computed: {
    ...modalMapGetters(['modals']),
  },
};
</script>
