<template>
    <b-container
        fluid
        class="m-0 mt-4 p-4"
        style="background-color: transparent"
    >
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
        <div v-else>
            <b-row>
                <b-col class="text-left" md="auto"
                    ><b-button
                        size="sm"
                        id="workflows-button"
                        block
                        class="m-1 text-left"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/home/workflows/"
                        ><i class="fas fa-stream fa-fw"></i> Workflows</b-button
                    ><b-popover
                        v-if="profile.hints && isRootPath"
                        triggers="hover"
                        placement="bottom"
                        target="workflows-button"
                        title="Your Workflows"
                        >Click here to explore and run workflows.</b-popover
                    ><b-button
                        size="sm"
                        id="datasets-button"
                        block
                        class="m-1 text-left"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/home/datasets/"
                        ><i class="fas fa-database fa-fw"></i>
                        Datasets</b-button
                    ><b-popover
                        v-if="profile.hints && isRootPath"
                        triggers="hover"
                        placement="bottom"
                        target="datasets-button"
                        title="Your Datasets"
                        >Click here to view your data in the CyVerse Data
                        Store.</b-popover
                    ><b-button
                        size="sm"
                        id="projects-button"
                        block
                        class="m-1 text-left"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/home/projects/"
                        ><b-img
                            class="mb-1"
                            style="max-width: 15px"
                            :src="
                                profile.darkMode
                                    ? require('../assets/miappe_icon.png')
                                    : require('../assets/miappe_icon_black.png')
                            "
                        ></b-img>
                        Projects</b-button
                    ><b-popover
                        v-if="profile.hints && isRootPath"
                        triggers="hover"
                        placement="bottom"
                        target="projects-button"
                        title="Your MIAPPE projects"
                        >Click here to see your MIAPPE projects and manage your
                        metadata.</b-popover
                    >
                    <b-button
                        size="sm"
                        id="agents-button"
                        block
                        class="m-1 text-left"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/home/agents/"
                        ><i class="fas fa-server fa-fw"></i> Agents</b-button
                    ><b-popover
                        v-if="profile.hints && isRootPath"
                        triggers="hover"
                        placement="bottom"
                        target="agents-button"
                        title="Your Agents"
                        >Click here to view and manage servers, clusters, and
                        other computing resources.</b-popover
                    ><b-button
                        size="sm"
                        id="tasks-button"
                        block
                        class="m-1 text-left"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/home/tasks/"
                        ><i class="fas fa-tasks fa-fw"></i> Tasks</b-button
                    ><b-popover
                        v-if="profile.hints && isRootPath"
                        triggers="hover"
                        placement="bottom"
                        target="tasks-button"
                        title="Your Tasks"
                        >Click here to see your workflow submissions and
                        results.</b-popover
                    >
                    <b-button
                        size="sm"
                        id="users-button"
                        block
                        class="m-1 text-left"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                        to="/home/users/"
                        ><i class="fas fa-user-friends fa-fw"></i>
                        Users</b-button
                    ><b-popover
                        v-if="profile.hints && isRootPath"
                        triggers="hover"
                        placement="bottom"
                        target="users-button"
                        title="Users"
                        >Click here to view the user registry.</b-popover
                    >
                </b-col>
                <b-col class="m-0 p-0"
                    ><b-row class="mt-2" v-if="!isRootPath"
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
                                    <small
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                    >
                                        <i
                                            class="fas fa-caret-right fa-fw fa-1x"
                                        ></i>
                                        {{ crumb.text }}
                                    </small>
                                </b-breadcrumb-item>
                            </b-breadcrumb></b-col
                        ></b-row
                    ><router-view
                        :class="
                            profile.darkMode
                                ? 'theme-dark m-0 p-1'
                                : 'theme-light m-0 p-1'
                        "
                    ></router-view>
                    <div v-if="isRootPath" class="p-2">
                        <b-row v-if="profile.stats !== null">
                            <b-col>
                                <b-row align-v="start">
                                    <b-col>
                                        <b-row align-v="start">
                                            <b-col md="auto">
                                                <h4
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Usage Summary
                                                </h4>
                                            </b-col>
                                        </b-row>
                                        <b-row>
                                            <b-col md="auto" class="mt-3">
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
                                                owned
                                                <br />
                                                <b>{{
                                                    profile.stats.workflow_usage
                                                        .labels.length
                                                }}</b>
                                                used
                                            </b-col>
                                            <b-col md="auto" class="mt-3">
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
                                                        userDatasets ===
                                                            undefined ||
                                                        userDatasets.folders ===
                                                            undefined
                                                    "
                                                ></i
                                                ><b v-else>{{
                                                    userDatasets.folders.length
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
                                            <b-col md="auto" class="mt-3">
                                                <h5
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    Projects
                                                </h5>
                                                <b>{{ userProjects.length }}</b>
                                                owned
                                                <br />
                                                <b>{{
                                                    othersProjects.length
                                                }}</b>
                                                guest
                                            </b-col>
                                            <b-col
                                                md="auto"
                                                class="mt-3"
                                                v-if="profile.stats !== null"
                                            >
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
                                                owned
                                                <br />
                                                <b>{{
                                                    profile.stats.guest_agents
                                                        .length
                                                }}</b>
                                                guest
                                                <br />
                                                <b>{{
                                                    profile.stats.agent_usage
                                                        .labels.length
                                                }}</b>
                                                used
                                            </b-col>
                                            <b-col md="auto" class="mt-3">
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
                                                    profile.stats.total_tasks
                                                }}</b>
                                                total
                                                <!--<br />
                                                <b>{{
                                                    profile.stats
                                                        .total_task_results
                                                }}</b>
                                                results produced-->
                                                <br />
                                                <b>{{
                                                    prettifyDuration(
                                                        profile.stats
                                                            .total_task_seconds
                                                    )
                                                }}</b>
                                                total runtime
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <hr />
                                <b-row align-v="start">
                                    <b-col md="auto">
                                        <h4
                                            :class="
                                                profile.darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            Recent Usage
                                        </h4>
                                    </b-col>
                                </b-row>
                                <div v-if="anyRecentUsageStats">
                                    <b-row>
                                        <b-col
                                            ><Plotly
                                                v-if="tasks.length > 0"
                                                :data="tasksStatusPlotTraces"
                                                :layout="tasksStatusPlotLayout"
                                            ></Plotly></b-col
                                        ><b-col>
                                            <Plotly
                                                v-if="showTasksUsagePlot"
                                                :data="tasksUsagePlotTraces"
                                                :layout="tasksUsagePlotLayout"
                                            ></Plotly> </b-col
                                    ></b-row>
                                    <br />
                                    <b-row
                                        ><b-col
                                            ><Plotly
                                                v-if="showWorkflowsUsagePlot"
                                                :data="workflowsUsagePlotTraces"
                                                :layout="
                                                    workflowsUsagePlotLayout
                                                "
                                            ></Plotly></b-col
                                    ></b-row>
                                    <br />
                                    <b-row
                                        ><b-col
                                            ><Plotly
                                                v-if="showAgentsUsagePlot"
                                                :data="agentsUsagePlotTraces"
                                                :layout="agentsUsagePlotLayout"
                                            ></Plotly></b-col
                                    ></b-row>
                                </div>
                                <b-row v-else
                                    ><b-col
                                        >You haven't run any tasks
                                        recently.</b-col
                                    ></b-row
                                >
                                <hr />
                                <b-row align-v="start">
                                    <b-col md="auto">
                                        <h4
                                            :class="
                                                profile.darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            Cumulative Usage
                                        </h4>
                                    </b-col>
                                </b-row>
                                <b-row v-if="anyCumulativeUsageStats">
                                    <b-col>
                                        <Plotly
                                            v-if="
                                                profile.stats.workflow_usage
                                                    .labels.length > 0
                                            "
                                            :data="workflowPieData"
                                            :layout="workflowPieLayout"
                                        ></Plotly>
                                    </b-col>
                                    <b-col>
                                        <Plotly
                                            v-if="
                                                profile.stats.agent_usage.labels
                                                    .length > 0
                                            "
                                            :data="agentPieTraces"
                                            :layout="agentPieLayout"
                                        ></Plotly></b-col
                                    ><b-col
                                        v-if="
                                            profile.stats.project_usage.labels
                                                .length > 0
                                        "
                                    >
                                        <Plotly
                                            v-if="
                                                profile.stats.project_usage
                                                    .labels.length > 0
                                            "
                                            :data="projectPieData"
                                            :layout="projectPieLayout"
                                        ></Plotly> </b-col
                                ></b-row>
                                <b-row v-else
                                    ><b-col
                                        >You haven't run any tasks yet.</b-col
                                    ></b-row
                                >
                            </b-col>
                        </b-row>
                    </div>
                </b-col></b-row
            >
        </div></b-container
    >
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import { Plotly } from 'vue-plotly';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'home',
    components: {
        Plotly,
    },
    data: function () {
        return {
            crumbs: [],
            timeseriesTasksUsage: null,
            timeseriesWorkflowsUsage: null,
            timeseriesAgentsUsage: null,
        };
    },
    async created() {
        this.crumbs = this.$route.meta.crumb;
        await this.loadUserTimeseries();
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        },
    },
    methods: {
        prettifyDuration: function (dur) {
            return moment.duration(dur, 'seconds').humanize();
        },
        async loadUserTimeseries() {
            await axios
                .get(`/apis/v1/stats/user_timeseries/`)
                .then((response) => {
                    // set timeseries traces
                    this.timeseriesTasksUsage = {
                        x: Object.keys(response.data.tasks_usage).map((key) =>
                            moment(key).format('YYYY-MM-DD HH:mm:ss')
                        ),
                        y: Object.values(response.data.tasks_usage),
                        type: 'line',
                        mode: 'lines',
                        fill: 'tozeroy',
                        line: { color: '#d6df5D', shape: 'spline', },
                        connectgaps: true,
                        colorscale: 'Greens',
                    };
                    this.timeseriesWorkflowsUsage = Object.fromEntries(
                        Object.entries(response.data.workflows_usage).map(
                            ([k, v]) => [
                                k,
                                {
                                    x: Object.keys(v).map((key) =>
                                        moment(key).format(
                                            'YYYY-MM-DD HH:mm:ss'
                                        )
                                    ),
                                    y: Object.values(v),
                                    name: k,
                                    type: 'line',
                                    mode: 'lines',
                                    fill: 'tozeroy',
                                    line: { shape: 'spline', },
                                    connectgaps: true,
                                    stackgroup: 'one'
                                },
                            ]
                        )
                    );
                    this.timeseriesAgentsUsage = Object.fromEntries(
                        Object.entries(response.data.agents_usage).map(
                            ([k, v]) => [
                                k,
                                {
                                    x: Object.keys(v).map((key) =>
                                        moment(key).format(
                                            'YYYY-MM-DD HH:mm:ss'
                                        )
                                    ),
                                    y: Object.values(v),
                                    name: k,
                                    type: 'line',
                                    mode: 'lines',
                                    fill: 'tozeroy',
                                    line: { shape: 'spline', },
                                    connectgaps: true,
                                    colorscale: 'Greens',
                                },
                            ]
                        )
                    );
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (
                        error.response !== undefined &&
                        error.response.status === 500
                    )
                        throw error;
                });
        },
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('tasks', [
            'tasks',
            'tasksLoading',
            'tasksRunning',
            'tasksCompleted',
        ]),
        ...mapGetters('datasets', [
            'userDatasets',
            'userDatasetsLoading',
            'sharedDatasets',
            'sharedDatasetsLoading',
            'sharingDatasets',
            'sharingDatasetsLoading',
            'publicDatasets',
        ]),
        ...mapGetters('notifications', ['notifications']),
        ...mapGetters('workflows', ['userWorkflows', 'userWorkflowsLoading']),
        ...mapGetters('projects', ['userProjects', 'othersProjects']),
        isRootPath() {
            return this.$route.name === 'home';
        },
        anyRecentUsageStats() {
            return (
                (this.timeseriesTasksUsage !== null &&
                    this.timeseriesTasksUsage.x.length > 1) ||
                (this.timeseriesWorkflowsUsage !== null &&
                    Object.keys(this.timeseriesWorkflowsUsage).length > 1) ||
                (this.timeseriesAgentsUsage !== null &&
                    Object.keys(this.timeseriesAgentsUsage).length > 1)
            );
        },
        anyCumulativeUsageStats() {
            return (
                this.profile.stats.workflow_usage.labels.length > 0 ||
                this.profile.stats.agent_usage.labels.length > 0 ||
                this.profile.stats.project_usage.labels.length > 0
            );
        },
        pieColors() {
          return [
                          'rgb(146, 123, 21)', 'rgb(177, 180, 34)', 'rgb(206, 206, 40)', 'rgb(175, 51, 21)', 'rgb(35, 36, 21)',
                          'rgb(177, 127, 38)', 'rgb(205, 152, 36)', 'rgb(99, 79, 37)', 'rgb(129, 180, 179)', 'rgb(124, 103, 37)',
                          'rgb(33, 75, 99)', 'rgb(79, 129, 102)', 'rgb(151, 179, 100)', 'rgb(175, 49, 35)', 'rgb(36, 73, 147)',
                          'rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)', 'rgb(36, 55, 57)', 'rgb(6, 4, 4)'
          ];
        },
        workflowPieData() {
            return [
                {
                    values: this.profile.stats.workflow_usage.values,
                    labels: this.profile.stats.workflow_usage.labels,
                    type: 'pie',
                    marker: {
                      colors: this.pieColors
                    }
                },
            ];
        },
        workflowPieLayout() {
            return {
                title: {
                    text: 'Workflows',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                autosize: true,
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                showlegend: false,
                height: 350,
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
        agentPieTraces() {
            return [
                {
                    values: this.profile.stats.agent_usage.values,
                    labels: this.profile.stats.agent_usage.labels,
                    type: 'pie',
                    marker: {
                      colors: this.pieColors
                    }
                },
            ];
        },
        agentPieLayout() {
            return {
                title: {
                    text: 'Agents',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                autosize: true,
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                showlegend: false,
                height: 350,
                piecolorway: 'Greens',
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
        projectPieData() {
            return [
                {
                    values: this.profile.stats.project_usage.values,
                    labels: this.profile.stats.project_usage.labels,
                    type: 'pie',
                    marker: {
                      colors: this.pieColors
                    }
                },
            ];
        },
        projectPieLayout() {
            return {
                title: {
                    text: 'Projects',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                autosize: true,
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                showlegend: false,
                height: 350,
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
        tasksStatusPlotTraces() {
            return [
                {
                    x: this.tasks.map((t) =>
                        moment(t.created).format('YYYY-MM-DD HH:mm:ss')
                    ),
                    y: this.tasks.map(
                        (t) => `${t.workflow_owner}/${t.workflow_name}`
                    ),
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        color: this.tasks.map((t) =>
                            t.status === 'success'
                                ? 'rgb(214, 223, 93)'
                                : t.status === 'failure'
                                ? 'rgb(255, 114, 114)'
                                : 'rgb(128, 128, 128)'
                        ),
                        line: {
                            color: 'rgba(156, 165, 196, 1.0)',
                            width: 1,
                        },
                        symbol: 'circle',
                        size: 16,
                    },
                },
            ];
        },
        tasksStatusPlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                title: {
                    text: 'Task Status',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)',
                        },
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)',
                        },
                    },
                },
                yaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    showticklabels: false,
                    autotick: false
                },
                height: 300,
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
        showTasksUsagePlot() {
            return (
                this.timeseriesTasksUsage !== null &&
                this.timeseriesTasksUsage.x.length > 1
            );
        },
        tasksUsagePlotTraces() {
            return [this.timeseriesTasksUsage];
        },
        tasksUsagePlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                hovermode: false,
                title: {
                    text: 'Task Usage',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)',
                        },
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)',
                        },
                    },
                },
                yaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    showticklabels: false,
                    autotick: false
                },
                height: 300,
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
        showWorkflowsUsagePlot() {
            return (
                this.timeseriesWorkflowsUsage !== null &&
                Object.keys(this.timeseriesWorkflowsUsage).length > 1
            );
        },
        workflowsUsagePlotTraces() {
          return Object.values(this.timeseriesWorkflowsUsage);
        },
        workflowsUsagePlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                hovermode: false,
                title: {
                    text: 'Workflows',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    // orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)',
                        },
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)',
                        },
                    },
                },
                yaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    showticklabels: false,
                    autotick: false
                },
                height: 300,
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
        showAgentsUsagePlot() {
            return (
                this.timeseriesAgentsUsage !== null &&
                Object.keys(this.timeseriesAgentsUsage).length > 1
            );
        },
        agentsUsagePlotTraces() {
            return Object.values(this.timeseriesAgentsUsage);
        },
        agentsUsagePlotLayout() {
            return {
                font: {
                    color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                },
                autosize: true,
                hovermode: false,
                title: {
                    text: 'Agents',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                legend: {
                    // orientation: 'h',
                    font: {
                        color: this.profile.darkMode ? '#ffffff' : '#1c1e23',
                    },
                },
                xaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    linecolor: 'rgb(102, 102, 102)',
                    titlefont: {
                        font: {
                            color: 'rgb(204, 204, 204)',
                        },
                    },
                    tickfont: {
                        font: {
                            color: 'rgb(102, 102, 102)',
                        },
                    },
                },
                yaxis: {
                    showgrid: false,
                    showline: true,
                    zeroline: false,
                    showticklabels: false,
                    autotick: false
                },
                height: 300,
                paper_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
                plot_bgcolor: this.profile.darkMode ? '#212529' : '#ffffff',
            };
        },
    },
};
</script>

<style scoped></style>
