<template>
    <div>
        <br />
        <br />
        <b-container>
            <b-row>
                <b-col class="text-center"
                    ><b-img
                        style="max-width: 5rem; transform: translate(0px, 20px)"
                        :src="require('../assets/logo.png')"
                        center
                        class="m-0 p-0 mb-1"
                    ></b-img>
                    <h1
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        style="text-decoration: underline"
                    >
                        plant<small
                            class="mb-3 text-success"
                            style="
                                text-decoration: underline;
                                text-shadow: 1px 0 0 #000, 0 -1px 0 #000,
                                    0 1px 0 #000, -1px 0 0 #000;
                            "
                            >IT</small
                        ><small class="ml-1">beta</small>
                    </h1>
                </b-col>
            </b-row>
            <br />
            <b-row
                ><b-col class="text-center"
                    ><b>Thanks for your interest in PlantIT!</b><br />Feedback
                    is crucial and much appreciated. Here are a couple ways to
                    get started. <br /><br />
                    <h5>1</h5>
                    If you'd prefer to read about the platform first, you can
                    download the
                    <b-link
                        @click="downloadTutorials"
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-file fa-1x fa-fw"></i>
                            Tutorials</span
                        ></b-link
                    >
                    or check out the
                    <b-link
                        href="https://plantit.readthedocs.io/en/latest"
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-book fa-1x fa-fw"></i> Developer
                            Docs</span
                        ></b-link
                    >.<br /><br />
                    <h5>2</h5>
                    To jump straight in, go to the
                    <b-link
                        :to="{
                            name: 'workflow',
                            params: {
                                owner: 'Computational-Plant-Science',
                                name: 'plantit-example-hello-world',
                            },
                        }"
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-stream fa-1x fa-fw"></i> Example:
                            Hello World</span
                        ></b-link
                    >
                    workflow, then click the
                    <b-link
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        @click="toggleHints"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-question fa-1x fa-fw"></i>
                            Hints</span
                        ></b-link
                    >
                    button in the top-right dropdown menu.<br /><br />
                    <h5>3</h5>
                    Ready to share your thoughts? Feel free to use the built-in
                    <b-link
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        @click="showFeedbackModal"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-comment-alt fa-1x fa-fw"></i>
                            Feedback System</span
                        ></b-link
                    >, download the
                    <b-link
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        @click="downloadFeedbackForm"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-file fa-1x fa-fw"></i> Feedback
                            Form</span
                        ></b-link
                    >, or
                    <b-link
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        href="mailto:wbonelli@uga.edu"
                        ><span
                            :class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><i class="fas fa-envelope fa-1x fa-fw"></i>
                            Contact</span
                        ></b-link
                    >
                    us directly.</b-col
                ></b-row
            >
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'beta',
    data: function () {
        return {
            downloading: false,
            togglingHints: false,
        };
    },
    methods: {
        async toggleHints() {
            this.togglingHints = true;
            await this.$store.dispatch('user/toggleHints');
            this.togglingHints = false;
        },
        showFeedbackModal() {
            this.$bvModal.show('feedback');
        },
        async downloadTutorials() {
            this.downloading = true;
            await axios
                .get(
                    `/apis/v1/feedback/tutorials/`,

                    {
                        responseType: 'blob',
                    }
                )
                .then((response) => {
                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'tutorials.pdf');
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    alert(`Failed to download tutorials`);
                    throw error;
                });
        },
        async downloadFeedbackForm() {
            this.downloading = true;
            await axios
                .get(
                    `/apis/v1/feedback/feedback/`,

                    {
                        responseType: 'blob',
                    }
                )
                .then((response) => {
                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', 'feedback.pdf');
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    alert(`Failed to download feedback form`);
                    throw error;
                });
        },
    },
    computed: {
        ...mapGetters('user', ['profile']),
    },
};
</script>

<style scoped></style>
