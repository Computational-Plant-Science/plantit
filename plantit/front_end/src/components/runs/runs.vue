<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="profileLoading">
            <b-row>
                <b-col class="text-center">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </b-col>
            </b-row>
        </div>
        <div v-else>
            <div v-if="isRootPath">
                <b-row
                    ><b-col
                        ><h2
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Your Runs
                        </h2></b-col
                    >
                    <b-col md="auto" class="ml-0" align-self="center"
                        ><b-button
                            :disabled="runsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            title="Refresh runs"
                            @click="refreshRuns"
                            class="ml-0 mt-0 mr-0"
                        >
                            <b-spinner
                                small
                                v-if="runsLoading"
                                label="Refreshing..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="mr-1"
                            ></b-spinner
                            ><i v-else class="fas fa-redo mr-1"></i
                            >Refresh</b-button
                        ></b-col
                    >
                </b-row>
                <hr class="mt-2 mb-2" style="border-color: gray" />
                <b-row v-if="runsLoading" class="mt-2">
                    <b-col class="text-center">
                        <b-spinner
                            type="grow"
                            label="Loading..."
                            variant="secondary"
                        ></b-spinner>
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
                                class="ml-1 mr-1 mb-1"
                                variant="warning"
                                >{{ runningRuns.length }}</b-badge
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
                                    v-if="runningRuns.length === 0"
                                >
                                    No workflows are running right now.
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
                                            v-model="runSearchText"
                                        ></b-form-input>
                                    </b-input-group>
                                    <b-list-group class="text-left m-0 p-0">
                                        <b-list-group-item
                                            variant="default"
                                            style="box-shadow: -2px 2px 2px #adb5bd"
                                            v-for="run in filteredRunningRuns"
                                            v-bind:key="run.name"
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                            "
                                        >
                                            <b-img
                                                v-if="
                                                    run.workflow_image_url !==
                                                        undefined &&
                                                        run.workflow_image_url !==
                                                            null
                                                "
                                                rounded
                                                class="card-img-right"
                                                style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                                right
                                                :src="run.workflow_image_url"
                                            ></b-img>
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :to="{
                                                    name: 'run',
                                                    params: {
                                                        owner: run.owner,
                                                        name: run.name
                                                    }
                                                }"
                                                replace
                                                >{{ run.name }}</b-link
                                            >
                                            <br />
                                            <div
                                                v-if="
                                                    run.tags !== undefined &&
                                                        run.tags.length > 0
                                                "
                                            >
                                                <b-badge
                                                    v-for="tag in run.tags"
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
                                                v-if="!run.is_complete"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'light'
                                                        : 'dark'
                                                "
                                            >
                                            </b-spinner>
                                            <small v-if="!run.is_complete"
                                                >Running</small
                                            >
                                            <b-badge
                                                :variant="
                                                    run.is_failure ||
                                                    run.is_timeout
                                                        ? 'danger'
                                                        : run.is_cancelled
                                                        ? 'secondary'
                                                        : 'success'
                                                "
                                                v-else
                                                >{{ run.job_status }}</b-badge
                                            >
                                            <small> on </small>
                                            <b-badge
                                                class="ml-0 mr-0"
                                                variant="secondary"
                                                >{{ run.agent }}</b-badge
                                            ><small>
                                                {{
                                                    prettify(run.updated)
                                                }}</small
                                            >
                                            <br />
                                            <small
                                                v-if="
                                                    run.workflow_name !== null
                                                "
                                                class="mr-1"
                                                ><a
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    :href="
                                                        `https://github.com/${run.workflow_owner}/${run.workflow_name}`
                                                    "
                                                    ><i
                                                        class="fab fa-github fa-fw"
                                                    ></i>
                                                    {{ run.workflow_owner }}/{{
                                                        run.workflow_name
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
                                pill
                                class="ml-1 mr-1 mb-1"
                                variant="success"
                                >{{ succeededRuns.length }}</b-badge
                            >
                            <b-badge
                                pill
                                class="ml-1 mr-1 mb-1"
                                variant="danger"
                                >{{ failedRuns.length }}</b-badge
                            >
                        </template>
                        <b-row>
                            <b-col
                                v-if="runsLoading"
                                class="m-0 pl-0 pr-0 text-center"
                            >
                                <b-spinner
                                    type="grow"
                                    variant="secondary"
                                ></b-spinner
                            ></b-col>
                            <b-col
                                v-if="
                                    !runsLoading && completedRuns.length === 0
                                "
                                class="m-0 pl-0 pr-0"
                            >
                                <p
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    You haven't run any workflows.
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
                                        v-model="runSearchText"
                                    ></b-form-input> </b-input-group
                            ></b-col>
                        </b-row>
                        <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                            ><b-col
                                v-if="!runsLoading && completedRuns.length > 0"
                                class="m-0 pl-0 pr-0 text-center"
                            >
                                <b-list-group class="text-left m-0 p-0">
                                    <b-list-group-item
                                        variant="default"
                                        style="box-shadow: -2px 2px 2px #adb5bd"
                                        v-for="run in filteredCompletedRuns"
                                        v-bind:key="run.name"
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
                                                        run.workflow_image_url !==
                                                            undefined &&
                                                            run.workflow_image_url !==
                                                                null
                                                    "
                                                    rounded
                                                    class="card-img-right"
                                                    style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                                    right
                                                    :src="
                                                        run.workflow_image_url
                                                    "
                                                ></b-img>
                                                <b-link
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    :to="{
                                                        name: 'run',
                                                        params: {
                                                            owner: run.owner,
                                                            name: run.name
                                                        }
                                                    }"
                                                    replace
                                                    >{{ run.name }}</b-link
                                                >
                                            </b-col>
                                        </b-row>
                                        <b-row
                                            ><b-col>
                                                <div
                                                    v-if="
                                                        run.tags !==
                                                            undefined &&
                                                            run.tags.length > 0
                                                    "
                                                >
                                                    <b-badge
                                                        v-for="tag in run.tags"
                                                        v-bind:key="tag"
                                                        class="mr-1"
                                                        variant="secondary"
                                                        >{{ tag }}
                                                    </b-badge>
                                                    <br
                                                        v-if="
                                                            run.tags.length > 0
                                                        "
                                                    />
                                                </div>
                                                <small v-if="!run.is_complete"
                                                    >Running</small
                                                >
                                                <b-badge
                                                    :variant="
                                                        run.is_failure ||
                                                        run.is_timeout
                                                            ? 'danger'
                                                            : run.is_cancelled
                                                            ? 'secondary'
                                                            : 'success'
                                                    "
                                                    v-else
                                                    >{{
                                                        run.job_status
                                                    }}</b-badge
                                                >
                                                <small>
                                                    on
                                                </small>
                                                <b-badge
                                                    class="ml-0 mr-0"
                                                    variant="secondary"
                                                    >{{ run.agent }}</b-badge
                                                ><small>
                                                    {{
                                                        prettify(run.updated)
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
                                                            `https://github.com/${run.workflow_owner}/${run.workflow_name}`
                                                        "
                                                        ><i
                                                            class="fab fa-github fa-fw"
                                                        ></i>
                                                        {{
                                                            run.workflow_owner
                                                        }}/{{
                                                            run.workflow_name
                                                        }}</a
                                                    >
                                                </small>
                                            </b-col>
                                            <b-col md="auto">
                                                <b-button
                                                    v-if="run.is_complete"
                                                    variant="outline-danger"
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    title="Delete Run"
                                                    class="text-right"
                                                    @click="
                                                        showDeleteRunPrompt(run)
                                                    "
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
        </div>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import router from '@/router';
import * as Sentry from '@sentry/browser';

export default {
    name: 'runs',
    data: function() {
        return {
            runSearchText: ''
        };
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async refreshRuns() {
            await this.$store.dispatch('runs/loadAll');
        },
        showDeleteRunPrompt(run) {
            this.$bvModal.show('delete ' + run.name);
        },
        deleteRun(run) {
            axios
                .get(`/apis/v1/runs/${run.owner}/${run.name}/delete/`)
                .then(response => {
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                        this.$store.dispatch('runs/loadAll');
                        if (
                            this.$router.currentRoute.name === 'run' &&
                            run.name === this.$router.currentRoute.params.name
                        )
                            router.push({
                                name: 'runs'
                            });
                    } else {
                        this.showFailedToCancelAlert = true;
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        }
    },
    async mounted() {
        // await Promise.all([this.$store.dispatch('runs/loadAll')]);
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('runs', ['runs', 'runsLoading']),
        isRootPath() {
            return this.$route.name === 'runs';
        },
        runningRuns() {
            return this.runs.filter(r => !r.is_complete);
        },
        completedRuns() {
            return this.runs.filter(r => r.is_complete);
        },
        succeededRuns() {
            return this.completedRuns.filter(r => r.is_success);
        },
        failedRuns() {
            return this.completedRuns.filter(r => r.is_failure);
        },
        filteredRunningRuns() {
            return this.runningRuns.filter(
                r =>
                    (r.workflow_name !== null &&
                        r.workflow_name.includes(this.runSearchText)) ||
                    (r.name !== null && r.name.includes(this.runSearchText)) ||
                    r.tags.some(t => t.includes(this.runSearchText))
            );
        },
        filteredCompletedRuns() {
            return this.completedRuns.filter(
                r =>
                    (r.workflow_name !== null &&
                        r.workflow_name.includes(this.runSearchText)) ||
                    (r.name !== null && r.name.includes(this.runSearchText)) ||
                    r.tags.some(t => t.includes(this.runSearchText))
            );
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
</style>
