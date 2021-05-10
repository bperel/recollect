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
      :opacity="overlayOpacity"
      :zoom="parameters.zoom.value"
      :padding-x="parameters.paddingX.value"
      :padding-y="parameters.paddingY.value"
      :calibration-points="getCalibrationPointsByType('input')"
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
      <ParameterSlider
        v-for="({ min, max, step, value }, parameterName) in parameters"
        :key="parameterName"
        :name="parameterName"
        :min="min"
        :max="max"
        :step="step"
        :value="value"
        :scores="scoresPerParameter[parameterName]"
        @change="setParameterValue(parameterName, $event)"
        @auto="superimposeImages(parameterName)"
      />
      Overlay opacity :
      <input
        :value="overlayOpacity"
        type="range"
        min="0"
        max="1"
        step="0.1"
        @input="overlayOpacity = parseFloat($event.target.value)"
      />
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
import ParameterSlider from "@/components/ParameterSlider";

const parameters = {
  zoom: { default: 1, min: 0.1, step: 0.1, max: 3, value: 1 },
  paddingX: { default: 0, min: -250, step: 1, max: 250, value: 0 },
  paddingY: { default: 0, min: -250, step: 1, max: 250, value: 0 },
};

export default {
  name: "Calibrate",

  components: {
    ParameterSlider,
    InputImage,
    MapillaryCalibration,
  },

  mixins: [calibrationPointMixin],

  data: () => ({
    calibrationPoints: [
      {
        reference: {
          latLon: { lat: 55.60859144592081, lon: 12.995164231506969 },
          pixelPoint: [305, 200],
        },
        input: { pixelPoint: [339, 330] },
      },
      {
        input: { pixelPoint: [650, 322] },
        reference: {
          latLon: { lat: 55.60838957030178, lon: 12.995690351491728 },
          pixelPoint: [556, 186],
        },
      },
    ],
    parameters,
    overlayOpacity: 0.7,
    scores: {},
  }),

  computed: {
    distanceBetweenCalibrationPoints() {
      return this.calculateDistanceDiffBetweenInputAndReference({});
    },

    calibrationPointsWithBothTypes() {
      return this.calibrationPoints.filter(
        (calibrationPoint) => !!calibrationPoint.input && !!calibrationPoint.reference
      );
    },

    currentValues() {
      return {
        zoom: this.parameters.zoom.value,
        paddingX: this.parameters.paddingX.value,
        paddingY: this.parameters.paddingY.value,
      };
    },

    scoresPerParameter() {
      const vm = this;
      return Object.keys(this.parameters).reduce(
        (acc, parameterName) => ({
          ...acc,
          [parameterName]: Object.keys(this.scores)
            .filter((scoreParameters) => {
              scoreParameters = JSON.parse(scoreParameters);
              return Object.keys(scoreParameters).some(
                (scoreParameterName) =>
                  scoreParameterName !== parameterName &&
                  scoreParameters[scoreParameterName] === vm.parameters[scoreParameterName].value
              );
            })
            .reduce(
              (acc, scoreParameters) => ({
                ...acc,
                [JSON.parse(scoreParameters)[parameterName]]: vm.scores[scoreParameters],
              }),
              {}
            ),
        }),
        {}
      );
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

    setParameterValue(name, value) {
      Vue.set(this.parameters, name, { ...this.parameters[name], value });
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
      // Distance formula : sqrt((X1ref - Z * X1input)² + (Y1ref - Z * Y1input)²) where Z is the zoom
      // with 2 points: sqrt(((a) - (x*(b)))^2 + ((c) - (x*(d)))^2) + sqrt(((f) - (x*(g)))^2 + ((h) - (x*(j)))^2)
      // Whatever the number of points, the formula will always have a minimum, so we can simply approximate the minimum value
      // by running the formula against different values of Z until we consider that we're close enough
      // Derivative : (−2 * Y1input * (Y1ref − Y1input * Z) −2 * X1input * (X1ref − X1input * Z)) / (2 * sqrt((Y1ref − Y1input * Z)² + (X1ref − X1input * Z)²))
      // Zero found at: (Y1ref * X1input + X1ref * X1input)/(X1input² + X1input²)
      const { calibrationPointsWithBothTypes } = this;
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

    calculateDistanceDiffBetweenInputAndReference(parameters) {
      parameters = { ...this.currentValues, ...parameters };

      return this.addScore(
        parameters,
        Math.abs(
          this.getDistanceBetweenCalibrationPoints("input", parameters) -
            this.getDistanceBetweenCalibrationPoints("reference")
        )
      );
    },

    addScore(parameters, score) {
      Vue.set(this.scores, JSON.stringify({ ...this.currentValues, ...parameters }), score);
      return score;
    },

    getScore(parameters) {
      return this.scores[JSON.stringify({ ...this.currentValues, ...parameters })];
    },

    superimposeImages(parameter) {
      let value;

      switch (parameter) {
        case "paddingX":
        case "paddingY":
          const axis = parameter === "paddingX" ? 0 : 1;
          const points = {
            input: this.getCalibratedInputPoints(this.currentValues),
            reference: this.calibrationPointsWithBothTypes.map(
              ({ reference: referencePoint }) => referencePoint
            ),
          };
          let averagePosition = {};
          for (const source of Object.keys(points)) {
            averagePosition[source] =
              points[source].reduce((acc, { pixelPoint }) => acc + pixelPoint[axis], 0) /
              points[source].length;
          }
          value = this.currentValues[parameter] + averagePosition.reference - averagePosition.input;
          points.input = this.getCalibratedInputPoints({
            ...this.currentValues,
            [parameter]: value,
          });
          this.addScore(
            { [parameter]: value },
            points.input.reduce(
              (acc, { pixelPoint }, index) =>
                acc + Math.abs(pixelPoint[axis] - points.reference[index].pixelPoint[axis]),
              0
            )
          );
          break;
        case "zoom":
          let minimumValue = this.parameters[parameter].min;
          let maximumValue = this.parameters[parameter].max;
          for (const extremeValue of [minimumValue, maximumValue]) {
            this.calculateDistanceDiffBetweenInputAndReference({
              [parameter]: extremeValue,
            });
          }

          for (let i = 0; i < 10; i++) {
            value = (minimumValue + maximumValue) / 2;
            let score = this.calculateDistanceDiffBetweenInputAndReference({
              [parameter]: value,
            });
            console.debug(`${parameter} = ${value}, score=${score}`);
            if (
              this.getScore({ [parameter]: minimumValue }) < score &&
              score < this.getScore({ [parameter]: maximumValue })
            ) {
              maximumValue = value;
            } else {
              let intermediateValue1 = minimumValue + (maximumValue - minimumValue) / 4;
              let intermediateValue2 = minimumValue + (3 * (maximumValue - minimumValue)) / 4;
              for (const intermediateValue of [intermediateValue1, intermediateValue2]) {
                score = this.calculateDistanceDiffBetweenInputAndReference({
                  [parameter]: intermediateValue,
                });
                console.debug(` intermediate ${parameter} = ${intermediateValue}, score=${score}`);
              }
              if (
                this.getScore({ [parameter]: intermediateValue1 }) <
                this.getScore({ [parameter]: intermediateValue2 })
              ) {
                minimumValue = intermediateValue1;
                maximumValue = value;
              } else {
                minimumValue = value;
                maximumValue = intermediateValue2;
              }
              console.debug(`New intervals: ${minimumValue},${maximumValue}`);
            }
          }
      }

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
</style>
