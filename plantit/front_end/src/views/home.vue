<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <div v-if="profileLoading">
            <b-row align-v="center">
                <b-col class="text-center">
                    <b-img
                        :src="require('../assets/PlantITLoading.gif')"
                        style="transform: translate(0px, 150px); opacity: 0.1"
                    ></b-img>
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
                    ><i
                        class="fas fa-exclamation-circle fa-fw fa-3x text-warning"
                    ></i
                    ><br />
                    <h3 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Almost there!
                    </h3>
                    <br />
                    We need to link your
                    <i class="fab fa-github fa-fw fa-1x"></i
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
                    account.<br />Click the button below (or in the navigation
                    bar) to log in.<br /><br /><b-button
                        class="mt-1 text-left"
                        variant="warning"
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
            <b-container>
                <b-row
                    ><b-col
                        ><b-button
                            id="workflows-button"
                            block
                            class="m-1"
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            to="/home/workflows/"
                            ><i class="fas fa-stream fa-fw"></i>
                            Workflows</b-button
                        ><b-popover
                            :show.sync="profile.tutorials && isRootPath"
                            triggers="manual"
                            placement="bottom"
                            target="workflows-button"
                            title="Your Workflows"
                            >Click here to see explore and run public workflows,
                            or share your own.</b-popover
                        ></b-col
                    ><b-col
                        ><b-button
                            id="datasets-button"
                            block
                            class="m-1"
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            to="/home/datasets/"
                            ><i class="fas fa-database fa-fw"></i>
                            Datasets</b-button
                        ><b-popover
                            :show.sync="profile.tutorials && isRootPath"
                            triggers="manual"
                            placement="bottom"
                            target="datasets-button"
                            title="Your Datasets"
                            >Click here to view your data in the CyVerse Data
                            Store.</b-popover
                        ></b-col
                    ><b-col>
                        <b-button
                            id="agents-button"
                            block
                            class="m-1"
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            to="/home/agents/"
                            ><i class="fas fa-server fa-fw"></i>
                            Agents</b-button
                        ><b-popover
                            :show.sync="profile.tutorials && isRootPath"
                            triggers="manual"
                            placement="bottom"
                            target="agents-button"
                            title="Your Agents"
                            >Click here to view and manage servers, clusters,
                            and other computing resources.</b-popover
                        ></b-col
                    ><b-col
                        ><b-button
                            id="tasks-button"
                            block
                            class="m-1"
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            to="/home/tasks/"
                            ><i class="fas fa-tasks fa-fw"></i> Tasks</b-button
                        ><b-popover
                            :show.sync="profile.tutorials && isRootPath"
                            triggers="manual"
                            placement="bottom"
                            target="tasks-button"
                            title="Your Tasks"
                            >Click here to see your workflow submissions and
                            results.</b-popover
                        >
                    </b-col>
                    <b-col
                        ><b-button
                            id="miappe-button"
                            block
                            class="m-1"
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            to="/home/miappe/"
                            ><b-img
                          class="mb-1"
                                style="max-width: 18px"
                                :src="profile.darkMode ? require('../assets/miappe_icon.png') : require('../assets/miappe_icon_black.png')"
                            ></b-img>
                            MIAPPE</b-button
                        ><b-popover
                            :show.sync="profile.tutorials && isRootPath"
                            triggers="manual"
                            placement="bottom"
                            target="miappe-button"
                            title="Your MIAPPE metadata"
                            >Click here to see your MIAPPE metadata.</b-popover
                        >
                    </b-col>
                </b-row>
            </b-container>
            <b-row class="mt-2" v-if="!isRootPath"
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
                                <i class="fas fa-caret-right fa-fw fa-1x"></i>
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
            <b-row>
                <b-col
                    ><router-view
                        :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
                    ></router-view>
                    <div v-if="isRootPath" class="p-2">
                        <b-row>
                            <b-col>
                                <b-row align-v="start">
                                    <b-col>
                                        <b-row align-v="start">
                                            <b-col md="auto">
                                                <h2
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Welcome,
                                                    {{
                                                        profile.djangoProfile
                                                            .first_name
                                                            ? profile
                                                                  .djangoProfile
                                                                  .first_name
                                                            : profile
                                                                  .djangoProfile
                                                                  .username
                                                    }}
                                                </h2>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col md="auto">
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Workflows
                                                </h5>
                                                <b>{{
                                                    profile.stats
                                                        .owned_workflows.length
                                                }}</b>
                                                maintained
                                                <br />
                                                <b>{{
                                                    profile.stats.workflow_usage
                                                        .labels.length
                                                }}</b>
                                                used
                                            </b-col>
                                            <b-col md="auto">
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Datasets
                                                </h5>
                                                <i
                                                    class="fas fa-spinner"
                                                    v-if="
                                                        personalDatasetsLoading
                                                    "
                                                ></i
                                                ><b v-else>{{
                                                    personalDatasets.folders
                                                        .length
                                                }}</b>
                                                owned
                                                <br />
                                                <i
                                                    class="fas fa-spinner"
                                                    v-if="sharedDatasetsLoading"
                                                ></i
                                                ><b v-else>{{
                                                    sharedDatasets.folders
                                                        .length
                                                }}</b>
                                                shared with you
                                                <br />
                                                <i
                                                    class="fas fa-spinner"
                                                    v-if="
                                                        sharingDatasetsLoading
                                                    "
                                                ></i
                                                ><b v-else>{{
                                                    sharingDatasets.length
                                                }}</b>
                                                you've shared
                                            </b-col>
                                            <!--<b-col md="auto"><b-col md="auto"><Plotly
                                            v-if="
                                                profile.stats.used_datasets
                                                    .length > 0
                                            "
                                            :data="workflowPlotData"
                                            :layout="workflowPlotLayout"
                                        ></Plotly></b-col></b-col>-->
                                            <b-col md="auto">
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Agents
                                                </h5>
                                                <b>{{
                                                    profile.stats.owned_agents
                                                        .length
                                                }}</b>
                                                administered
                                                <br />
                                                <b>{{
                                                    profile.stats.guest_agents
                                                        .length
                                                }}</b>
                                                guest passes
                                                <br />
                                                <b>{{
                                                    profile.stats.agent_usage
                                                        .labels.length
                                                }}</b>
                                                used
                                            </b-col>
                                            <b-col md="auto">
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Tasks
                                                </h5>
                                                <b>{{ tasksRunning.length }}</b>
                                                running
                                                <br />
                                                <b>{{
                                                    tasksCompleted.length
                                                }}</b>
                                                completed
                                                <br />
                                                <b>{{
                                                    profile.stats.total_tasks
                                                }}</b>
                                                total
                                                <br />
                                                <b>{{
                                                    profile.stats
                                                        .total_task_results
                                                }}</b>
                                                results produced
                                                <br />
                                                <b>{{
                                                    prettifyDuration(
                                                        profile.stats
                                                            .total_task_seconds
                                                    )
                                                }}</b>
                                                cumulative runtime
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                    <b-col>
                                        <Plotly
                                            v-if="
                                                profile.stats.workflow_usage
                                                    .labels.length > 0
                                            "
                                            :data="workflowPlotData"
                                            :layout="workflowPlotLayout"
                                        ></Plotly>
                                    </b-col>
                                    <b-col>
                                        <Plotly
                                            v-if="
                                                profile.stats.agent_usage.labels
                                                    .length > 0
                                            "
                                            :data="agentPlotData"
                                            :layout="agentPlotLayout"
                                        ></Plotly>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col>
                                        <Plotly
                                            v-if="tasks.length > 0"
                                            :data="taskTimeseriesData"
                                            :layout="taskTimeseriesLayout"
                                        ></Plotly
                                    ></b-col>
                                </b-row>
                                <b-row>
                                    <div
                                        v-if="
                                            profile.stats.timeseries !==
                                                undefined
                                        "
                                    >
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
                                                    @click="
                                                        statsScope = 'Month'
                                                    "
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
                                        <div
                                            v-if="statsScope === 'Month'"
                                        ></div>
                                        <div
                                            v-if="statsScope === 'Year'"
                                        ></div></div
                                ></b-row> </b-col
                        ></b-row>
                    </div> </b-col
            ></b-row></div
    ></b-container>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import { Plotly } from 'vue-plotly';

export default {
    name: 'home',
    components: {
        Plotly
    },
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
    methods: {
        prettifyDuration: function(dur) {
            return moment.duration(dur, 'seconds').humanize();
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
        ...mapGetters('datasets', [
            'personalDatasets',
            'personalDatasetsLoading',
            'sharedDatasets',
            'sharedDatasetsLoading',
            'sharingDatasets',
            'sharingDatasetsLoading',
            'publicDatasets'
        ]),
        ...mapGetters('notifications', ['notifications']),
        ...mapGetters('workflows', [
            'boundWorkflows',
            'personalWorkflowsLoading'
        ]),
        isRootPath() {
            return this.$route.name === 'home';
        },
        workflowPlotData() {
            return [
                {
                    values: this.profile.stats.workflow_usage.values,
                    labels: this.profile.stats.workflow_usage.labels,
                    type: 'pie'
                }
            ];
        },
        workflowPlotLayout() {
            return {
                title: {
                    text: 'Workflow Usage Distribution',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        },
        agentPlotData() {
            return [
                {
                    values: this.profile.stats.agent_usage.values,
                    labels: this.profile.stats.agent_usage.labels,
                    type: 'pie'
                }
            ];
        },
        agentPlotLayout() {
            return {
                title: {
                    text: 'Agent Usage Distribution',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        },
        taskPlotData() {
            return [
                {
                    values: this.profile.stats.task_status.values,
                    labels: this.profile.stats.task_status.labels,
                    marker: {
                        colors: this.tasks.map(t =>
                            t.status === 'success'
                                ? 'rgb(214, 223, 93)'
                                : t.status === 'failure'
                                ? 'rgb(255, 114, 114)'
                                : 'rgb(128, 128, 128)'
                        )
                    },
                    type: 'pie'
                }
            ];
        },
        taskPlotLayout() {
            return {
                title: {
                    text: 'Task Status Distribution',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        },
        taskTimeseriesData() {
            return [
                {
                    x: this.tasks.map(t => t.created),
                    y: this.tasks.map(
                        t => `${t.workflow_owner}/${t.workflow_name}`
                    ),
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        color: this.tasks.map(t =>
                            t.status === 'success'
                                ? 'rgb(214, 223, 93)'
                                : t.status === 'failure'
                                ? 'rgb(255, 114, 114)'
                                : 'rgb(128, 128, 128)'
                        ),
                        line: {
                            color: 'rgba(156, 165, 196, 1.0)',
                            width: 1
                        },
                        symbol: 'circle',
                        size: 16
                    }
                }
            ];
        },
        taskTimeseriesLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                },
                autosize: true,
                title: {
                    text: 'Task History',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23'
                    }
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)'
                        }
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)'
                        }
                    }
                },
                yaxis: {
                    showticklabels: false
                },
                paper_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#1c1e23' : '#ffffff'
            };
        }
    }
};
</script>

<style scoped></style>
