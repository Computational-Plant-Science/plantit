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
        <div
            v-else-if="
                profile.loggedIn
                    ? profile.githubProfile === null ||
                      profile.githubProfile === undefined
                    : false
            "
        >
            <b-row align-v="center"
                ><b-col class="text-center" align-self="center"
                    ><i class="fas fa-exclamation-circle fa-fw fa-3x"></i><br />
                    <h3 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Almost there!
                    </h3>
                    <br />
                    To use
                    <b
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        style="text-decoration: underline;"
                    >
                        plant<small
                            class="mb-3 mr-1 text-success"
                            style="text-decoration: underline;text-shadow: 1px 0 0 #000, 0 -1px 0 #000, 0 1px 0 #000, -1px 0 0 #000;"
                            >IT</small
                        >
                    </b>
                    you'll need a <i class="fab fa-github fa-fw fa-1x"></i
                    ><b-img
                        class="m-0"
                        rounded
                        style="max-height: 1.2rem;"
                        :src="
                            profile.darkMode
                                ? require('../assets/logos/github_white.png')
                                : require('../assets/logos/github_black.png')
                        "
                    ></b-img>
                    account.<br />Once you have one, click the button
                    below (or in the navigation bar) to log in.<br /><br /><b-button
                        class="mt-1 text-left"
                        variant="success"
                        size="md"
                        href="/apis/v1/idp/github_request_identity/"
                    >
                        <i class="fab fa-github"></i>
                        Log in to GitHub
                    </b-button></b-col
                ></b-row
            >
        </div>
        <div v-else>
            <b-row
                ><b-col align-self="end"
                    ><b-breadcrumb
                        class="m-0 p-0"
                        style="background-color: transparent"
                    >
                        <b-breadcrumb-item
                            v-for="crumb in crumbs"
                            :key="crumb.text"
                            :to="crumb.href"
                            :disabled="crumb.text === 'tasks'"
                            class="m-0"
                        >
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                <i
                                    v-if="crumb.text !== 'Dashboard'"
                                    class="fas fa-caret-right fa-fw fa-1x"
                                ></i>
                                {{ crumb.text }}
                            </h5>
                        </b-breadcrumb-item>
                    </b-breadcrumb></b-col
                ><!--<b-col md="auto" align-self="end"
                    ><b :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Welcome, {{ profile.cyverseProfile.first_name }}.
                    </b></b-col
                >--></b-row
            >
            <b-row
                ><b-col md="auto" style="max-width: 15rem"
                    ><b-button
                        class="m-1 text-left"
                        block
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/dashboard/workflows/"
                        ><i class="fas fa-stream fa-fw"></i> Workflows</b-button
                    ><b-button
                        class="m-1 text-left"
                        block
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/dashboard/datasets/"
                        ><i class="fas fa-database fa-fw"></i>
                        Datasets</b-button
                    >
                    <b-button
                        class="m-1 text-left"
                        block
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/dashboard/agents/"
                        ><i class="fas fa-robot fa-fw"></i> Agents</b-button
                    ><b-button
                        class="m-1 text-left"
                        block
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/dashboard/tasks/"
                        ><i class="fas fa-tasks fa-fw"></i> Tasks</b-button
                    ></b-col
                ><b-col
                    ><router-view
                        :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
                    ></router-view>
                    <div v-if="isRootPath" class="p-2">
                        <b-row align-v="start">
                            <b-col md="auto">
                                <h2
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    Your usage summary
                                </h2>
                            </b-col></b-row
                        >
                        <b-row align-v="start">
                            <b-col md="auto">
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    Usage right now
                                </h5>
                                <b>{{ tasksRunning.length }}</b>
                                running
                                <div v-if="profile.stats !== null">
                                    <hr
                                        class="mt-2 mb-2"
                                        style="border-color: gray"
                                    />
                                    <h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        Cumulative usage
                                    </h5>
                                    <b>{{ profile.stats.total_tasks }}</b>
                                    tasks completed
                                    <br />
                                    <b>{{ profile.stats.total_time }}</b>
                                    working minutes
                                    <br />
                                    <b>{{ profile.stats.total_results }}</b>
                                    results produced
                                    <!--<hr />
                                            <h5>Most used</h5>
                                            Agent:
                                            <b>{{ stats.most_used_cluster }}</b>
                                            <br />
                                            Workflow:
                                            <b>{{ stats.most_used_dataset }}</b>
                                            <br />Most frequent collaborator:
                                            <b>{{
                                                stats.most_frequent_collaborator
                                            }}</b>-->
                                    <hr
                                        class="mt-2 mb-2"
                                        style="border-color: gray"
                                    />
                                    <h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        Usage in the past<b-dropdown
                                            class="ml-2 p-0"
                                            size="sm"
                                            dropright
                                            v-model="statsScope"
                                        >
                                            <template #button-content>
                                                {{ statsScope }}
                                            </template>
                                            <b-dropdown-item
                                                title="Hour"
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :link-class="
                                                    profile.darkMode
                                                        ? 'text-secondary'
                                                        : 'text-dark'
                                                "
                                                @click="statsScope = 'Hour'"
                                            >
                                                Hour </b-dropdown-item
                                            ><b-dropdown-item
                                                title="Day"
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :link-class="
                                                    profile.darkMode
                                                        ? 'text-secondary'
                                                        : 'text-dark'
                                                "
                                                @click="statsScope = 'Day'"
                                            >
                                                Day </b-dropdown-item
                                            ><b-dropdown-item
                                                title="Week"
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :link-class="
                                                    profile.darkMode
                                                        ? 'text-secondary'
                                                        : 'text-dark'
                                                "
                                                @click="statsScope = 'Week'"
                                            >
                                                Week
                                            </b-dropdown-item>
                                            <b-dropdown-item
                                                title="Month"
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :link-class="
                                                    profile.darkMode
                                                        ? 'text-secondary'
                                                        : 'text-dark'
                                                "
                                                @click="statsScope = 'Month'"
                                            >
                                                Month </b-dropdown-item
                                            ><b-dropdown-item
                                                title="Year"
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                :link-class="
                                                    profile.darkMode
                                                        ? 'text-secondary'
                                                        : 'text-dark'
                                                "
                                                @click="statsScope = 'Year'"
                                            >
                                                Year
                                            </b-dropdown-item></b-dropdown
                                        >
                                    </h5>
                                    <div v-if="statsScope === 'Hour'">
                                        TODO: hour data
                                    </div>
                                    <div v-if="statsScope === 'Day'"></div>
                                    <div v-if="statsScope === 'Week'"></div>
                                    <div v-if="statsScope === 'Month'"></div>
                                    <div
                                        v-if="statsScope === 'Year'"
                                    ></div></div></b-col
                        ></b-row>
                    </div> </b-col
            ></b-row></div
    ></b-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'dashboard',
    data: function() {
        return {
            crumbs: []
        };
    },
    created() {
        this.crumbs = this.$route.meta.crumb;
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        }
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('tasks', [
            'tasks',
            'tasksLoading',
            'tasksRunning',
            'tasksCompleted'
        ]),
        ...mapGetters('notifications', ['notifications']),
        ...mapGetters('workflows', [
            'connectedWorkflows',
            'personalWorkflowsLoading'
        ]),
        isRootPath() {
            return this.$route.name === 'dashboard';
        }
    }
};
</script>

<style scoped></style>
