<template>
    <b-card
        class="mt-2 pt-1 overflow-hidden"
        :bg-variant="profile.darkMode ? 'dark' : 'white'"
        :header-text-variant="profile.darkMode ? 'white' : 'dark'"
        border-variant="secondary"
        :text-variant="profile.darkMode ? 'white' : 'dark'"
        :body-text-variant="profile.darkMode ? 'white' : 'dark'"
        no-body
    >
        <b-card-body>
            <span v-if="!task.is_complete"
                ><b-spinner
                    class="mb-1 mr-1"
                    style="width: 0.7rem; height: 0.7rem"
                    :variant="profile.darkMode ? 'text-white' : 'text-dark'"
                >
                </b-spinner> </span
            ><b
                :class="
                    task.is_failure
                        ? 'text-danger'
                        : task.is_cancelled || task.is_timeout
                        ? 'text-secondary'
                        : task.is_complete
                        ? 'text-success'
                        : profile.darkMode
                        ? 'text-white'
                        : 'text-dark'
                "
                >{{
                    !task.agent.is_local &&
                    !task.is_complete &&
                    task.job_status !== null
                        ? task.job_status.toUpperCase()
                        : task.status.toUpperCase()
                }}</b
            >
            <small class="ml-1 mr-1">on</small>
            <small>
                <b-link
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    :to="{
                        name: 'agent',
                        params: {
                            name: task.agent.name,
                        },
                    }"
                    ><b-img
                        v-if="task.agent.logo"
                        rounded
                        class="overflow-hidden"
                        style="max-height: 1rem"
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
            <b-link
                :class="profile.darkMode ? 'text-light' : 'text-dark'"
                :to="{
                    name: 'task',
                    params: {
                        owner: task.owner,
                        guid: task.guid,
                    },
                }"
                replace
                >{{ task.guid}}</b-link
            >
            <span v-if="project && task.project !== null">
                <br />
                <b-link
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    :to="{
                        name: 'project',
                        params: {
                            owner: task.project.owner,
                            title: task.project.title,
                        },
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
            <b-img
                v-if="
                    task.workflow_image_url !== undefined &&
                    task.workflow_image_url !== null
                "
                rounded
                class="card-img-right"
                style="
                    max-width: 5rem;
                    position: absolute;
                    right: -15px;
                    top: -20px;
                    z-index: 1;
                "
                right
                :src="task.workflow_image_url"
            ></b-img>
            <small v-if="task.workflow_name !== null" class="mr-1 mb-0"
                ><a
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    :href="`https://github.com/${task.workflow_owner}/${task.workflow_name}`"
                    ><i class="fab fa-github fa-fw"></i>
                    {{ task.workflow_owner }}/{{ task.workflow_name }}</a
                >
            </small>
            <br />
            <span v-if="task.output_path !== null && task.output_path !== ''">
                <small v-if="task.input_path !== null"
                    ><i class="far fa-folder fa-fw mr-1"></i
                    >{{ task.input_path }}</small
                ><small v-else
                    ><i
                        v-if="profile.darkMode"
                        class="far fa-circle text-white fa-fw"
                    ></i
                    ><i v-else class="far fa-circle text-dark fa-fw"></i
                ></small>
                <small
                    ><i
                        v-if="profile.darkMode"
                        class="fas fa-arrow-right text-white fa-fw mr-1 ml-1"
                    ></i
                    ><i
                        v-else
                        class="fas fa-arrow-right text-dark fa-fw mr-1 ml-1"
                    ></i
                ></small>
                <small v-if="task.output_path !== null"
                    ><i class="far fa-folder fa-fw mr-1"></i
                    >{{ task.output_path }}</small
                >
            </span>
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
            required: true,
        },
        project: {
            type: Boolean,
            required: false,
        },
    },
    methods: {
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
    },
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
