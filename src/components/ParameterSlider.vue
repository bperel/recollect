<template>
  <div class="d-flex parameter">
    {{ name }}:
    <b-form-input
      :value="value"
      class="mx-3"
      type="range"
      :min="min"
      :max="max"
      :step="step"
      @input="$emit('change', parseInt($event))"
    />
    <b-button size="sm" @click="$emit('auto', name)">
      <b-icon-lightning-fill />
    </b-button>
  </div>
</template>

<script>
import { BIconLightningFill } from "bootstrap-vue";

export default {
  name: "ParameterSlider",

  components: {
    BIconLightningFill,
  },

  props: {
    name: {
      type: String,
      required: true,
    },
    min: {
      type: Number,
      required: true,
    },
    max: {
      type: Number,
      required: true,
    },
    step: {
      type: Number,
      required: true,
    },
    value: {
      type: Number,
      required: true,
    },
  },
};
</script>

<style scoped></style>