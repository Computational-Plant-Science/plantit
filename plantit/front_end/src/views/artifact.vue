<template>
    <div
        class="w-100 h-100 p-2"
        :style="
            profile.darkMode
                ? 'background-color: #616163'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
            <div v-if="dataNotFound">
                <b-row align-content="center">
                    <b-col>
                        <p
                            :class="
                                profile.darkMode
                                    ? 'text-center text-white'
                                    : 'text-center text-dark'
                            "
                        >
                            <i
                                class="fas fa-exclamation-circle fa-3x fa-fw"
                            ></i>
                            <br />
                            <br />
                            This file does not exist.
                        </p>
                    </b-col>
                </b-row>
            </div>
            <div v-else>
                <b-row>
                    <b-col>
                        <b-row align-h="center" v-if="dataLoading">
                            <b-spinner
                                type="grow"
                                label="Loading..."
                                variant="secondary"
                            ></b-spinner> </b-row
                        ><b-row v-else
                            ><b-col>
                                <b-img
                                    :src="imageSrc"
                                ></b-img> </b-col></b-row></b-col
                ></b-row>
            </div>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'artifact',
    data: function() {
        return {
            data: null,
            dataLoading: false,
            dataNotFound: false,
            imageSrc: `/apis/v1/sessions/view${this.$router.currentRoute.params.path}/`
        };
    },
    computed: {
        ...mapGetters([
            'profile',
            'workflow',
            'workflowsRecentlyRun',
            'session',
            'sessionLoading'
        ])
    }
};
</script>

<style scoped></style>
