<template>
    <b-container fluid class="m-0 p-0">
        <b-row no-gutters class="m-0 p-0">
            <b-col class="m-0 p-0">
                <brand></brand>
                <about></about>
                <!--<sponsors></sponsors>-->
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
// @ is an alias to /src
import brand from '@/components/splash/brand.vue';
import about from '@/components/splash/about.vue';
// import sponsors from '../components/splash/sponsors';

export default {
    name: 'splash',
    components: {
        brand,
        about,
        // sponsors,
    },
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'

html
    scroll-behavior: smooth
</style>
