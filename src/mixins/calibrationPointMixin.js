export default {
  methods: {
    getCalibrationPointMargins(inputCalibrationPoint, zoom = 1) {
      const textWidth = 15;
      const margins = inputCalibrationPoint.pixelPoint.map(
        (position) => (position - textWidth / 2) * zoom + "px"
      );
      return { marginLeft: margins[0], marginTop: margins[1] };
    },
  },
};
