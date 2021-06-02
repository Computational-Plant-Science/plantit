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
                            Your Submissions
                        </h2></b-col
                    >
                    <b-col md="auto" class="ml-0" align-self="center"
                        ><b-button
                            :disabled="submissionsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="md"
                            v-b-tooltip.hover
                            title="Refresh submissions"
                            @click="refresh"
                            class="ml-0 mt-0 mr-0"
                        >
                            <b-spinner
                                small
                                v-if="submissionsLoading"
                                label="Refreshing..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="mr-1"
                            ></b-spinner
                            ><i v-else class="fas fa-redo mr-1"></i
                            >Refresh</b-button
                        ></b-col
                    >
                </b-row>
                <b-row v-if="submissionsLoading" class="mt-2">
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
                                >{{ submissionsRunning.length }}</b-badge
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
                                    v-if="submissionsRunning.length === 0"
                                >
                                    No submissions running right now.
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
                                    <b-list-group class="text-left m-0 p-0">
                                        <b-list-group-item
                                            variant="default"
                                            style="box-shadow: -2px 2px 2px #adb5bd"
                                            v-for="submission in filteredRunning"
                                            v-bind:key="submission.name"
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                                    : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                            "
                                        >
                                            <b-img
                                                v-if="
                                                    submission.workflow_image_url !==
                                                        undefined &&
                                                        submission.workflow_image_url !==
                                                            null
                                                "
                                                rounded
                                                class="card-img-right"
                                                style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                                right
                                                :src="
                                                    submission.workflow_image_url
                                                "
                                            ></b-img>
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :to="{
                                                    name: 'submission',
                                                    params: {
                                                        owner: submission.owner,
                                                        name: submission.name
                                                    }
                                                }"
                                                replace
                                                >{{ submission.name }}</b-link
                                            >
                                            <br />
                                            <div
                                                v-if="
                                                    submission.tags !==
                                                        undefined &&
                                                        submission.tags.length >
                                                            0
                                                "
                                            >
                                                <b-badge
                                                    v-for="tag in submission.tags"
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
                                                v-if="!submission.is_complete"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'light'
                                                        : 'dark'
                                                "
                                            >
                                            </b-spinner>
                                            <small
                                                v-if="!submission.is_complete"
                                                >Running</small
                                            >
                                            <b-badge
                                                :variant="
                                                    submission.is_failure ||
                                                    submission.is_timeout
                                                        ? 'danger'
                                                        : submission.is_cancelled
                                                        ? 'secondary'
                                                        : 'success'
                                                "
                                                v-else
                                                >{{
                                                    submission.job_status
                                                }}</b-badge
                                            >
                                            <small> on </small>
                                            <b-badge
                                                class="ml-0 mr-0"
                                                variant="secondary"
                                                >{{ submission.agent }}</b-badge
                                            ><small>
                                                {{
                                                    prettify(submission.updated)
                                                }}</small
                                            >
                                            <br />
                                            <small
                                                v-if="
                                                    submission.workflow_name !==
                                                        null
                                                "
                                                class="mr-1"
                                                ><a
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    :href="
                                                        `https://github.com/${submission.workflow_owner}/${submission.workflow_name}`
                                                    "
                                                    ><i
                                                        class="fab fa-github fa-fw"
                                                    ></i>
                                                    {{
                                                        submission.workflow_owner
                                                    }}/{{
                                                        submission.workflow_name
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
                                >{{ submissionsSucceeded.length }}</b-badge
                            >
                            <b-badge
                                pill
                                class="ml-1 mr-1 mb-1"
                                variant="danger"
                                >{{ submissionsFailed.length }}</b-badge
                            >
                        </template>
                        <b-row>
                            <b-col
                                v-if="submissionsLoading"
                                class="m-0 pl-0 pr-0 text-center"
                            >
                                <b-spinner
                                    type="grow"
                                    variant="secondary"
                                ></b-spinner
                            ></b-col>
                            <b-col
                                v-if="
                                    !submissionsLoading &&
                                        submissionsCompleted.length === 0
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
                                    No workflow submissions.
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
                        <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                            ><b-col
                                v-if="
                                    !submissionsLoading && submissionsCompleted.length > 0
                                "
                                class="m-0 pl-0 pr-0 text-center"
                            >
                                <b-list-group class="text-left m-0 p-0">
                                    <b-list-group-item
                                        variant="default"
                                        style="box-shadow: -2px 2px 2px #adb5bd"
                                        v-for="submission in filteredCompleted"
                                        v-bind:key="submission.name"
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
                                                        submission.workflow_image_url !==
                                                            undefined &&
                                                            submission.workflow_image_url !==
                                                                null
                                                    "
                                                    rounded
                                                    class="card-img-right"
                                                    style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                                    right
                                                    :src="
                                                        submission.workflow_image_url
                                                    "
                                                ></b-img>
                                                <b-link
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    :to="{
                                                        name: 'submission',
                                                        params: {
                                                            owner:
                                                                submission.owner,
                                                            name:
                                                                submission.name
                                                        }
                                                    }"
                                                    replace
                                                    >{{
                                                        submission.name
                                                    }}</b-link
                                                >
                                            </b-col>
                                        </b-row>
                                        <b-row
                                            ><b-col>
                                                <div
                                                    v-if="
                                                        submission.tags !==
                                                            undefined &&
                                                            submission.tags
                                                                .length > 0
                                                    "
                                                >
                                                    <b-badge
                                                        v-for="tag in submission.tags"
                                                        v-bind:key="tag"
                                                        class="mr-1"
                                                        variant="secondary"
                                                        >{{ tag }}
                                                    </b-badge>
                                                    <br
                                                        v-if="
                                                            submission.tags
                                                                .length > 0
                                                        "
                                                    />
                                                </div>
                                                <small
                                                    v-if="
                                                        !submission.is_complete
                                                    "
                                                    >Running</small
                                                >
                                                <b-badge
                                                    :variant="
                                                        submission.is_failure ||
                                                        submission.is_timeout
                                                            ? 'danger'
                                                            : submission.is_cancelled
                                                            ? 'secondary'
                                                            : 'success'
                                                    "
                                                    v-else
                                                    >{{
                                                        submission.job_status
                                                    }}</b-badge
                                                >
                                                <small>
                                                    on
                                                </small>
                                                <b-badge
                                                    class="ml-0 mr-0"
                                                    variant="secondary"
                                                    >{{
                                                        submission.agent
                                                    }}</b-badge
                                                ><small>
                                                    {{
                                                        prettify(
                                                            submission.updated
                                                        )
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
                                                            `https://github.com/${submission.workflow_owner}/${submission.workflow_name}`
                                                        "
                                                        ><i
                                                            class="fab fa-github fa-fw"
                                                        ></i>
                                                        {{
                                                            submission.workflow_owner
                                                        }}/{{
                                                            submission.workflow_name
                                                        }}</a
                                                    >
                                                </small>
                                            </b-col>
                                            <b-col md="auto">
                                                <b-button
                                                    v-if="
                                                        submission.is_complete
                                                    "
                                                    variant="outline-danger"
                                                    size="sm"
                                                    v-b-tooltip.hover
                                                    title="Delete Run"
                                                    class="text-right"
                                                    @click="
                                                        showRemovePrompt(
                                                            submission
                                                        )
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
    name: 'submissions',
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
        showRemovePrompt(submission) {
            this.$bvModal.show('remove ' + submission.name);
        },
        async refresh() {
            await this.$store.dispatch('submissions/loadAll');
        },
        async remove(submission) {
            await axios
                .get(
                    `/apis/v1/submissions/${submission.owner}/${submission.name}/delete/`
                )
                .then(response => {
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                        this.$store.dispatch('submissions/loadAll');
                        if (
                            this.$router.currentRoute.name === 'submission' &&
                            submission.name ===
                                this.$router.currentRoute.params.name
                        )
                            router.push({
                                name: 'submissions'
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
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('submissions', [
            'submissions',
            'submissionsLoading',
            'submissionsRunning',
            'submissionsCompleted',
            'submissionsSucceeded',
            'submissionsFailed'
        ]),
        isRootPath() {
            return this.$route.name === 'submissions';
        },
        filteredRunning() {
            return this.submissionsRunning.filter(
                sub =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.searchText)) ||
                    (sub.name !== null && sub.name.includes(this.searchText)) ||
                    sub.tags.some(tag => tag.includes(this.searchText))
            );
        },
        filteredCompleted() {
            return this.submissionsCompleted.filter(
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
