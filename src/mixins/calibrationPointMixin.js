export default {
  methods: {
    getCalibrationPointMargins(inputCalibrationPoint) {
      const textWidth = 15;
      const margins = inputCalibrationPoint.pixelPoint.map(
        (position) => position - textWidth / 2 + "px"
      );
      return { marginLeft: margins[0], marginTop: margins[1] };
    },
  },
};
