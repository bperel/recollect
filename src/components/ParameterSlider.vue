<template>
  <div class="d-flex row parameter">
    <div class="name col-3 text-left">{{ name }}:</div>
    <div class="col-7">
      <div class="score-wrapper">
        <div
          v-for="(score, key) in scores"
          :key="`score-${score}`"
          class="score"
          :style="{ marginLeft: `${keyOffsets[key]}%`, backgroundColor: `#${colors[key]}` }"
        ></div>
      </div>
      <b-form-input
        :value="value"
        class="mx-3"
        type="range"
        :min="min"
        :max="max"
        :step="step"
        @input="$emit('change', parseFloat($event))"
      />
    </div>
    <div class="col-2">
      <b-button size="sm" @click="$emit('auto', name)">
        <b-icon-lightning-fill />
      </b-button>
    </div>
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
    scores: {
      type: Object,
      default: () => [],
    },
  },

  computed: {
    minScore() {
      return Math.min(...Object.values(this.scores));
    },
    maxScore() {
      return Math.max(...Object.values(this.scores));
    },
    keyOffsets() {
      const vm = this;
      return Object.keys(this.scores).reduce(
        (acc, key) => ({
          ...acc,
          [key]: (100 * (key - vm.min)) / (vm.max - vm.min),
        }),
        {}
      );
    },

    colors() {
      const vm = this;
      return Object.keys(this.scores).reduce(
        (acc, key) => ({
          ...acc,
          [key]: vm.interpolateColor(
            "00ff00",
            "ff0000",
            (vm.scores[key] - vm.minScore) / (vm.maxScore - vm.minScore)
          ),
        }),
        {}
      );
    },
  },

  mounted() {
    this.$emit("change", this.value);
  },

  methods: {
    interpolateColor(c0, c1, f) {
      c0 = c0.match(/.{1,2}/g).map((oct) => parseInt(oct, 16) * (1 - f));
      c1 = c1.match(/.{1,2}/g).map((oct) => parseInt(oct, 16) * f);
      return [0, 1, 2]
        .map((i) => Math.min(Math.round(c0[i] + c1[i]), 255))
        .reduce((a, v) => (a << 8) + v, 0)
        .toString(16)
        .padStart(6, "0");
    },
  },
};
</script>

<style scoped lang="scss">
.parameter {
  display: flex;
  justify-content: space-between;
  color: white;
  .score-wrapper {
    position: absolute;
    pointer-events: none;
    width: calc(100% - 3rem + 2px);
    height: 100%;
    padding-left: 1.5rem;
    .score {
      position: absolute;
      background: red;
      width: 1px;
      height: 1.4rem;
    }
  }
}
</style>