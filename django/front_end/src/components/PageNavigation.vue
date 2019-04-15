<template>
    <b-nav>
        <b-navbar class="mx-auto">
            <slot name="page-nav"> </slot>
        </b-navbar>

        <hr id="sep" />

        <div class="button-nav">
            <slot name="buttons"> </slot>
        </div>
    </b-nav>
</template>

<script>
export default {
    name: 'PageNavigation'
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"

.navbar
  padding-left: 50px // To align with app nav

.nav-link
  padding-top: 0
  padding-bottom: 0
  margin-top: -25px // Push closer to app nav
  color: $color-text-green-on-white

#sep
  width: 100%
  color: black
  height: 1px
  background-color: black

.button-nav
  padding-left: 35px // To align with App nav
  width: 100%
  text-align: center

button
  background-color: $color-button
  border-radius: 20px
  min-height: 50px
  border-style: none
  font-weight: 800
  margin: 5px

  &:hover
    background-color: $color-highlight
</style>
