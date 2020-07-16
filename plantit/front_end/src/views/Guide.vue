<template>
    <div>
        <br />
        <br />
        <br />
        <div class="p-0 m-0 background-white text-white">
            <b-img
                style="max-width: 8rem;transform: translate(0px, 20px);"
                :src="require('../assets/logo.png')"
                center
                class="m-0 p-0"
            ></b-img>
        </div>
        <div class="p-1 pt-2 background-dark">
            <h2 class="text-center text-white">
                <b class="text-success">User Guide</b>
            </h2>
        </div>
        <div class="p-5 m-0" style="min-height: 100%">
            <b-container>
                <b-row align-content="center">
                    <b-col class="text-center">
                        This page is under construction.
                        <!--<VueMarkdown :source="source"> </VueMarkdown>-->
                    </b-col>
                </b-row>
            </b-container>
        </div>
    </div>
</template>

<script>
import VueMarkdown from 'vue-markdown';
import guide from '../docs/guide.md';

export default {
    name: 'Guide',
    components: {
        VueMarkdown
    },
    data() {
        return {
            source: guide
        };
    }
};
</script>

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'
.dark
    color: $dark
    padding: 0px
    margin: 0px

.background-dark
    background-color: $dark

.success
    color: $success

.selected
    background-color: $color-button
    color: $dark

a
    font-weight: 400
    color: $success !important
    text-decoration: underline
    text-decoration-color: $color-button
</style>
