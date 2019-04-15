<template>
  <div id="app" class="content-column">
    <b-table striped hover :items="items"></b-table>
  </div>
</template>

<script>
export default {
  name: "app",
  props: ['items'],
  data() {
    return {
      items: []
    };
  },
  methods: {
  }
};
</script>

<style lang="scss">
</style>
