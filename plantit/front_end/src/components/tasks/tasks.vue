<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="isRootPath">
            <b-row
                ><b-col md="auto"
                    ><h2 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-tasks fa-fw"></i> Your Tasks
                    </h2></b-col
                >
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
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
            <b-tabs
                v-else
                nav-class="bg-transparent"
                active-nav-item-class="bg-info text-dark"
                pills
            >
                <b-tab
                    :title-link-class="
                        profile.darkMode ? 'text-white' : 'text-dark'
                    "
                    :class="
                        profile.darkMode
                            ? 'theme-dark m-0 p-3'
                            : 'theme-light m-0 p-3'
                    "
                >
                    <template #title>
                        Running
                        <b-badge
                            pill
                            :title="tasksRunning.length + ' running'"
                            class="ml-1 mr-1 mb-1"
                            variant="warning"
                            >{{ tasksRunning.length }}</b-badge
                        >
                    </template>
                    <b-row class="pl-0 pr-0"
                        ><b-col class="m-0 pl-0 pr-0">
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                v-if="tasksRunning.length === 0"
                            >
                                No tasks running right now.
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
                                        v-for="task in filteredRunning"
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
                                                    ? 'text-light'
                                                    : 'text-dark'
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
                                        >
                                        <br />
                                        <div
                                            v-if="
                                                task.tags !== undefined &&
                                                    task.tags.length > 0
                                            "
                                        >
                                            <b-badge
                                                v-for="tag in task.tags"
                                                v-bind:key="tag"
                                                class="mr-1"
                                                variant="secondary"
                                                >{{ tag }}
                                            </b-badge>
                                            <br />
                                        </div>
                                        <b-spinner
                                            class="mb-1 mr-1"
                                            style="width: 0.7rem; height: 0.7rem;"
                                            v-if="!task.is_complete"
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                        >
                                        </b-spinner>
                                        <small v-if="!task.is_complete"
                                            >Running</small
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
                                            >{{ task.status }}</b-badge
                                        >
                                        <small>
                                            on
                                            <b class="ml-0 mr-0">{{
                                                task.agent
                                                    ? task.agent
                                                    : '[agent removed]'
                                            }}</b>
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
                            </div>
                        </b-col></b-row
                    >
                </b-tab>
                <b-tab
                    :title-link-class="
                        profile.darkMode ? 'text-white' : 'text-dark'
                    "
                    :class="
                        profile.darkMode
                            ? 'theme-dark m-0 p-3'
                            : 'theme-light m-0 p-3'
                    "
                >
                    <template #title>
                        Completed
                        <b-badge
                            :title="tasksSucceeded.length + ' succeeded'"
                            pill
                            class="ml-1 mr-1 mb-1"
                            variant="warning"
                            >{{ tasksSucceeded.length }}</b-badge
                        >
                        <b-badge
                            :title="tasksFailed.length + ' failed'"
                            pill
                            class="ml-1 mr-1 mb-1"
                            variant="danger"
                            >{{ tasksFailed.length }}</b-badge
                        >
                    </template>
                    <b-row>
                        <b-col
                            v-if="tasksLoading"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <b-spinner
                                type="grow"
                                variant="secondary"
                            ></b-spinner
                        ></b-col>
                        <b-col
                            v-if="!tasksLoading && tasksCompleted.length === 0"
                            class="m-0 pl-0 pr-0"
                        >
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                No tasks have completed.
                            </p>
                        </b-col>
                        <b-col v-else class="m-0 pl-0 pr-0 text-center"
                            ><b-input-group size="sm" style="bottom: 4px"
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
                                ></b-form-input> </b-input-group
                        ></b-col>
                    </b-row>
                    <b-row class="mt-1 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col
                            v-if="!tasksLoading && tasksCompleted.length > 0"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <b-list-group class="text-left m-0 p-0">
                                <b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="task in filteredCompleted"
                                    v-bind:key="task.name"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                            : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                    "
                                >
                                    <b-row
                                        ><b-col>
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
                                                        ? 'text-light'
                                                        : 'text-dark'
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
                                            >
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col>
                                            <div
                                                v-if="
                                                    task.tags !== undefined &&
                                                        task.tags.length > 0
                                                "
                                            >
                                                <b-badge
                                                    v-for="tag in task.tags"
                                                    v-bind:key="tag"
                                                    class="mr-1"
                                                    variant="secondary"
                                                    >{{ tag }}
                                                </b-badge>
                                                <br
                                                    v-if="task.tags.length > 0"
                                                />
                                            </div>
                                            <small v-if="!task.is_complete"
                                                >Running</small
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
                                                >{{ task.status }}</b-badge
                                            >
                                            <small>
                                                on
                                                <b class="ml-0 mr-0">{{
                                                    task.agent
                                                        ? task.agent
                                                        : '[agent removed]'
                                                }}</b>
                                                {{
                                                    prettify(task.updated)
                                                }}</small
                                            >
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col>
                                            <small class="mr-1"
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
                                        </b-col>
                                        <b-col md="auto">
                                            <b-button
                                                v-if="task.is_complete"
                                                variant="outline-danger"
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Delete Task"
                                                class="text-right"
                                                @click="showRemovePrompt(task)"
                                            >
                                                <i class="fas fa-trash"></i>
                                                Delete
                                            </b-button>
                                        </b-col></b-row
                                    >
                                </b-list-group-item>
                            </b-list-group>
                        </b-col>
                    </b-row>
                </b-tab>
            </b-tabs>
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
            'tasksFailed'
        ]),
        isRootPath() {
            return this.$route.name === 'tasks';
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
