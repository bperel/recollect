<template>
  <div
    :class="{ 'input-image': true, interactive, ...cssClasses }"
    :style="{
      backgroundImage: 'url(\'' + inputImage + '\')',
      backgroundPosition: inputImagePanInPx,
      marginLeft: `${paddingX}px`,
      marginTop: `${paddingY}px`,
      width: `${50 * zoom}%`,
      opacity,
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
        :style="getCalibrationPointMargins(calibrationPoint.input, zoom)"
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
    opacity: {
      type: Number,
      default: 1,
    },
    zoom: {
      type: Number,
      default: 1,
    },
    paddingX: {
      type: Number,
      default: 0,
    },
    paddingY: {
      type: Number,
      default: 0,
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
