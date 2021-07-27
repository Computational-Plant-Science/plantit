<template>
    <b-card
        class="mt-2 pt-1 overflow-hidden"
        :bg-variant="profile.darkMode ? 'dark' : 'white'"
        :header-text-variant="profile.darkMode ? 'white' : 'dark'"
        :text-variant="profile.darkMode ? 'white' : 'dark'"
        :body-text-variant="profile.darkMode ? 'white' : 'dark'"
        no-body
        :style="
            task.is_failure || task.is_timeout
                ? 'border-bottom: 5px solid red'
                : task.is_cancelled
                ? 'border-bottom: 5px solid lightgray'
                : task.is_complete
                ? 'border-bottom: 5px solid #d6df5D'
                : 'border-bottom: 5px solid #e2e3b0'
        "
    >
        <b-card-body>
            <b-link
                :class="profile.darkMode ? 'text-light' : 'text-dark'"
                :to="{
                    name: 'task',
                    params: {
                        owner: task.owner,
                        name: task.name
                    }
                }"
                replace
                >{{ task.name }}</b-link
            >
            <span v-if="project && task.project !== null">
            <br/>
            <b-link
                :class="profile.darkMode ? 'text-light' : 'text-dark'"
                :to="{
                    name: 'project',
                    params: {
                        owner: task.project.owner,
                        title: task.project.title
                    }
                }"
                ><b-img
                    class="mb-1 mr-1"
                    style="max-width: 18px"
                    :src="
                        profile.darkMode
                            ? require('../../assets/miappe_icon.png')
                            : require('../../assets/miappe_icon_black.png')
                    "
                ></b-img>
                <span v-if="task.project !== null"
                    >{{ task.project.title }}
                    <small v-if="task.study !== null">{{
                        task.study.title
                    }}</small></span
                ></b-link
            >
            </span>
            <span v-if="task.tags !== undefined && task.tags.length > 0">
                <b-badge
                    v-for="tag in task.tags"
                    v-bind:key="tag"
                    class="ml-2 mb-2"
                    variant="secondary"
                    >{{ tag }}
                </b-badge>
            </span>
            <br />
            <span v-if="!task.is_complete"
                ><b-spinner
                    class="mb-1 mr-1"
                    style="width: 0.7rem; height: 0.7rem;"
                    variant="warning"
                >
                </b-spinner>
                <small>Running on </small></span
            >
            <small v-else>Ran on </small>
            <small>
                <b-link
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    :to="{
                        name: 'agent',
                        params: {
                            name: task.agent.name
                        }
                    }"
                    ><b-img
                        v-if="task.agent.logo"
                        rounded
                        class="overflow-hidden"
                        style="max-height: 1rem;"
                        :src="task.agent.logo"
                    ></b-img
                    ><i v-else class="fas fa-server fa-fw"></i>
                    {{
                        task.agent ? task.agent.name : '[agent removed]'
                    }}</b-link
                >

                {{ prettify(task.updated) }}</small
            >
            <br />
            <b-img
                v-if="
                    task.workflow_image_url !== undefined &&
                        task.workflow_image_url !== null
                "
                rounded
                class="card-img-right"
                style="max-width: 5rem;position: absolute;right: -15px;top: -20px;z-index:1;"
                right
                :src="task.workflow_image_url"
            ></b-img>
            <small v-if="task.workflow_name !== null" class="mr-1"
                ><a
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    :href="
                        `https://github.com/${task.workflow_owner}/${task.workflow_name}`
                    "
                    ><i class="fab fa-github fa-fw"></i>
                    {{ task.workflow_owner }}/{{ task.workflow_name }}</a
                >
            </small>
            <b-row class="mt-0"
                ><b-col
                    style="top: 27px;position: relative; font-size: 18pt"
                    align-self="end"
                    :class="
                        task.is_failure || task.is_timeout
                            ? 'text-danger'
                            : task.is_cancelled
                            ? 'text-secondary'
                            : task.is_complete
                            ? 'text-success'
                            : 'text-warning'
                    "
                    ><b>{{ task.status.toUpperCase() }}</b></b-col
                ></b-row
            >
        </b-card-body>
    </b-card>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'task-blurb',
    props: {
        task: {
            type: Object,
            required: true
        },
        project: {
            type: Boolean,
            required: false
        }
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

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
