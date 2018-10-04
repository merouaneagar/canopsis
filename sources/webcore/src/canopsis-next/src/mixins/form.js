import omit from 'lodash/omit';

import uid from '@/helpers/uid';

const eventKeyComputed = uid('eventKey');
const formKeyComputed = uid('formKey');

/**
 * @mixin Form mixin
 */
export default {
  computed: {
    [formKeyComputed]() {
      if (this.$options.model && this.$options.model.prop) {
        return this.$options.model.prop;
      }

      return 'value';
    },
    [eventKeyComputed]() {
      if (this.$options.model && this.$options.model.event) {
        return this.$options.model.event;
      }

      return 'input';
    },
  },
  methods: {
    /**
     * Emit event to parent with new object and with updated field
     *
     * @param {string} fieldName
     * @param {*} value
     */
    updateField(fieldName, value) {
      this.$emit(this[eventKeyComputed], { ...this[this[formKeyComputed]], [fieldName]: value });
    },

    /**
     * Emit event to parent with new object without field
     *
     * @param {string} fieldName
     */
    removeField(fieldName) {
      this.$emit(this[eventKeyComputed], omit(this[this[formKeyComputed]], [fieldName]));
    },

    /**
     * Emit event to parent with new array with new item
     *
     * @param {*} value
     */
    addItemIntoArray(value) {
      this.$emit(this[eventKeyComputed], [...this[this[formKeyComputed]], value]);
    },

    /**
     * Emit event to parent with new array with updated array item with updated field
     *
     * @param {number} index
     * @param {string} fieldName
     * @param {*} value
     */
    updateFieldInArrayItem(index, fieldName, value) {
      const items = [...this[this[formKeyComputed]]];

      items[index] = {
        ...items[index],
        [fieldName]: value,
      };

      this.$emit(this[eventKeyComputed], items);
    },

    /**
     * Emit event to parent with new array without array item
     *
     * @param {number} index
     */
    removeItemFromArray(index) {
      this.$emit(this[eventKeyComputed], this[this[formKeyComputed]].filter((v, i) => i !== index));
    },
  },
};