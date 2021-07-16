<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="isRootPath">
            <b-row
                ><b-col
                    ><h2 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-tasks fa-fw"></i> Your Tasks
                    </h2></b-col
                ><b-col md="auto" align-self="center" class="mb-1"
                    ><small
                        >{{ tasks.length }} shown,
                        {{ profile.stats.total_tasks }} total</small
                    ></b-col
                >
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
                        id="refresh-tasks"
                        :disabled="tasksLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Refresh tasks"
                        @click="refresh"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="tasksLoading"
                            label="Loading..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i
                        >{{ tasksLoading ? 'Loading...' : 'Refresh' }}</b-button
                    ><b-popover
                        :show.sync="profile.hints"
                        triggers="manual"
                        placement="left"
                        target="refresh-tasks"
                        title="Refresh Tasks"
                        >Click here to refresh your tasks.</b-popover
                    ></b-col
                >
            </b-row>
            <b-row v-if="tasksLoading" class="mt-2">
                <b-col class="text-left">
                    <b-spinner
                        small
                        v-if="tasksLoading"
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading your tasks...</span
                    >
                </b-col>
            </b-row>
            <b-row v-else>
                <b-col>
                    <!--Running
                    <b-badge
                        pill
                        :title="tasksRunning.length + ' running'"
                        class="ml-1 mr-1 mb-1"
                        variant="warning"
                        >{{ tasksRunning.length }}</b-badge
                    >-->
                    <b-row class="pl-0 pr-0"
                        ><b-col class="m-0 pl-0 pr-0">
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                v-if="filtered.length === 0"
                            >
                                No tasks to show.
                            </p>
                            <div v-else>
                                <b-input-group size="sm" style="bottom: 4px"
                                    ><template #prepend>
                                        <b-input-group-text
                                            ><i class="fas fa-search"></i
                                        ></b-input-group-text> </template
                                    ><b-form-input
                                        :class="
                                            profile.darkMode
                                                ? 'theme-search-dark'
                                                : 'theme-search-light'
                                        "
                                        size="lg"
                                        type="search"
                                        v-model="searchText"
                                    ></b-form-input>
                                </b-input-group>
                                <b-list-group class="text-left m-0 p-0 mt-1">
                                    <b-list-group-item
                                        style="box-shadow: -2px 2px 2px #adb5bd"
                                        v-for="task in filtered"
                                        v-bind:key="task.name"
                                        :class="
                                            profile.darkMode
                                                ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                                : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                        "
                                    >
                                        <b-img
                                            v-if="
                                                task.workflow_image_url !==
                                                    undefined &&
                                                    task.workflow_image_url !==
                                                        null
                                            "
                                            rounded
                                            class="card-img-right"
                                            style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                            right
                                            :src="task.workflow_image_url"
                                        ></b-img>
                                        <b-link
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light mr-1'
                                                    : 'text-dark mr-1'
                                            "
                                            :to="{
                                                name: 'task',
                                                params: {
                                                    owner: task.owner,
                                                    name: task.name
                                                }
                                            }"
                                            replace
                                            >{{ task.name }}</b-link
                                        ><b-badge
                                            v-for="tag in task.tags"
                                            v-bind:key="tag"
                                            class="mr-2"
                                            variant="secondary"
                                            >{{ tag }}
                                        </b-badge>
                                        <span v-if="task.project !== null">
                                            <b-badge
                                                class="mr-2"
                                                variant="info"
                                                >{{
                                                    task.project.title
                                                }}</b-badge
                                            ><small v-if="task.study !== null"
                                                ><b-badge
                                                    class="mr-2"
                                                    variant="info"
                                                    >{{
                                                        task.study.title
                                                    }}</b-badge
                                                ></small
                                            >
                                        </span>
                                        <br />
                                        <b-spinner
                                            class="mb-1 mr-1"
                                            style="width: 0.7rem; height: 0.7rem;"
                                            v-if="!task.is_complete"
                                            variant="warning"
                                        >
                                        </b-spinner>
                                        <b-badge
                                            variant="warning"
                                            v-if="!task.is_complete"
                                            >Running</b-badge
                                        >
                                        <b-badge
                                            :variant="
                                                task.is_failure ||
                                                task.is_timeout
                                                    ? 'danger'
                                                    : task.is_cancelled
                                                    ? 'secondary'
                                                    : 'success'
                                            "
                                            v-else
                                            >{{
                                                task.status.toUpperCase()
                                            }}</b-badge
                                        >
                                        <small>
                                            on
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :to="{
                                                    name: 'agent',
                                                    params: {
                                                        name: task.agent.name
                                                    }
                                                }"
                                                >{{
                                                    task.agent
                                                        ? task.agent.name
                                                        : '[agent removed]'
                                                }}</b-link
                                            >
                                            {{ prettify(task.updated) }}</small
                                        >
                                        <br />
                                        <small
                                            v-if="task.workflow_name !== null"
                                            class="mr-1"
                                            ><a
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :href="
                                                    `https://github.com/${task.workflow_owner}/${task.workflow_name}`
                                                "
                                                ><i
                                                    class="fab fa-github fa-fw"
                                                ></i>
                                                {{ task.workflow_owner }}/{{
                                                    task.workflow_name
                                                }}</a
                                            >
                                        </small>
                                    </b-list-group-item>
                                </b-list-group>
                                <div v-if="tasksNextPage !== null">
                                    <b-button
                                        id="load-more-completed-tasks"
                                        :disabled="tasksLoading"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        size="sm"
                                        v-b-tooltip.hover
                                        title="Load more"
                                        @click="loadMoreTasks"
                                        block
                                        class="ml-0 mt-0 mr-0 text-center"
                                    >
                                        <b-spinner
                                            small
                                            v-if="tasksLoading"
                                            label="Loading..."
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                            class="mr-1"
                                        ></b-spinner
                                        ><i
                                            v-else
                                            class="fas fa-caret-down mr-1"
                                        ></i
                                        >{{
                                            tasksLoading
                                                ? 'Loading...'
                                                : 'Load More'
                                        }}</b-button
                                    ><b-popover
                                        :show.sync="profile.hints"
                                        triggers="manual"
                                        placement="left"
                                        target="load-more-completed-tasks"
                                        title="Load More"
                                        >Click here to load more completed
                                        tasks.</b-popover
                                    >
                                </div>
                            </div>
                        </b-col>
                    </b-row>
                </b-col>
            </b-row>
        </div>
        <router-view
            v-else
            :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        ></router-view>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import router from '@/router';
import * as Sentry from '@sentry/browser';
import { guid } from '@/utils';

export default {
    name: 'tasks',
    data: function() {
        return {
            searchText: ''
        };
    },
    methods: {
        async loadMoreTasks() {
            await this.$store.dispatch('tasks/loadMore', {
                page: this.tasksNextPage
            });
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        showRemovePrompt(task) {
            this.$bvModal.show('remove ' + task.name);
        },
        async refresh() {
            await this.$store.dispatch('tasks/loadAll');
        },
        async remove(task) {
            await axios
                .get(`/apis/v1/tasks/${task.owner}/${task.name}/delete/`)
                .then(async response => {
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'tasks/setAll',
                                response.data.tasks
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Deleted task ${task.name}`,
                                guid: guid().toString(),
                                time: moment().format()
                            })
                        ]);
                        if (
                            this.$router.currentRoute.name === 'task' &&
                            task.name === this.$router.currentRoute.params.name
                        )
                            router.push({
                                name: 'tasks'
                            });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to delete ${task.name}`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to delete task`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    return error;
                });
        }
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('tasks', [
            'tasks',
            'tasksLoading',
            'tasksRunning',
            'tasksCompleted',
            'tasksSucceeded',
            'tasksFailed',
            'tasksNextPage'
        ]),
        isRootPath() {
            return this.$route.name === 'tasks';
        },
        filtered() {
            return this.tasks.filter(
                task =>
                    (task.workflow_name !== null &&
                        task.workflow_name.includes(this.searchText)) ||
                    (task.name !== null &&
                        task.name.includes(this.searchText)) ||
                    task.tags.some(tag => tag.includes(this.searchText)) ||
                    (task.project !== null &&
                        task.project.title.includes(this.searchText)) ||
                    (task.study !== null &&
                        task.study.title.includes(this.searchText))
            );
        },
        filteredRunning() {
            return this.tasksRunning.filter(
                sub =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.searchText)) ||
                    (sub.name !== null && sub.name.includes(this.searchText)) ||
                    sub.tags.some(tag => tag.includes(this.searchText))
            );
        },
        filteredCompleted() {
            return this.tasksCompleted.filter(
                sub =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.searchText)) ||
                    (sub.name !== null && sub.name.includes(this.searchText)) ||
                    sub.tags.some(tag => tag.includes(this.searchText))
            );
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
