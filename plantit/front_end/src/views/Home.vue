<template>
    <b-container fluid>
        <b-row no-gutters>
            <b-col>
                <HomeSplash></HomeSplash>
                <HomeAbout></HomeAbout>
                <HomeSponsors></HomeSponsors>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
// @ is an alias to /src
import HomeSplash from '@/components/home/HomeSplash.vue';
import HomeAbout from '@/components/home/HomeAbout.vue';
import HomeSponsors from '../components/home/HomeSponsors';

export default {
    name: 'home',
    components: {
        HomeSplash,
        HomeAbout,
        HomeSponsors
    }
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'

html
    scroll-behavior: smooth

</style>
