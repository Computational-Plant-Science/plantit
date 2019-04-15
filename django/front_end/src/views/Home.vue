<template>
    <div class="home">
        <HomeAbout></HomeAbout>
        <HomeResearchers></HomeResearchers>
        <HomeDevelopers></HomeDevelopers>
    </div>
</template>

<script>
// @ is an alias to /src
import HomeAbout from '@/components/home/HomeAbout.vue';
import HomeResearchers from '@/components/home/HomeResearchers.vue';
import HomeDevelopers from '@/components/home/HomeDevelopers.vue';

export default {
    name: 'home',
    components: {
        HomeAbout,
        HomeResearchers,
        HomeDevelopers
    }
};
</script>
