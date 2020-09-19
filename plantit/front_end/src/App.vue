<template>
    <div id="app" class="m-0 p-0">
        <b-container fluid class="m-0 p-0">
            <Navigation v-if="$route.path != '/'"></Navigation>
            <router-view class="m-0 p-0"></router-view>
        </b-container>
    </div>
</template>

<script>
import Navigation from '@/components/navigation';

export default {
    name: 'App',
    components: {
        Navigation
    },
    data() {
        return {};
    },
};
</script>

<style lang="sass">
@import "./scss/main.sass"
</style>
