<template lang="pug">
v-card-text
  v-container
    v-layout(row)
      v-text-field(
        :label="$t('common.name')",
        :value="name",
        @input="$emit('update:name', $event)",
        :error-messages="errors.collect('name')",
        v-validate="'required'",
        data-vv-name="name"
      )
    v-layout(row)
      v-text-field(
        :label="$t('common.description')",
        :value="description",
        @input="$emit('update:description', $event)",
        data-vv-name="description",
        :error-messages="errors.collect('description')",
        multi-line
      )
    v-layout(row)
      v-switch(
        :label="$t('common.enabled')",
        :input-value="enabled",
        @change="$emit('update:enabled', $event)"
      )
      v-select(
        :items="types",
        :value="entityType",
        data-vv-name="type",
        v-validate="'required'",
        :error-messages="errors.collect('type')",
        @input="$emit('update:type', $event)",
        label="Type",
        single-line
      )
    v-layout(wrap)
      v-flex(xs12)
        entities-select(label="Impacts", :entities="impact", @updateEntities="updateImpact")
      v-flex(xs12)
        entities-select(label="Dependencies", :entities="depends", @updateEntities="updateDepends")
</template>

<script>
import { MODALS } from '@/constants';

import EntitiesSelect from './entities-select.vue';

/**
 * Form to create a new entity
 *
 * @prop {String} [name] - Name of the entity (null if creating a new entity)
 * @prop {String} [description] - Description on the entity (null if creating a new entity)
 * @prop {String} [type] - Type of the entity (null if creating a new entity)
 * @prop {Array} [impact] - List of the entity's impacts (null if creating a new entity)
 * @prop {Array} [depends] - List of the entity's depends (null if creating a new entity)
 * @prop {Boolean} [enabled] - Whether the entity is enabled or not
 *
 * @event name#update
 * @event description#update
 * @event enabled#update
 * @event type#update
 *
 * @module context
 */
export default {
  name: MODALS.createEntity,
  inject: ['$validator'],
  components: {
    EntitiesSelect,
  },
  props: {
    name: {
      type: String,
      default: '',
    },
    description: {
      type: String,
      default: '',
    },
    type: {
      type: String,
      default: '',
    },
    impact: {
      type: Array,
      default() {
        return [];
      },
    },
    depends: {
      type: Array,
      default() {
        return [];
      },
    },
    enabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      showValidationErrors: true,
      types: [
        {
          text: this.$t('modals.createEntity.fields.types.connector'),
          value: 'connector',
        },
        {
          text: this.$t('modals.createEntity.fields.types.component'),
          value: 'component',
        },
        {
          text: this.$t('modals.createEntity.fields.types.resource'),
          value: 'resource',
        },
      ],
    };
  },
  computed: {
    entityType() {
      let entityType;
      this.types.map((item, index) => {
        if (this.type === item.value) {
          return entityType = this.types[index];
        }
        return null;
      });
      return entityType;
    },
  },
  methods: {
    updateImpact(entities) {
      this.$emit('update:impact', entities);
    },
    updateDepends(entities) {
      this.$emit('update:depends', entities);
    },
  },
};
</script>

<style scoped>
  .tooltip {
    flex: 1 1 auto;
  }
</style>
