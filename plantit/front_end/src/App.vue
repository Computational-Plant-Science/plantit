<template>
    <div
        id="app"
        :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        style="width: 100vw; min-height: 100vh"
    >
        <b-container
            fluid
            class="m-0 p-0"
            style="background-color: transparent"
        >
            <navigation v-if="!isRootPath"></navigation>
            <router-view
                v-bind:class="{ lightlinks: profile.darkMode }"
            ></router-view>
            <br />
        </b-container>
    </div>
</template>

<script>
import navigation from '@/components/navigation';
import { mapGetters } from 'vuex';

export default {
    name: 'App',
    components: {
        navigation,
    },
    computed: {
        ...mapGetters('user', ['profile']),
        isRootPath() {
            return this.$route.path === '/';
        },
    },
};
</script>

<style scoped lang="sass">
@import 'scss/main.sass'
@import 'scss/_colors.sass'
@import url('https://fonts.googleapis.com/css2?family=Cutive+Mono&display=swap')
.dark
    background-color: $dark
.light
    background-color: white
</style>
