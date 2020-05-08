<template>
    <b-container fluid>
        <b-row no-gutters>
            <b-col>
                <HomeAbout></HomeAbout>
                <HomeResearchers></HomeResearchers>
                <HomeDevelopers></HomeDevelopers>
                <HomeSponsors></HomeSponsors>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
// @ is an alias to /src
import HomeAbout from '@/components/home/HomeAbout.vue';
import HomeDevelopers from '@/components/home/HomeDevelopers.vue';
import HomeResearchers from '@/components/home/HomeResearchers.vue';
import HomeSponsors from "../components/home/HomeSponsors";

export default {
    name: 'home',
    components: {
        HomeSponsors,
        HomeAbout,
        HomeDevelopers,
        HomeResearchers
    }
};
</script>

<style>
html {
    scroll-behavior: smooth;
}
</style>
