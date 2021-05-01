<template>
  <div
    :class="{ 'input-image': true, interactive, ...cssClasses }"
    :style="{
      backgroundImage: 'url(\'' + inputImage + '\')',
      backgroundPosition: inputImagePanInPx,
    }"
    @dragend.prevent="() => {}"
    @click.exact="
      $emit('addCalibrationPoint', {
        pixelPoint: [$event.layerX, $event.layerY],
      })
    "
  >
    <template>
      <span
        v-for="(calibrationPoint, index) in calibrationPoints"
        :key="`calibration-point-${index}-input`"
        class="calibration-point"
        :style="getCalibrationPointMargins(calibrationPoint.input)"
      >
        {{ index + 1 }}
      </span></template
    >
  </div>
</template>

<script>
import calibrationPointMixin from "@/mixins/calibrationPointMixin";

export default {
  name: "InputImage",

  emits: ["addCalibrationPoint"],

  mixins: [calibrationPointMixin],

  props: {
    interactive: {
      type: Boolean,
      default: false,
    },
    cssClasses: {
      type: Object,
      default: () => ({}),
    },
    calibrationPoints: {
      type: Array,
      required: true,
    },
  },

  data: () => ({
    inputImage: "/images/stockholm1.jpg",
    inputImagePan: [0, 0],
  }),

  computed: {
    inputImagePanInPx() {
      return this.inputImagePan.map((value) => value + "px").join(" ");
    },
  },
};
</script>

<style scoped></style>
