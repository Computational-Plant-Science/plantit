<template>
    <b-card
        :title="project.title"
        :sub-title="project.unique_id"
        :bg-variant="profile.darkMode ? 'dark' : 'white'"
        :header-text-variant="profile.darkMode ? 'white' : 'dark'"
        :text-variant="profile.darkMode ? 'white' : 'dark'"
        :body-text-variant="profile.darkMode ? 'white' : 'dark'"
        no-body
    >
        <b-card-body>
            <h4>
                <b-link
                    :class="profile.darkMode ? 'text-white' : 'text-dark'"
                    :to="{
                        name: 'project',
                        params: {
                            owner: project.owner,
                            title: project.title
                        }
                    }"
                    >{{ project.title }}</b-link
                >
            </h4>
            <h6
                :class="profile.darkMode ? 'text-white' : 'text-dark'"
                v-if="project.description !== null"
            >
                {{ project.description }}
            </h6>
            <span v-if="project.submission_date !== null">
                <small
                    >Submission: {{ prettify(project.submission_date) }}</small
                >
                <br />
            </span>
            <span v-if="project.public_release_date !== null">
                <small
                    >Release: {{ prettify(project.public_release_date) }}</small
                >
                <br />
            </span>
            <span v-if="project.studies.length !== 0">
                <small>Studies: {{ project.studies.length }}</small>
                <br />
            </span>
            <span v-if="project.team.length !== 0">
                <small>Team Members: {{ project.team.length }}</small>
            </span>
        </b-card-body>
    </b-card>
</template>

<script>
import moment from 'moment';
import { mapGetters } from 'vuex';

export default {
    name: 'project-blurb.vue',
    props: {
        project: Object
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        }
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading'])
    }
};
</script>

<style scoped></style>
