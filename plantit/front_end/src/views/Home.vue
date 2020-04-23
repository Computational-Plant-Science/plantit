<template>
    <b-container fluid>
        <b-row no-gutters="true">
            <b-col>
                <HomeAbout></HomeAbout>
                <HomeDevelopers></HomeDevelopers>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
// @ is an alias to /src
import HomeAbout from '@/components/home/HomeAbout.vue';
import HomeDevelopers from '@/components/home/HomeDevelopers.vue';

export default {
    name: 'home',
    components: {
        HomeAbout,
        HomeDevelopers,
    }
};
</script>

<style>
html {
    scroll-behavior: smooth;
}
</style>
