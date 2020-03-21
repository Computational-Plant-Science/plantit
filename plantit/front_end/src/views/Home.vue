<template>
    <b-container fluid>
        <b-row no-gutters="true">
            <b-col>
                <HomeAbout></HomeAbout>
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
import HomeSponsors from '@/components/home/HomeSponsors.vue';

export default {
    name: 'home',
    components: {
        HomeAbout,
        HomeDevelopers,
        HomeSponsors
    }
};
</script>

<style>
html {
    scroll-behavior: smooth;
}
</style>
