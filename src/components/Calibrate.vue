<template>
  <div class="viewer-container">
    <MapillaryCalibration @addCalibrationPoint="addCalibrationPoint('reference', $event)" />
    <span
      v-for="(calibrationPoint, index) in getCalibrationPointsByType('reference')"
      :key="`calibration-point-${index}-reference`"
      class="calibration-point"
      :style="getCalibrationPointMargins(calibrationPoint.reference)"
    >
      {{ index + 1 }}
    </span>
    <InputImage
      :css-classes="{ viewer: true, top: true, left: true, overlay: true }"
      :calibration-points="calibratedInputPoints"
    />
    <InputImage
      interactive
      :css-classes="{ viewer: true, top: true, right: true }"
      :calibration-points="getCalibrationPointsByType('input')"
      @addCalibrationPoint="addCalibrationPoint('input', $event)"
    />
    <div
      id="depth1"
      class="viewer bottom left"
      style="background-image: url('/images/depth/stockholm2.png')"
    >
      <div
        v-for="({ min, max, step }, parameterName) in parameters"
        :key="parameterName"
        class="d-flex parameter"
      >
        {{ parameterName }}:
        <b-form-input
          :value="parameters[parameterName].value"
          class="mx-3"
          type="range"
          :min="min"
          :max="max"
          :step="step"
          @input="parameters[parameterName].value = parseInt($event)"
        />
        <b-button size="sm" @click="superimposeImages(parameterName)">
          <b-icon-lightning-fill />
        </b-button>
      </div>
    </div>
    <div
      id="depth2"
      class="viewer bottom right"
      style="background-image: url('/images/depth/stockholm1.png')"
    ></div>
  </div>
</template>

<script>
import MapillaryCalibration from "@/components/calibrations/MapillaryCalibration";
import interact from "interactjs";
import Vue from "vue";
import InputImage from "@/components/InputImage";
import calibrationPointMixin from "@/mixins/calibrationPointMixin";
import { BIconLightningFill } from "bootstrap-vue";

const parameters = {
  zoom: { default: 1, min: 0.1, step: 0.1, max: 3, value: 1 },
  paddingX: { default: 0, min: 0, step: 1, max: 500, value: 0 },
  paddingY: { default: 0, min: 0, step: 1, max: 500, value: 0 },
};

export default {
  name: "Calibrate",

  components: {
    BIconLightningFill,
    InputImage,
    MapillaryCalibration,
  },

  mixins: [calibrationPointMixin],

  data: () => ({
    calibrationPoints: [
      {
        reference: {
          latLon: { lat: 55.60791959363544, lon: 12.995770352486737 },
          pixelPoint: [584, 228],
        },
        input: { pixelPoint: [331, 255] },
      },
      {
        reference: {
          latLon: { lat: 55.60799819589218, lon: 12.9957852994826 },
          pixelPoint: [667, 168],
        },
        input: { pixelPoint: [513, 146] },
      },
    ],
    parameters,
  }),

  computed: {
    distanceBetweenCalibrationPoints() {
      console.log("zoom=" + this.parameters.zoom.value);
      return this.getDistanceDiffBetweenInputAndReference({
        zoom: this.parameters.zoom.value,
        paddingX: this.parameters.paddingX.value,
        paddingY: this.parameters.paddingY.value,
      });
    },

    calibratedInputPoints() {
      return this.getCalibratedInputPoints({
        zoom: this.parameters.zoom.value,
        paddingX: this.parameters.paddingX.value,
        paddingY: this.parameters.paddingY.value,
      }).map((inputPoint) => ({ input: inputPoint }));
    },

    calibrationPointsWithBothTypes() {
      const value = this.calibrationPoints.filter(
        (calibrationPoint) => !!calibrationPoint.input && !!calibrationPoint.reference
      );
      console.log(value);
      return value;
    },
  },

  mounted() {
    const vm = this;
    interact(".input-image.interactive").draggable({
      listeners: {
        move({ delta }) {
          vm.inputImagePan = [vm.inputImagePan[0] + delta.x, vm.inputImagePan[1] + delta.y];
        },
      },
    });
  },

  methods: {
    addCalibrationPoint(type, data) {
      for (let index in this.calibrationPoints) {
        if (!this.calibrationPoints[index][type]) {
          Vue.set(this.calibrationPoints[index], type, data);
          return;
        }
      }
      Vue.set(this.calibrationPoints, this.calibrationPoints.length, {
        [type]: data,
      });
    },

    getCalibrationPointsByType(type) {
      return this.calibrationPoints.filter((calibrationPoint) => !!calibrationPoint[type]);
    },

    getCalibratedInputPoints(parameters) {
      const { zoom, paddingX, paddingY } = parameters;

      return this.getCalibrationPointsByType("input").map(({ input: inputPoint }) => ({
        pixelPoint: [
          paddingX + zoom * inputPoint.pixelPoint[0],
          paddingY + zoom * inputPoint.pixelPoint[1],
        ],
      }));
    },

    getDistanceBetweenCalibrationPoints(
      calibrationPointType,
      parameters = { zoom: 1, paddingX: 0, paddingY: 0 }
    ) {
      console.log(parameters);

      const calibrationPointsWithBothTypes = this.calibrationPointsWithBothTypes;
      const points =
        calibrationPointType === "input"
          ? this.getCalibratedInputPoints(parameters)
          : calibrationPointsWithBothTypes.map(({ reference: referencePoint }) => referencePoint);

      return calibrationPointsWithBothTypes
        .map((calibrationPoint1, index1) =>
          calibrationPointsWithBothTypes
            .filter((calibrationPoint2, index2) => index2 < index1)
            .map((calibrationPoint2, index2) =>
              Math.sqrt(
                [0, 1].reduce(
                  (acc, axis) =>
                    acc +
                    Math.pow(points[index1].pixelPoint[axis] - points[index2].pixelPoint[axis], 2),
                  0
                )
              )
            )
            .reduce((acc, singleDistance) => acc + singleDistance, 0)
        )
        .reduce((acc, singleDistance) => acc + singleDistance, 0);
    },

    getDistanceDiffBetweenInputAndReference(parameters) {
      console.log(parameters);
      return Math.abs(
        this.getDistanceBetweenCalibrationPoints("input", parameters) -
          this.getDistanceBetweenCalibrationPoints("reference")
      );
    },

    superimposeImages(parameter) {
      // Distance formula : sqrt((X1ref - Z * X1input)² + (Y1ref - Z * Y1input)²) where Z is the zoom
      // with 2 points: sqrt(((a) - (x*(b)))^2 + ((c) - (x*(d)))^2) + sqrt(((f) - (x*(g)))^2 + ((h) - (x*(j)))^2)
      // Whatever the number of points, the formula will always have a minimum, so we can simply approximate the minimum value
      // by running the formula against different values of Z until we consider that we're close enough
      // Derivative : (−2 * Y1input * (Y1ref − Y1input * Z) −2 * X1input * (X1ref − X1input * Z)) / (2 * sqrt((Y1ref − Y1input * Z)² + (X1ref − X1input * Z)²))
      // Zero found at: (Y1ref * X1input + X1ref * X1input)/(X1input² + X1input²)

      const currentValues = {
        zoom: this.parameters.zoom.value,
        paddingX: this.parameters.paddingX.value,
        paddingY: this.parameters.paddingY.value,
      };

      let minimumValue = this.parameters[parameter].min;
      let maximumValue = this.parameters[parameter].max;
      let distances = {
        [minimumValue]: this.getDistanceDiffBetweenInputAndReference({
          ...currentValues,
          [parameter]: minimumValue,
        }),
        [maximumValue]: this.getDistanceDiffBetweenInputAndReference({
          ...currentValues,
          [parameter]: maximumValue,
        }),
      };

      let value;
      for (let i = 0; i < 10; i++) {
        value = (minimumValue + maximumValue) / 2;
        console.debug(`${parameter} = ${value}`);
        const distance = this.getDistanceDiffBetweenInputAndReference({
          ...currentValues,
          [parameter]: value,
        });
        console.debug(`distance=${distance}`);
        distances[value] = distance;
        if (distances[minimumValue] < distance && distance < distances[maximumValue]) {
          maximumValue = value;
        } else {
          console.debug(
            `distances[${minimumValue}]=${distances[minimumValue]}, distance=${distance}, distances[${maximumValue}]=${distances[maximumValue]}`
          );
          let intermediateValue1 = minimumValue + (maximumValue - minimumValue) / 4;
          let intermediateValue2 = minimumValue + (3 * (maximumValue - minimumValue)) / 4;
          for (const intermediateValue of [intermediateValue1, intermediateValue2]) {
            console.debug(` intermediate ${parameter} = ${intermediateValue}`);
            distances[intermediateValue] = this.getDistanceDiffBetweenInputAndReference({
              ...currentValues,
              [parameter]: intermediateValue,
            });
            console.debug(` intermediate ${parameter} distance=${distances[intermediateValue]}`);
          }
          if (distances[intermediateValue1] < distances[intermediateValue2]) {
            minimumValue = intermediateValue1;
            maximumValue = value;
          } else {
            minimumValue = value;
            maximumValue = intermediateValue2;
          }
        }
      }

      console.log(distances);
      this.parameters[parameter].value = value;
    },
  },
};
</script>

<style lang="scss">
canvas {
  left: 0;
}

body {
  margin: 0;
  padding: 0;
}

html,
body {
  width: 100%;
  height: 100%;
}

.viewer-container {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 100%;
}

.viewer {
  position: absolute;
  height: 100%;
  z-index: 0;
}

.left,
.right {
  width: 50%;
}

.left {
  left: 0;
}

.right {
  right: 0;
}

.top,
.bottom {
  height: 50%;
}

.top {
  top: 0;
}

.bottom {
  bottom: 0;
  background-repeat: no-repeat;
  background-size: cover;
}

.calibration-point {
  position: absolute;
  background: white;
  padding: 5px;
  top: 0;
  left: 0;
  pointer-events: none;
}

.input-image {
  background-color: black;
  background-size: cover;
  background-position: top;
  background-repeat: no-repeat;

  &.overlay {
    pointer-events: none;
    opacity: 0.2;
  }
}

.parameter {
  color: white;
}
</style>
