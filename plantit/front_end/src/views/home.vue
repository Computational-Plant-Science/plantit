<template>
    <b-container fluid class="m-0 p-0">
        <b-row no-gutters>
            <b-col>
                <splash></splash>
                <about></about>
                <people></people>
              <sponsors></sponsors>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>
// @ is an alias to /src
import splash from '@/components/home/splash.vue';
import about from '@/components/home/about.vue';
import people from '@/components/home/people.vue';
import sponsors from '../components/home/sponsors';

export default {
    name: 'home',
    components: {
        splash,
        about,
        people,
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
