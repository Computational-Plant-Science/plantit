<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent">
        <div v-if="isRootPath">
            <b-row
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-tasks fa-fw"></i> Tasks
                    </h4></b-col
                ><b-col align-self="center" md="auto"
                    ><b-badge
                        pill
                        :title="tasksRunning.length + ' running'"
                        class="ml-1 mr-1 mb-1"
                        variant="warning"
                        >{{ tasksRunning.length }}</b-badge
                    >
                    <small>running</small></b-col
                ><b-col
                    v-if="tasksNextPage !== null"
                    md="auto"
                    align-self="center"
                    ><b-button
                        id="load-more-completed-tasks"
                        :disabled="tasksLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        title="Load more"
                        @click="loadMoreTasks"
                        class="ml-0 mt-0 mr-0 text-center"
                    >
                        <b-spinner
                            small
                            v-if="tasksLoading"
                            label="Loading..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-plus mr-1"></i
                        >{{
                            tasksLoading ? 'Loading...' : 'Load More'
                        }}</b-button
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="left"
                        target="load-more-completed-tasks"
                        title="Load More"
                        >Click here to load more completed tasks.</b-popover
                    ></b-col
                >
                <b-col md="auto" class="ml-0 mb-0" align-self="center"
                    ><b-button
                        id="refresh-tasks"
                        :disabled="tasksLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
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
                        v-if="profile.hints"
                        triggers="hover"
                        placement="left"
                        target="refresh-tasks"
                        title="Refresh Tasks"
                        >Click here to refresh your tasks.</b-popover
                    ></b-col
                ></b-row
            >
            <b-row
                ><b-col
                    ><b-input-group size="sm"
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
                        ></b-form-input> </b-input-group></b-col
            ></b-row>
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
                    <b-row class="pl-0 pr-0 mt-2"
                        ><b-col class="m-0 pl-0 pr-0">
                            <b-tabs
                                v-model="activeTab"
                                nav-class="bg-transparent"
                                active-nav-item-class="bg-transparent text-dark"
                                pills
                            >
                                <b-tab
                                    title="Running"
                                    :title-link-class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    :class="
                                        profile.darkMode
                                            ? 'theme-dark m-0 pl-3 pr-3'
                                            : 'theme-light m-0 pl-3 pr-3'
                                    "
                                >
                                    <template #title>
                                        <b-button
                                            id="running-tasks"
                                            :variant="
                                                activeTab === 0
                                                    ? profile.darkMode
                                                        ? 'outline-warning'
                                                        : 'warning'
                                                    : profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            title="Running tasks"
                                            ><i
                                                class="fas fa-terminal fa-fw"
                                            ></i>
                                            Running </b-button
                                        ><b-popover
                                            v-if="profile.hints"
                                            triggers="hover"
                                            placement="bottomleft"
                                            target="running-tasks"
                                            title="Running Tasks"
                                            >Click here to view currently
                                            running tasks.</b-popover
                                        ></template
                                    >
                                    <b-row
                                        v-if="
                                            !tasksLoading &&
                                            tasksRunning.length === 0
                                        "
                                        class="m-0 pl-0 pr-0"
                                    >
                                        <b-col>
                                            <p
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                            >
                                                No tasks are running.
                                            </p>
                                        </b-col>
                                    </b-row>
                                    <b-list-group
                                        class="text-left m-0 p-0 mt-1"
                                    >
                                        <taskblurb
                                            v-for="task in filteredRunning"
                                            v-bind:key="task.guid"
                                            :task="task"
                                            :project="true"
                                        ></taskblurb>
                                    </b-list-group>
                                </b-tab>
                                <b-tab
                                    title="Completed"
                                    :title-link-class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    :class="
                                        profile.darkMode
                                            ? 'theme-dark m-0 pl-3 pr-3'
                                            : 'theme-light m-0 pl-3 pr-3'
                                    "
                                >
                                    <template #title>
                                        <b-button
                                            id="completed-tasks"
                                            :variant="
                                                activeTab === 1
                                                    ? profile.darkMode
                                                        ? 'outline-warning'
                                                        : 'warning'
                                                    : profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            title="Completed tasks"
                                            ><i class="fas fa-check fa-fw"></i>
                                            Completed </b-button
                                        ><b-popover
                                            v-if="profile.hints"
                                            triggers="hover"
                                            placement="bottomleft"
                                            target="completed-tasks"
                                            title="Completed Tasks"
                                            >Click here to view completed
                                            tasks.</b-popover
                                        ></template
                                    >
                                    <b-row
                                        v-if="
                                            !tasksLoading &&
                                            tasksCompleted.length === 0
                                        "
                                        class="m-0 pl-0 pr-0"
                                    >
                                        <b-col>
                                            <p
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                            >
                                                No completed tasks.
                                            </p>
                                        </b-col>
                                    </b-row>
                                    <b-list-group
                                        class="text-left m-0 p-0 mt-1"
                                    >
                                        <taskblurb
                                            v-for="task in filteredCompleted"
                                            v-bind:key="task.guid"
                                            :task="task"
                                            :project="true"
                                        ></taskblurb>
                                    </b-list-group>
                                </b-tab>
                                <b-tab
                                    title="Scheduled"
                                    :title-link-class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    :class="
                                        profile.darkMode
                                            ? 'theme-dark m-0 pl-3 pr-3'
                                            : 'theme-light m-0 pl-3 pr-3'
                                    "
                                >
                                    <template #title>
                                        <b-button
                                            id="scheduled-tasks"
                                            :variant="
                                                activeTab === 2
                                                    ? profile.darkMode
                                                        ? 'outline-warning'
                                                        : 'warning'
                                                    : profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            title="Scheduled tasks"
                                            ><i class="fas fa-clock fa-fw"></i>
                                            Scheduled </b-button
                                        ><b-popover
                                            v-if="profile.hints"
                                            triggers="hover"
                                            placement="bottomleft"
                                            target="scheduled-tasks"
                                            title="Scheduled Tasks"
                                            >Click here to view scheduled
                                            delayed and repeating
                                            tasks.</b-popover
                                        ></template
                                    >
                                    <b-row>
                                        <b-col>
                                            <b-row
                                                class="m-3 mb-1 pl-0 pr-0"
                                                align-v="center"
                                            >
                                                <b-col><b>Delayed</b></b-col>
                                            </b-row>
                                            <b-row
                                                v-if="
                                                    !tasksLoading &&
                                                    tasksDelayed.length === 0
                                                "
                                                class="m-0 pl-0 pr-0"
                                            >
                                                <b-col>
                                                    <p
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-light'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        No delayed tasks are
                                                        scheduled.
                                                    </p>
                                                </b-col>
                                            </b-row>
                                            <b-list-group
                                                class="text-left m-0 p-0 mt-1"
                                            >
                                                <delayedtaskblurb
                                                    v-for="task in tasksDelayed"
                                                    v-bind:key="task.guid"
                                                    :task="task"
                                                ></delayedtaskblurb>
                                            </b-list-group>
                                        </b-col>
                                        <b-col>
                                            <b-row
                                                class="m-3 mb-1 pl-0 pr-0"
                                                align-v="center"
                                            >
                                                <b-col><b>Repeating</b></b-col>
                                            </b-row>
                                            <b-row
                                                v-if="
                                                    !tasksLoading &&
                                                    tasksRepeating.length === 0
                                                "
                                                class="m-0 pl-0 pr-0"
                                            >
                                                <b-col>
                                                    <p
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-light'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        No repeating tasks are
                                                        scheduled.
                                                    </p>
                                                </b-col>
                                            </b-row>
                                            <b-list-group
                                                class="text-left m-0 p-0 mt-1"
                                            >
                                                <repeatingtaskblurb
                                                    v-for="task in tasksRepeating"
                                                    v-bind:key="task.guid"
                                                    :task="task"
                                                ></repeatingtaskblurb>
                                            </b-list-group>
                                        </b-col>
                                        <b-col>
                                            <b-row
                                                class="m-3 mb-1 pl-0 pr-0"
                                                align-v="center"
                                            >
                                                <b-col><b>Triggered</b></b-col>
                                            </b-row>
                                            <b-row
                                                v-if="
                                                    !tasksLoading &&
                                                    tasksTriggered.length === 0
                                                "
                                                class="m-0 pl-0 pr-0"
                                            >
                                                <b-col>
                                                    <p
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-light'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        No triggered tasks are
                                                        scheduled.
                                                    </p>
                                                </b-col>
                                            </b-row>
                                            <b-list-group
                                                class="text-left m-0 p-0 mt-1"
                                            >
                                                <triggeredtaskblurb
                                                    v-for="task in tasksTriggered"
                                                    v-bind:key="task.guid"
                                                    :task="task"
                                                ></triggeredtaskblurb>
                                            </b-list-group>
                                        </b-col>
                                    </b-row>
                                </b-tab>
                            </b-tabs>
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
import * as Sentry from '@sentry/browser';
import { guid } from '@/utils';
import taskblurb from '@/components/tasks/task-blurb';
import delayedtaskblurb from '@/components/tasks/delayed-task-blurb';
import repeatingtaskblurb from '@/components/tasks/repeating-task-blurb';
import triggeredtaskblurb from '@/components/tasks/triggered-task-blurb';

export default {
    name: 'tasks',
    components: {
        taskblurb,
        delayedtaskblurb,
        repeatingtaskblurb,
        triggeredtaskblurb,
    },
    data: function () {
        return {
            searchText: '',
            activeTab: 0,
        };
    },
    methods: {
        async deleteDelayed(guid) {
            this.unschedulingDelayed = true;
            await axios
                .get(`/apis/v1/tasks/${guid}/unschedule_delayed/`)
                .then(async (response) => {
                    await Promise.all([
                        this.$store.dispatch(
                            'tasks/setDelayed',
                            response.data.tasks
                        ),
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unscheduled delayed task`,
                            guid: guid().toString(),
                        }),
                    ]);
                    this.unschedulingDelayed = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unschedule delayed task`,
                        guid: guid().toString(),
                    });
                    this.unschedulingDelayed = false;
                    throw error;
                });
        },
        async deleteRepeating(id) {
            this.unschedulingRepeating = true;
            await axios
                .get(`/apis/v1/tasks/${id}/unschedule_repeating/`)
                .then(async (response) => {
                    await Promise.all([
                        this.$store.dispatch(
                            'tasks/setRepeating',
                            response.data.tasks
                        ),
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unscheduled repeating task`,
                            guid: guid().toString(),
                        }),
                    ]);
                    this.unschedulingRepeating = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unschedule repeating task`,
                        guid: guid().toString(),
                    });
                    this.unschedulingRepeating = false;
                    throw error;
                });
        },
        async deleteTriggered(id) {
            this.unschedulingTriggered = true;
            await axios
                .get(`/apis/v1/tasks/${id}/unschedule_triggered/`)
                .then(async (response) => {
                    await Promise.all([
                        this.$store.dispatch(
                            'tasks/setTriggered',
                            response.data.tasks
                        ),
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unscheduled triggered task`,
                            guid: guid().toString(),
                        }),
                    ]);
                    this.unschedulingTriggered = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unschedule triggered task`,
                        guid: guid().toString(),
                    });
                    this.unschedulingTriggered = false;
                    throw error;
                });
        },
        async loadMoreTasks() {
            await this.$store.dispatch('tasks/loadMore', {
                page: this.tasksNextPage,
            });
        },
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async refresh() {
            await Promise.all([
                this.$store.dispatch('tasks/loadAll'),
                this.$store.dispatch('tasks/loadDelayed'),
                this.$store.dispatch('tasks/loadRepeating'),
                this.$store.dispatch('tasks/loadTriggered'),
            ]);
        },
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('tasks', [
            'tasks',
            'tasksDelayed',
            'tasksRepeating',
            'tasksTriggered',
            'tasksLoading',
            'tasksRunning',
            'tasksCompleted',
            'tasksSucceeded',
            'tasksFailed',
            'tasksNextPage',
        ]),
        isRootPath() {
            return this.$route.name === 'tasks';
        },
        filtered() {
            return this.tasks.filter(
                (task) =>
                    (task.workflow_name !== null &&
                        task.workflow_name.includes(this.searchText)) ||
                    (task.name !== null &&
                        task.name.includes(this.searchText)) ||
                    task.tags.some((tag) => tag.includes(this.searchText)) ||
                    (task.project !== null &&
                        task.project.title.includes(this.searchText)) ||
                    (task.study !== null &&
                        task.study.title.includes(this.searchText))
            );
        },
        filteredRunning() {
            return this.tasksRunning.filter(
                (task) =>
                    (task.workflow_name !== null &&
                        task.workflow_name.includes(this.searchText)) ||
                    (task.name !== null &&
                        task.name.includes(this.searchText)) ||
                    task.tags.some((tag) => tag.includes(this.searchText)) ||
                    (task.project !== null &&
                        task.project.title.includes(this.searchText)) ||
                    (task.study !== null &&
                        task.study.title.includes(this.searchText))
            );
        },
        filteredCompleted() {
            return this.tasksCompleted.filter(
                (task) =>
                    (task.workflow_name !== null &&
                        task.workflow_name.includes(this.searchText)) ||
                    (task.name !== null &&
                        task.name.includes(this.searchText)) ||
                    task.tags.some((tag) => tag.includes(this.searchText)) ||
                    (task.project !== null &&
                        task.project.title.includes(this.searchText)) ||
                    (task.study !== null &&
                        task.study.title.includes(this.searchText))
            );
        },
    },
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
