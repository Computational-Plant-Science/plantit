<template>
    <div>
        <b-card
            class="rounded-0 text-center"
            bg-variant="dark"
            border-variant="dark"
            text-variant="white"
            header-bg-variant="dark"
            header-border-variant="dark"
        >
            <template slot="header" style="border: none">
                <br />

                <br />
                <b-row align-v="center" class="justify-content-md-center">
                    <b-col>
                        <b-img
                    style="max-width: 8rem;transform: translate(0px, 20px);"
                    :src="require('../../assets/logo.png')"
                    center
                    class="m-0 p-0"
                ></b-img>
                        <h1 class="text-white mt-5">
                            plant science workflow automation in the browser
                        </h1>
                    </b-col>
                </b-row>
            </template>
            <b-container>
                <br />
                <br />
                <b-row align-content="center" align-h="center">
                    <b-col align-h="center">
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left rounded-0 overflow-hidden"
                            bg-variant="dark"
                            no-body
                            text-variant="success"
                            :img-src="
                                require('../../assets/frontpage/icons/algorithm.png')
                            "
                            img-width="100px"
                            img-height="90px"
                            img-left
                            style="border: none;"
                        >
                            <b-card-text class="ml-4">
                                <h4 class="text-white">
                                    access or upload data
                                </h4>
                                upload, store, and publish datasets with
                                <b-link
                                    class="text-white"
                                    href="https://www.cyverse.org/"
                                    >CyVerse</b-link
                                ><!--, or plug in cloud stores like
                            <b-link
                                class="text-white"
                                href="https://aws.amazon.com/s3/"
                                >Amazon S3</b-link
                            >-->
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col>
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left rounded-0 overflow-hidden"
                            bg-variant="dark"
                            text-variant="success"
                            no-body
                            :img-src="
                                require('../../assets/frontpage/icons/code.png')
                            "
                            img-width="100px"
                            img-height="90px"
                            img-left
                            style="border: none;"
                        >
                            <b-card-text class="ml-4">
                                <h4 class="text-white">
                                    find or share software
                                </h4>
                                run code from
                                <b-link
                                    class="text-white"
                                    href="https://www.github.com/"
                                    >Github</b-link
                                >
                                or publish your own to the community &mdash; if
                                it can run in
                                <b-link
                                    class="text-white"
                                    href="https://www.docker.com/"
                                    >Docker</b-link
                                >
                                or
                                <b-link
                                    class="text-white"
                                    href="https://sylabs.io/docs/"
                                    >Singularity</b-link
                                >, it will run on PlantIT
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
                <b-row>
                    <b-col md="auto">
                        <b-card
                            sub-title-text-variant="success"
                            class="text-left text-white rounded-0 overflow-hidden"
                            no-body
                            bg-variant="dark"
                            text-variant="success"
                            :img-src="
                                require('../../assets/frontpage/icons/UI.png')
                            "
                            img-width="100px"
                            img-height="90px"
                            img-left
                            style="border: none;"
                        >
                            <b-card-text class="ml-4">
                                <h4 class="text-white">
                                    workflows on the web
                                </h4>
                                onfigure parameters, deploy to a cluster, and
                                get notified when results are ready &mdash; all
                                from the browser, no programming required
                            </b-card-text>
                        </b-card>
                    </b-col>
                </b-row>
                <br />
                <br />
            </b-container>
        </b-card>
        <b-card
            class="rounded-0 text-center"
            bg-variant="white"
            border-variant="white"
            text-variant="dark"
            header-bg-variant="dark"
            header-border-variant="dark"
        >
            <br />
            <br />
            <br />
            <div class="p-0 m-0 background-white text-white">
                <b-img
                    style="max-width: 8rem;transform: translate(0px, 20px);"
                    :src="require('../../assets/logo.png')"
                    center
                    class="m-0 p-0"
                ></b-img>
            </div>
            <div class="p-1 pt-2 background-dark">
                <h1 class="text-center text-white">
                    <b class="text-dark">about plantit</b>
                </h1>
            </div>
            <br />
            <br />
            <b-container>
                <b-row align-content="center">
                    <b-col class="text-left">
                        <VueMarkdown :source="source"> </VueMarkdown>
                    </b-col>
                </b-row>
            </b-container>
            <br />
            <br />
            <br />
        </b-card>
    </div>
</template>

<script>
import VueMarkdown from 'vue-markdown';
import about from '@/assets/markdown/about.md';

export default {
    name: 'home-about',
    components: {
        VueMarkdown
    },
    data: function() {
        return {
            source: about
        };
    }
};
</script>

<style scoped lang="sass">
@import '../../scss/_colors.sass'

h1
    color: $color-highlight
</style>
