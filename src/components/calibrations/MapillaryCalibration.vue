<template>
  <div class="viewer-container">
    <div id="mly" class="viewer top"></div>
  </div>
</template>

<script>
import * as Mapillary from "mapillary-js";

export default {
  name: "MapillaryCalibration",

  events: ["addCalibrationPoint", "removeCalibrationPoint"],

  data: () => {
    return {
      mly: null,
      mlyContainer: null,
      markerComponent: null,
      newMarkerId: 0,
    };
  },

  mounted() {
    const vm = this;
    const clientId = process.env.VUE_APP_MAPILLARY_CLIENT_ID;

    this.mly = new Mapillary.Viewer({
      apiClient: clientId,
      component: {
        imagePlane: { imageTiling: true },
        marker: {
          // Set visible bounding box size
          visibleBBoxSize: 80,
        },
      },
      container: "mly",
    });

    this.markerComponent = this.mly.getComponent("marker");
    this.mlyContainer = this.mly.getContainer();
    this.mly.moveToKey("JW1utOJP4g7gk06HtYgQSQ").catch((e) => {
      console.error(e);
    });

    let indicatorMarker = null;
    let indicatorMarkerId = "indicator-id";
    let dragging = false;
    const setIndicator = (latLon) => {
      indicatorMarker = new Mapillary.MarkerComponent.CircleMarker(indicatorMarkerId, latLon, {
        color: "#0f0",
      });

      vm.markerComponent.add([indicatorMarker]);
    };

    const removeIndicator = () => {
      if (!!indicatorMarker && vm.markerComponent.has(indicatorMarker.id)) {
        vm.markerComponent.remove([indicatorMarker.id]);
        indicatorMarker = null;
      }
    };

    const moveIndicator = (latLon) => {
      if (dragging) {
        return;
      }

      if (latLon == null) {
        removeIndicator();
      } else {
        setIndicator({ lat: latLon.lat, lon: latLon.lon });
      }
    };

    // let lastPos = null;
    const onViewerMouseEvent = ({ latLon }) => {
      // lastPos = event.pixelPoint;
      moveIndicator(latLon);
    };

    // Listen to viewer mouse events
    this.mly.on(Mapillary.Viewer.mouseup, onViewerMouseEvent);
    this.mly.on(Mapillary.Viewer.mouseover, onViewerMouseEvent);
    this.mly.on(Mapillary.Viewer.mousedown, onViewerMouseEvent);

    window.addEventListener("resize", this.resize);

    this.activateSideBySideMode();

    this.mly.on(Mapillary.Viewer.click, ({ latLon, pixelPoint }) => {
      if (!latLon) {
        return;
      }

      vm.markerComponent.getMarkerIdAt(pixelPoint).then((markerId) => {
        // Only create a new marker if no interactive markers are hovered
        if (markerId != null) {
          return;
        }

        const id = (vm.newMarkerId++).toString();
        vm.markerComponent.add([
          new Mapillary.MarkerComponent.SimpleMarker(id, latLon, {
            interactive: true,
          }),
        ]);
        vm.$emit("addCalibrationPoint", { latLon, pixelPoint });
      });
    });
  },

  methods: {
    resize() {
      this.mly.resize();
    },

    activateSideBySideMode() {
      this.mlyContainer.classList.add("left");

      this.mly.activateComponent("sequence");
      this.mly.activateComponent("direction");

      this.resize();
    },
  },
};
</script>

<style>
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
</style>
