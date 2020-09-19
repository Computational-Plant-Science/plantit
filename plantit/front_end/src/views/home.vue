<template>
    <b-container fluid>
        <b-row no-gutters>
            <b-col>
                <splash></splash>
                <about></about>
                <sponsors></sponsors>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
// @ is an alias to /src
import splash from '@/components/home/splash.vue';
import about from '@/components/home/about.vue';
import sponsors from '../components/home/sponsors';

export default {
    name: 'home',
    components: {
        splash,
        about,
        sponsors
    }
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'

html
    scroll-behavior: smooth
</style>
