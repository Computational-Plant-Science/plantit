<template>
    <div id="home-about-researchers">
        <b-container fluid class="m-0 p-4">
            <b-row>
                <b-col>
                    <h1>RESEARCHERS</h1>
                    <h4>You focus on the data.</h4>
                    <h4>We take care of everything else.</h4>
                    <b-img
                        center
                        fluid
                        :src="require('@/assets/frontpage/icons/hex1.png')"
                        alt="Plant IT"
                    ></b-img>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
export default {
    name: 'HomeResearchers'
};
</script>

<style scoped lang="sass">
@import '../../scss/_colors.sass'

#home-about-researchers
  background-color: $color-box-background

h1
  color: $color-highlight
</style>
