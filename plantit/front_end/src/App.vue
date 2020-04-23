<template>
    <div id="app" class="m-0 p-0">
        <b-container fluid class="m-0 p-0">
            <app-navigation v-if="$route.path != '/'"></app-navigation>

            <router-view class="m-0 p-0"></router-view>
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
