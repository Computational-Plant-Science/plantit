<template>
    <div id="app">
        <b-container fluid>
            <app-navigation v-if="$route.path != '/'"></app-navigation>

            <router-view></router-view>
        </b-container>
    </div>
</template>

<script>
import AppNavigation from '@/components/AppNavigation';

export default {
    name: 'App',
    components: {
        AppNavigation
    },
    data() {
        return {
            //
        };
    }
};
</script>

<style lang="sass">
@import "./scss/main.sass"
</style>
