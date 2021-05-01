<template>
  <div id="app">
    <Calibrate />
  </div>
</template>

<script>
import Calibrate from "./components/Calibrate.vue";

export default {
  name: "App",
  components: {
    Calibrate,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
