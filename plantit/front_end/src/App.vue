<template>
    <div
        id="app"
        :class="darkMode ? 'theme-dark' : 'theme-light' + ' m-0'"
        style="width: 100vw; min-height: 100vh;"
    >
        <b-container
            fluid
            class="m-0 p-0"
            style="min-height: 98vh; background-color: transparent;"
        >
            <Navigation v-if="$route.path !== '/'"></Navigation>
            <router-view
                :class="darkMode ? 'theme-dark' : 'theme-light'"
            ></router-view>
        </b-container>
    </div>
</template>

<script>
import Navigation from '@/components/navigation';
import { mapGetters } from 'vuex';

export default {
    name: 'App',
    components: {
        Navigation
    },
    computed: mapGetters([
        'darkMode',
    ]),
    data() {
        return {};
    }
};
</script>

<style scoped lang="sass">
@import 'scss/main.sass'
@import 'scss/_colors.sass'
@import url('https://fonts.googleapis.com/css2?family=Cutive+Mono&display=swap');
.dark
    background-color: $dark
.light
    background-color: white
</style>
