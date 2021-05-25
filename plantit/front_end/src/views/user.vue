<template>
    <div class="w-100 h-100 pl-3" style="background-color: transparent">
        <br />
        <br />
        <b-container class="p-3 vl" fluid>
            <div v-if="profileLoading">
                <br />
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
                    !(
                        userProfile === null ||
                        userProfile === undefined ||
                        userProfile.githubProfile === null ||
                        userProfile.githubProfile === undefined
                    )
                "
            >
                <b-row
                    ><b-col
                        ><h1
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Welcome, {{ userProfile.cyverseProfile.first_name }}
                        </h1></b-col
                    ></b-row
                >
                <hr class="mt-2 mb-2" style="border-color: gray" />
                <b-row align-v="center" class="mt-3"
                    ><b-col>
                        <b-tabs
                            pills
                            vertical
                            content-class="mt-2 mr-3"
                            v-model="currentTab"
                            :active-nav-item-class="
                                profile.darkMode ? 'bg-dark' : 'bg-secondary'
                            "
                        >
                            <b-tab
                                title="Dashboard"
                                v-if="userProfile.djangoProfile"
                                active
                                ><template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Dashboard</b
                                    > </template
                                ><b-row
                                    ><b-col
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Dashboard
                                        </h2></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"/>
                                <b-row align-v="start" class="mb-2">
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
                                        <b>{{ runningRuns.length }}</b>
                                        running workflows
                                        <br />
                                        <b>{{ unreadNotifications.length }}</b>
                                        unread notifications
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
                                            <b>{{
                                                profile.stats.total_runs
                                            }}</b>
                                            workflows run
                                            <br />
                                            <b>{{
                                                profile.stats.total_time
                                            }}</b>
                                            working minutes
                                            <br />
                                            <b>{{
                                                profile.stats.total_results
                                            }}</b>
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
                                                        @click="
                                                            statsScope = 'Hour'
                                                        "
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
                                                        @click="
                                                            statsScope = 'Day'
                                                        "
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
                                                        @click="
                                                            statsScope = 'Week'
                                                        "
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
                                                        @click="
                                                            statsScope = 'Year'
                                                        "
                                                    >
                                                        Year
                                                    </b-dropdown-item></b-dropdown
                                                >
                                            </h5>
                                            <div v-if="statsScope === 'Hour'">
                                                TODO: hour data
                                            </div>
                                            <div
                                                v-if="statsScope === 'Day'"
                                            ></div>
                                            <div
                                                v-if="statsScope === 'Week'"
                                            ></div>
                                            <div
                                                v-if="statsScope === 'Month'"
                                            ></div>
                                            <div
                                                v-if="statsScope === 'Year'"
                                            ></div></div></b-col></b-row
                            ></b-tab>
                            <b-tab
                                v-if="
                                    profile.djangoProfile.username ===
                                        $router.currentRoute.params.username
                                "
                            >
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Datasets</b
                                    >
                                </template>
                                <b-row
                                    ><b-col
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Datasets
                                        </h2></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"
                                />
                                <b-tabs
                                    nav-class="bg-transparent"
                                    active-nav-item-class="bg-secondary text-dark"
                                    pills
                                >
                                    <b-tab
                                        :title-link-class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark m-0 p-3'
                                                : 'theme-light m-0 p-3'
                                        "
                                    >
                                        <template #title>
                                            <b>Yours</b>
                                        </template>
                                        <b-row class="mt-2"
                                            ><b-col
                                                >Your own datasets.</b-col
                                            ></b-row
                                        >
                                        <!--<b-row class="mb-2"
                                            ><b-col>
                                                <b-input-group size="sm">
                                                    <template #prepend>
                                                        <b-input-group-text>
                                                            Search
                                                        </b-input-group-text></template
                                                    ><b-form-input
                                                        :class="
                                                            profile.darkMode
                                                                ? 'theme-search-dark'
                                                                : 'theme-search-light'
                                                        "
                                                        size="lg"
                                                        type="search"
                                                        v-model="
                                                            yourDatasetsSearchText
                                                        "
                                                    ></b-form-input></b-input-group></b-col
                                        ></b-row>-->
                                        <b-row>
                                            <b-col>
                                                <datatree
                                                    :node="data"
                                                    select="directory"
                                                    :upload="true"
                                                    :download="true"
                                                    :agents="agents"
                                                    :class="
                                                        profile.darkMode
                                                            ? 'theme-dark'
                                                            : 'theme-light'
                                                    "
                                                ></datatree></b-col></b-row
                                    ></b-tab>
                                    <b-tab
                                        :title-link-class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark m-0 p-3'
                                                : 'theme-light m-0 p-3'
                                        "
                                    >
                                        <template #title>
                                            <b>Shared</b>
                                        </template>
                                        <b-row class="mt-2"
                                            ><b-col
                                                >Datasets shared with
                                                you.</b-col
                                            ></b-row
                                        >
                                        <!--<b-row class="mb-2"
                                            ><b-col>
                                                <b-input-group>
                                                    <template #prepend>
                                                        <b-input-group-text>
                                                            Search
                                                        </b-input-group-text></template
                                                    ><b-form-input
                                                        :class="
                                                            profile.darkMode
                                                                ? 'theme-search-dark'
                                                                : 'theme-search-light'
                                                        "
                                                        size="lg"
                                                        type="search"
                                                        v-model="
                                                            sharedDatasetsSearchText
                                                        "
                                                    ></b-form-input></b-input-group></b-col
                                        ></b-row>-->
                                        <b-row>
                                            <b-col>
                                                <datatree
                                                    :node="sharedDatasets"
                                                    select="directory"
                                                    :agents="agents"
                                                    :upload="true"
                                                    :download="true"
                                                    :class="
                                                        profile.darkMode
                                                            ? 'theme-dark'
                                                            : 'theme-light'
                                                    "
                                                ></datatree></b-col></b-row
                                    ></b-tab>
                                    <b-tab
                                        :title-link-class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark m-0 p-3'
                                                : 'theme-light m-0 p-3'
                                        "
                                    >
                                        <template #title>
                                            <b>Sharing</b>
                                        </template>
                                        <b-row class="mt-2"
                                            ><b-col
                                                >Datasets you're sharing with
                                                others.</b-col
                                            ></b-row
                                        >
                                        <!--<b-row class="mb-2"
                                            ><b-col>
                                                <b-input-group>
                                                    <template #prepend>
                                                        <b-input-group-text>
                                                            Search
                                                        </b-input-group-text></template
                                                    ><b-form-input
                                                        :class="
                                                            profile.darkMode
                                                                ? 'theme-search-dark'
                                                                : 'theme-search-light'
                                                        "
                                                        size="lg"
                                                        type="search"
                                                        v-model="
                                                            sharingDatasetsSearchText
                                                        "
                                                    ></b-form-input></b-input-group></b-col
                                        ></b-row>-->
                                        <b-row v-if="alertEnabled">
                                            <b-col class="m-0 p-0">
                                                <b-alert
                                                    :show="alertEnabled"
                                                    :variant="
                                                        alertMessage.startsWith(
                                                            'Failed'
                                                        )
                                                            ? 'danger'
                                                            : 'success'
                                                    "
                                                    dismissible
                                                    @dismissed="
                                                        alertEnabled = false
                                                    "
                                                >
                                                    {{ alertMessage }}
                                                </b-alert>
                                            </b-col>
                                        </b-row>
                                        <b-row
                                            v-for="directory in sharingDatasets"
                                            v-bind:key="directory.path"
                                        >
                                            <b-col
                                                ><small>{{
                                                    directory.path
                                                }}</small></b-col
                                            ><b-col md="auto" class="mt-1">
                                                <small
                                                    >Shared with
                                                    {{ directory.guest }}</small
                                                ></b-col
                                            ><b-col md="auto">
                                                <b-button
                                                    class="mb-2"
                                                    size="sm"
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'outline-dark'
                                                    "
                                                    @click="
                                                        unshareDataset(
                                                            directory
                                                        )
                                                    "
                                                    ><i
                                                        class="fas fa-user-lock fa-fw"
                                                    ></i>
                                                    Unshare</b-button
                                                ></b-col
                                            ></b-row
                                        >
                                        <b-row
                                            v-if="sharingDatasets.length === 0"
                                            ><b-col
                                                ><p>
                                                    <small class="text-danger"
                                                        >You haven't shared any
                                                        datasets with
                                                        anyone.</small
                                                    >
                                                </p></b-col
                                            ></b-row
                                        >
                                    </b-tab>
                                </b-tabs>
                            </b-tab>
                            <b-tab>
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Workflows</b
                                    >
                                </template>
                                <b-row
                                    ><b-col md="auto"
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Workflows
                                        </h2></b-col
                                    ><b-col
                                        md="auto"
                                        class="ml-0"
                                        align-self="middle"
                                        ><b-button
                                            :disabled="workflowsLoading"
                                            :variant="
                                                profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            size="md"
                                            v-b-tooltip.hover
                                            title="Refresh workflows"
                                            @click="refreshWorkflows"
                                            class="ml-0 mt-0 mr-0"
                                        >
                                            <b-spinner
                                                small
                                                v-if="workflowsLoading"
                                                label="Refreshing..."
                                                :variant="
                                                    profile.darkMode
                                                        ? 'light'
                                                        : 'dark'
                                                "
                                                class="mr-1"
                                            ></b-spinner
                                            ><i
                                                v-else
                                                class="fas fa-redo mr-1"
                                            ></i
                                            >Refresh</b-button
                                        ></b-col
                                    ><b-col class="ml-0" align-self="middle"
                                        ><b-button
                                            :disabled="workflowsLoading"
                                            :variant="
                                                profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            size="md"
                                            v-b-tooltip.hover
                                            title="Connect a new workflow"
                                            @click="showConnectWorkflowModal"
                                            class="ml-0 mt-0 mr-0"
                                        >
                                            <b-spinner
                                                small
                                                v-if="workflowsLoading"
                                                label="Connecting..."
                                                :variant="
                                                    profile.darkMode
                                                        ? 'light'
                                                        : 'dark'
                                                "
                                                class="mr-1"
                                            ></b-spinner
                                            ><i
                                                v-else
                                                class="fas fa-plug mr-1"
                                            ></i
                                            >Connect</b-button
                                        ></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"
                                />
                                <b-row
                                    v-if="profile.githubProfile === null"
                                    align-v="center"
                                >
                                    <b-col md="auto" class="mr-2 pr-0">
                                        <b-button
                                            variant="success"
                                            href="/apis/v1/users/github_request_identity/"
                                            class="mr-0"
                                        >
                                            <i class="fab fa-github"></i>
                                            Log in to GitHub
                                        </b-button>
                                    </b-col>
                                    <b-col md="auto" class="ml-0 pl-0">
                                        <b
                                            class="text-center align-center ml-0 pl-0"
                                            >to load workflows.</b
                                        >
                                    </b-col>
                                </b-row>
                                <b-row
                                    v-if="
                                        userWorkflows.length === 0 &&
                                            !workflowsLoading
                                    "
                                    ><b-col
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >No workflows to show!</b-col
                                    ></b-row
                                >
                                <b-row
                                    v-else-if="
                                        userProfile.githubProfile &&
                                            profile.djangoProfile
                                                .github_token !== undefined
                                    "
                                >
                                    <b-col
                                        ><workflows
                                            class="m-1"
                                            :github-user="
                                                profile.githubProfile.login
                                            "
                                            :github-token="
                                                profile.djangoProfile
                                                    .github_token
                                            "
                                            :workflows="userWorkflows"
                                        >
                                        </workflows>
                                    </b-col>
                                </b-row>
                            </b-tab>
                            <b-tab
                                v-if="
                                    profile.djangoProfile.username ===
                                        $router.currentRoute.params.username
                                "
                            >
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Agents</b
                                    >
                                </template>
                                <b-row
                                    ><b-col
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Agents
                                        </h2></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"
                                />
                                <div>
                                    <b-row v-if="agentsLoading">
                                        <b-spinner
                                            type="grow"
                                            label="Loading..."
                                            variant="secondary"
                                        ></b-spinner>
                                    </b-row>
                                    <b-row class="text-left">
                                        <b-col>
                                            See
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                to="/agents"
                                                ><i
                                                    class="fas fa-server fa-1x fa-fw"
                                                ></i>
                                                Agents</b-link
                                            >
                                            to request guest access to public
                                            servers, clusters, or
                                            supercomputers, or
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                @click="showConnectAgentModal"
                                                ><i
                                                    class="fas fa-plus fa-1x fa-fw"
                                                ></i>
                                                connect a new agent</b-link
                                            >.
                                            <br />
                                            <b
                                                class="text-danger"
                                                v-if="
                                                    !agentsLoading &&
                                                        agents.length === 0
                                                "
                                                >You don't have access to any
                                                agents yet.</b
                                            >
                                        </b-col>
                                    </b-row>
                                    <b-card-group
                                        v-if="
                                            !agentsLoading &&
                                                agents.length !== 0
                                        "
                                        deck
                                        columns
                                        class="justify-content-center mt-3"
                                    >
                                        <b-card
                                            v-for="agent in agents"
                                            v-bind:key="agent.name"
                                            :bg-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            :header-bg-variant="
                                                profile.darkMode
                                                    ? 'dark'
                                                    : 'white'
                                            "
                                            border-variant="default"
                                            :header-border-variant="
                                                profile.darkMode
                                                    ? 'secondary'
                                                    : 'default'
                                            "
                                            :text-variant="
                                                profile.darkMode
                                                    ? 'white'
                                                    : 'dark'
                                            "
                                            style="min-width: 30rem;"
                                            class="overflow-hidden mb-4"
                                        >
                                            <b-row style="z-index: 10">
                                                <b-col cols="10">
                                                    <h2>
                                                        <b-link
                                                            :class="
                                                                profile.darkMode
                                                                    ? 'text-white'
                                                                    : 'text-dark'
                                                            "
                                                            variant="outline-dark"
                                                            v-b-tooltip.hover
                                                            @click="
                                                                goToAgent(agent)
                                                            "
                                                        >
                                                            {{ agent.name }}
                                                        </b-link>
                                                    </h2>
                                                    <b-badge
                                                        v-if="!agent.public"
                                                        class="mr-1"
                                                        variant="info"
                                                        ><i
                                                            class="fas fa-lock fa-fw"
                                                        ></i>
                                                        Private</b-badge
                                                    >
                                                    <b-badge
                                                        v-else
                                                        variant="success"
                                                        class="mr-1"
                                                        ><i
                                                            class="fas fa-lock-open fa-fw"
                                                        ></i>
                                                        Public</b-badge
                                                    >
                                                    <b-badge
                                                        variant="warning"
                                                        >{{
                                                            agent.role === 'own'
                                                                ? 'Owner'
                                                                : 'Guest'
                                                        }}</b-badge
                                                    >

                                                    <br />
                                                    <small>
                                                        {{ agent.description }}
                                                    </small>
                                                    <br />
                                                </b-col>
                                                <b-col cols="1"></b-col>
                                            </b-row>
                                            <b-img
                                                v-if="agent.logo"
                                                rounded
                                                class="card-img-right overflow-hidden"
                                                style="max-height: 4rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                                right
                                                :src="agent.logo"
                                            ></b-img>
                                            <i
                                                v-else
                                                style="max-width: 7rem;position: absolute;right: 20px;top: 20px;"
                                                right
                                                class="card-img-left fas fa-server fa-2x fa-fw"
                                            ></i>
                                        </b-card>
                                    </b-card-group>
                                </div>
                            </b-tab>
                            <b-tab
                                v-if="userProfile.djangoProfile"
                                title="Runs"
                            >
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Runs</b
                                    >
                                </template>
                                <b-row
                                    ><b-col
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Runs
                                        </h2></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"
                                />
                                <b-tabs
                                    nav-class="bg-transparent"
                                    active-nav-item-class="bg-secondary text-dark"
                                    pills
                                >
                                    <b-tab
                                        :title-link-class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark m-0 p-3'
                                                : 'theme-light m-0 p-3'
                                        "
                                    >
                                        <template #title>
                                            <b>Running</b>
                                        </template>
                                        <b-row class="m-3 mb-1 pl-0 pr-0"
                                            ><b-col class="m-0 pl-0 pr-0">
                                                <b-list-group
                                                    v-if="
                                                        runningRuns.length > 0
                                                    "
                                                    class="text-left m-0 p-0"
                                                >
                                                    <b-list-group-item
                                                        variant="default"
                                                        style="box-shadow: -2px 2px 2px #adb5bd"
                                                        v-for="run in filteredRunningRuns"
                                                        v-bind:key="run.id"
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                                                : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                                        "
                                                        :to="{
                                                            name: 'run',
                                                            params: {
                                                                id: run.id
                                                            }
                                                        }"
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
                                                                    id: run.id
                                                                }
                                                            }"
                                                            replace
                                                            >{{
                                                                run.id
                                                            }}</b-link
                                                        >
                                                        <br />
                                                        <div
                                                            v-if="
                                                                run.tags !==
                                                                    undefined &&
                                                                    run.tags
                                                                        .length >
                                                                        0
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
                                                            v-if="
                                                                !run.is_complete
                                                            "
                                                            :variant="
                                                                profile.darkMode
                                                                    ? 'light'
                                                                    : 'dark'
                                                            "
                                                        >
                                                        </b-spinner>
                                                        <small
                                                            v-if="
                                                                !run.is_complete
                                                            "
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
                                                        <small> on </small>
                                                        <b-badge
                                                            class="ml-0 mr-0"
                                                            variant="secondary"
                                                            >{{
                                                                run.agent
                                                            }}</b-badge
                                                        ><small>
                                                            {{
                                                                prettify(
                                                                    run.updated
                                                                )
                                                            }}</small
                                                        >
                                                        <br />
                                                        <small
                                                            v-if="
                                                                run.workflow_name !==
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
                                                    </b-list-group-item>
                                                </b-list-group>
                                                <p
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    v-if="
                                                        runningRuns.length === 0
                                                    "
                                                >
                                                    No workflows are running
                                                    right now.
                                                </p>
                                                <b-input-group
                                                    v-else
                                                    size="sm"
                                                    style="bottom: 4px"
                                                    ><template #prepend>
                                                        <b-input-group-text
                                                            ><i
                                                                class="fas fa-search"
                                                            ></i
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
                                                </b-input-group> </b-col
                                        ></b-row>
                                    </b-tab>
                                    <b-tab
                                        :title-link-class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :class="
                                            profile.darkMode
                                                ? 'theme-dark m-0 p-3'
                                                : 'theme-light m-0 p-3'
                                        "
                                    >
                                        <template #title>
                                            <b>Completed</b>
                                        </template>
                                        <b-row
                                            class="m-3 mb-1 pl-0 pr-0"
                                            align-v="center"
                                            ><b-col
                                                v-if="
                                                    !runsLoading &&
                                                        completedRuns.length > 0
                                                "
                                                class="m-0 pl-0 pr-0 text-center"
                                            >
                                                <b-list-group
                                                    class="text-left m-0 p-0"
                                                >
                                                    <b-list-group-item
                                                        variant="default"
                                                        style="box-shadow: -2px 2px 2px #adb5bd"
                                                        v-for="run in filteredCompletedRuns"
                                                        v-bind:key="run.id"
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
                                                                        name:
                                                                            'run',
                                                                        params: {
                                                                            id:
                                                                                run.id
                                                                        }
                                                                    }"
                                                                    replace
                                                                    >{{
                                                                        run.id
                                                                    }}</b-link
                                                                >
                                                            </b-col>
                                                        </b-row>
                                                        <b-row
                                                            ><b-col>
                                                                <div
                                                                    v-if="
                                                                        run.tags !==
                                                                            undefined &&
                                                                            run
                                                                                .tags
                                                                                .length >
                                                                                0
                                                                    "
                                                                >
                                                                    <b-badge
                                                                        v-for="tag in run.tags"
                                                                        v-bind:key="
                                                                            tag
                                                                        "
                                                                        class="mr-1"
                                                                        variant="secondary"
                                                                        >{{
                                                                            tag
                                                                        }}
                                                                    </b-badge>
                                                                    <br
                                                                        v-if="
                                                                            run
                                                                                .tags
                                                                                .length >
                                                                                0
                                                                        "
                                                                    />
                                                                </div>
                                                                <small
                                                                    v-if="
                                                                        !run.is_complete
                                                                    "
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
                                                                    >{{
                                                                        run.agent
                                                                    }}</b-badge
                                                                ><small>
                                                                    {{
                                                                        prettify(
                                                                            run.updated
                                                                        )
                                                                    }}</small
                                                                >
                                                            </b-col>
                                                        </b-row>
                                                        <b-row
                                                            ><b-col>
                                                                <small
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
                                                                    v-if="
                                                                        run.is_complete
                                                                    "
                                                                    variant="outline-danger"
                                                                    size="sm"
                                                                    v-b-tooltip.hover
                                                                    title="Delete Run"
                                                                    class="text-right"
                                                                    @click="
                                                                        showDeleteRunPrompt(
                                                                            run
                                                                        )
                                                                    "
                                                                >
                                                                    <i
                                                                        class="fas fa-trash"
                                                                    ></i>
                                                                    Delete
                                                                </b-button>
                                                            </b-col></b-row
                                                        >
                                                    </b-list-group-item>
                                                </b-list-group>
                                            </b-col>
                                            <b-col
                                                v-if="
                                                    runsLoading ||
                                                        loadingMoreRuns
                                                "
                                                class="m-0 pl-0 pr-0 text-center"
                                            >
                                                <b-spinner
                                                    type="grow"
                                                    variant="secondary"
                                                ></b-spinner
                                            ></b-col>
                                            <b-col
                                                v-if="
                                                    !runsLoading &&
                                                        completedRuns.length ===
                                                            0
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
                                                    You haven't run any
                                                    workflows yet.
                                                </p>
                                            </b-col>
                                            <b-col
                                                v-else
                                                class="m-0 pl-0 pr-0 text-center"
                                                ><b-input-group
                                                    size="sm"
                                                    style="bottom: 4px"
                                                    ><template #prepend>
                                                        <b-input-group-text
                                                            ><i
                                                                class="fas fa-search"
                                                            ></i
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
                                        </b-row> </b-tab
                                ></b-tabs>
                            </b-tab>
                            <b-tab
                                v-if="userProfile.djangoProfile"
                                title="User Profile"
                            >
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Profile</b
                                    >
                                </template>
                                <b-row
                                    ><b-col
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Profile
                                        </h2></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"
                                />
                                <b-row align-v="start" class="mb-2">
                                    <b-col md="auto">
                                        <div>
                                            <b-row
                                                ><b-col
                                                    v-if="
                                                        userProfile.githubProfile
                                                    "
                                                    md="auto"
                                                    class="ml-0 mr-0"
                                                    align-self="end"
                                                >
                                                    <b-img
                                                        class="avatar"
                                                        rounded="circle"
                                                        style="max-height: 5rem; max-width: 5rem; position: relative; top: 20px; box-shadow: -2px 2px 2px #adb5bd;opacity:0.9"
                                                        :src="
                                                            userProfile.githubProfile
                                                                ? userProfile
                                                                      .githubProfile
                                                                      .avatar_url
                                                                : ''
                                                        "
                                                        v-if="
                                                            userProfile.githubProfile
                                                        "
                                                    ></b-img>
                                                    <i
                                                        v-else
                                                        class="far fa-user fa-fw fa-3x"
                                                    ></i>
                                                </b-col>
                                            </b-row>
                                            <br />
                                        </div>
                                    </b-col>
                                    <b-col
                                        style="color: white; right: 12px"
                                        align-self="end"
                                        class="ml-0 mr-0"
                                    >
                                        <b-row
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-secondary'
                                            "
                                        >
                                            <b-col
                                                class="ml-0 mr-0"
                                                align-self="end"
                                            >
                                                <b-img
                                                    rounded
                                                    style="max-height: 2rem;"
                                                    class="ml-1 mr-1 mb-3"
                                                    :src="
                                                        require('@/assets/logos/cyverse_logo.png')
                                                    "
                                                ></b-img>
                                                <b
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    v-if="
                                                        userProfile.djangoProfile !==
                                                            null
                                                    "
                                                >
                                                    {{
                                                        userProfile
                                                            .djangoProfile
                                                            .username
                                                    }}
                                                </b>
                                                <br />
                                                <a
                                                    v-if="
                                                        userProfile.githubProfile
                                                    "
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-light'
                                                            : 'text-dark'
                                                    "
                                                    :href="
                                                        'https://github.com/' +
                                                            userProfile
                                                                .githubProfile
                                                                .login
                                                    "
                                                >
                                                    <i
                                                        class="fab fa-github fa-2x fa-fw"
                                                    ></i>
                                                    {{
                                                        'https://github.com/' +
                                                            userProfile
                                                                .githubProfile
                                                                .login
                                                    }}
                                                </a>
                                            </b-col>
                                        </b-row>
                                    </b-col>
                                </b-row>
                                <b-row>
                                    <b-col md="auto">
                                        <p>
                                            <small>Name</small>
                                            <br />
                                            {{
                                                userProfile.cyverseProfile
                                                    ? `${userProfile.cyverseProfile.first_name} ${userProfile.cyverseProfile.last_name} `
                                                    : userProfile.githubProfile
                                                    ? userProfile.githubProfile
                                                          .login
                                                    : ''
                                            }}
                                            <br />
                                        </p>
                                        <p>
                                            <small>Email Address</small>
                                            <br />
                                            {{
                                                userProfile.cyverseProfile.email
                                            }}
                                            (CyVerse)
                                            <br />
                                            {{
                                                userProfile.githubProfile
                                                    ? userProfile.githubProfile
                                                          .email
                                                    : ''
                                            }}
                                            (GitHub)
                                        </p>
                                        <p>
                                            <small>Affiliation</small>
                                            <br />
                                            {{
                                                userProfile.cyverseProfile ===
                                                undefined
                                                    ? ''
                                                    : userProfile.cyverseProfile
                                                          .institution
                                            }}
                                        </p>
                                        <p>
                                            <small>Bio</small>
                                            <br />
                                            {{
                                                userProfile.githubProfile
                                                    ? userProfile.githubProfile
                                                          .bio
                                                    : 'None'
                                            }}
                                        </p>
                                        <p>
                                            <small>Location</small>
                                            <br />
                                            {{
                                                userProfile.githubProfile
                                                    ? userProfile.githubProfile
                                                          .location
                                                    : 'None'
                                            }}
                                        </p>
                                    </b-col>
                                </b-row>
                            </b-tab>
                            <b-tab
                                v-if="userProfile.djangoProfile"
                                title="Settings"
                            >
                                <template v-slot:title>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        >Settings</b
                                    >
                                </template>
                                <b-row
                                    ><b-col
                                        ><h2
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            Your Settings
                                        </h2></b-col
                                    ></b-row
                                >
                                <hr
                                    class="mt-2 mb-2"
                                    style="border-color: gray"
                                />
                                <b-row class="m-1">
                                    <b-col align-self="center" cols="3"
                                        ><i
                                            class="fas fa-envelope fa-1x fa-fw"
                                        ></i>
                                        Push Notifications:
                                        {{ profile.pushNotifications }}
                                    </b-col>
                                    <b-col align-self="center" cols="8">
                                        <b-button
                                            size="sm"
                                            v-if="
                                                profile.pushNotifications !==
                                                    'pending'
                                            "
                                            @click="togglePushNotifications"
                                            >{{
                                                profile.pushNotifications ===
                                                'enabled'
                                                    ? 'Disable'
                                                    : 'Enable'
                                            }}<b-spinner
                                                small
                                                v-if="togglingPushNotifications"
                                                label="Loading..."
                                                :variant="
                                                    profile.darkMode
                                                        ? 'light'
                                                        : 'dark'
                                                "
                                                class="ml-2 mb-1"
                                            ></b-spinner></b-button
                                    ></b-col>
                                </b-row>
                                <b-row class="m-1"
                                    ><b-col align-self="center" cols="3">
                                        <i
                                            v-if="profile.darkMode"
                                            class="fas fa-sun fa-1x fa-fw"
                                        ></i>
                                        <i
                                            v-else
                                            class="fas fa-moon fa-1x fa-fw"
                                        ></i>
                                        Dark Mode:
                                        {{
                                            profile.darkMode
                                                ? 'enabled'
                                                : 'disabled'
                                        }} </b-col
                                    ><b-col align-self="center" cols="8">
                                        <b-button
                                            size="sm"
                                            @click="toggleDarkMode"
                                            >{{
                                                profile.darkMode
                                                    ? 'Disable'
                                                    : 'Enable'
                                            }}<b-spinner
                                                small
                                                v-if="togglingDarkMode"
                                                label="Loading..."
                                                :variant="
                                                    profile.darkMode
                                                        ? 'light'
                                                        : 'dark'
                                                "
                                                class="ml-2 mb-1"
                                            ></b-spinner></b-button></b-col
                                ></b-row>
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </div>
            <b-modal
                id="connectAgent"
                :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
                centered
                close
                size="lg"
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-border-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
                title="Connect a new agent"
                @ok="connectAgent"
                :ok-disabled="agentInvalid"
                ok-title="Connect"
            >
                <b-form-group label="Name" description="A name for this agent.">
                    <b-form-input
                        :state="agentName !== ''"
                        v-model="agentName"
                        type="text"
                        placeholder="Enter a name"
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group
                    label="Host"
                    description="This agent's FQDN or IP address."
                >
                    <b-form-input
                        :state="agentHost !== ''"
                        v-model="agentHost"
                        type="text"
                        placeholder="Enter a host or IP address"
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group
                    label="Description"
                    description="A plain-text description of this agent."
                >
                    <b-form-textarea
                        :state="agentDescription !== ''"
                        v-model="agentDescription"
                        placeholder="Enter a description"
                        required
                    ></b-form-textarea>
                </b-form-group>
                <b-form-group
                    label="Working directory"
                    description="Working directory within which to run user workflows."
                >
                    <b-form-input
                        :state="agentWorkdir !== ''"
                        v-model="agentWorkdir"
                        type="text"
                        placeholder="Enter a directory path"
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group
                    label="Pre-commands"
                    description="Commands to run before user commands (e.g., loading modules, setting environment variables). Frequently useful but not required."
                >
                    <b-form-textarea
                        v-model="agentPrecommands"
                        type="text"
                        rows="3"
                        placeholder="Enter commands"
                        required
                    ></b-form-textarea>
                </b-form-group>
                <b-form-group
                    label="Max time"
                    description="Maximum runtime permitted before the workflow is aborted."
                    ><b-form-spinbutton
                        v-model="agentMaxTime"
                        min="1"
                        max="1440"
                    ></b-form-spinbutton
                ></b-form-group>
                <b-form-group
                    label="Executor"
                    description="Select an executor to orchestrate workflows."
                >
                    <b-form-select
                        v-model="agentExecutor"
                        :options="agentExecutorOptions"
                        type="text"
                        placeholder="Select an executor"
                        required
                    ></b-form-select>
                    <b-form-checkbox
                        v-if="isJobQueue(agentExecutor)"
                        v-model="agentJobArray"
                    >
                        Enable job arrays
                    </b-form-checkbox>
                    <b-form-checkbox
                        v-if="isSLURM(agentExecutor)"
                        v-model="agentLauncher"
                    >
                        Enable TACC launcher parameter sweep utility (for
                        Dask-incompatible hosts)
                    </b-form-checkbox>
                </b-form-group>
            </b-modal>
            <b-modal
                id="connectWorkflow"
                :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
                centered
                close
                size="lg"
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-border-variant="profile.darkMode ? 'dark' : 'white'"
                :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
                title="Connect Workflow"
                @ok="connectWorkflow"
                :ok-disabled="workflowInvalid"
                ok-title="Connect"
            >
                <div class="text-left">
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Specify the GitHub repository containing your workflow.
                        Before a repository can be connected, you must have a
                        file named <code>plantit.yaml</code> in your project
                        root.
                    </p>
                </div>
                <b-form-group
                    description="Type the name of the GitHub repository you'd like to connect."
                >
                    <b-form-input
                        v-model="workflowName"
                        :state="!workflowInvalid"
                        type="text"
                        placeholder="Enter a repository name"
                        required
                        @input="onWorkflowNameChange"
                    ></b-form-input>
                </b-form-group>
                <div class="text-center" v-if="isLoading">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </div>
                <div
                    class="text-center"
                    v-else-if="
                        workflowSearchResult === null && workflowName !== ''
                    "
                >
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">Repository <b>{{ workflowName }}</b> not found.</p>
                </div>
                <div
                    class="text-left"
                    v-else-if="workflowSearchResult !== null"
                >
                    <h5 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Repository
                    </h5>
                    <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <b-link
                            target="_blank"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :href="workflowSearchResult.repo.html_url"
                            ><i class="fab fa-github fa-fw mr-1"></i
                            >{{ workflowSearchResult.repo.full_name }}</b-link
                        >
                        <br />
                        {{ workflowSearchResult.repo.description }}
                        <br />
                        Last updated:
                        {{ prettify(workflowSearchResult.repo.updated_at) }}
                        <br />
                        Language: {{ workflowSearchResult.repo.language }}
                        <br />
                        Stars: {{ workflowSearchResult.repo.stargazers_count }}
                    </p>
                    <hr class="mt-2 mb-2" style="border-color: gray" />
                    <div v-if="workflowSearchResult.validation.is_valid">
                        <h5
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            Configuration
                        </h5>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            <b-row>
                                <b-col>
                                    <small>Image</small>
                                </b-col>
                                <b-col cols="10">
                                    <b>{{
                                        workflowSearchResult.config.image
                                    }}</b>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>GPU</small>
                                </b-col>
                                <b-col cols="10">
                                    {{
                                        workflowSearchResult.config.gpu
                                            ? 'Yes'
                                            : 'No'
                                    }}
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>Mount</small>
                                </b-col>
                                <b-col cols="10">
                                    {{
                                        workflowSearchResult.config.mount
                                            ? workflowSearchResult.config.mount
                                            : 'None'
                                    }}
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>Parameters</small>
                                </b-col>
                                <b-col cols="10">
                                    <b>{{
                                        workflowSearchResult.config.params
                                            ? workflowSearchResult.config.params
                                                  .length
                                            : 'None'
                                    }}</b>
                                </b-col>
                            </b-row>
                            <b-row>
                                <b-col>
                                    <small>Command</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code>{{
                                            ' ' +
                                                workflowSearchResult.config
                                                    .commands
                                        }}</code></b
                                    >
                                </b-col>
                            </b-row>
                            <b-row
                                v-if="
                                    workflowSearchResult.config.input !==
                                        undefined
                                "
                            >
                                <b-col>
                                    <small>Input</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code
                                            >[working directory]/input/{{
                                                workflowSearchResult.config
                                                    .input.filetypes
                                                    ? '[' +
                                                      (workflowSearchResult
                                                          .config.input
                                                          .filetypes
                                                          ? '*.' +
                                                            workflowSearchResult.config.input.filetypes.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      ']'
                                                    : ''
                                            }}</code
                                        ></b
                                    >
                                </b-col>
                            </b-row>
                            <b-row
                                v-if="
                                    workflowSearchResult.config.output !==
                                        undefined
                                "
                            >
                                <b-col>
                                    <small>Output</small>
                                </b-col>
                                <b-col cols="10">
                                    <b
                                        ><code
                                            >[working directory]/{{
                                                workflowSearchResult.config
                                                    .output.path
                                                    ? workflowSearchResult
                                                          .config.output.path +
                                                      '/'
                                                    : ''
                                            }}{{
                                                workflowSearchResult.config
                                                    .output.include
                                                    ? '[' +
                                                      (workflowSearchResult
                                                          .config.output.exclude
                                                          ? '+ '
                                                          : '') +
                                                      (workflowSearchResult
                                                          .config.output.include
                                                          .patterns
                                                          ? '*.' +
                                                            workflowSearchResult.config.output.include.patterns.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      (workflowSearchResult
                                                          .config.output.include
                                                          .names
                                                          ? ', ' +
                                                            workflowSearchResult.config.output.include.names.join(
                                                                ', '
                                                            )
                                                          : [])
                                                    : ''
                                            }}{{
                                                workflowSearchResult.config
                                                    .output.exclude
                                                    ? ' - ' +
                                                      (workflowSearchResult
                                                          .config.output.exclude
                                                          .patterns
                                                          ? '*.' +
                                                            workflowSearchResult.config.output.exclude.patterns.join(
                                                                ', *.'
                                                            )
                                                          : []) +
                                                      (workflowSearchResult
                                                          .config.output.exclude
                                                          .names
                                                          ? ', ' +
                                                            workflowSearchResult.config.output.exclude.names.join(
                                                                ', '
                                                            )
                                                          : [])
                                                    : '' + ']'
                                            }}
                                        </code></b
                                    >
                                </b-col>
                            </b-row>
                        </p>
                    </div>
                    <div v-else>
                        <h5
                            class="text-danger"
                        >
                            Configuration Errors
                        </h5>
                        <p
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        ></p>
                    </div>
                </div>
                <div></div>
            </b-modal>
        </b-container>
    </div>
</template>

<script>
import router from '../router';
import { mapGetters } from 'vuex';
import workflows from '@/components/workflows.vue';
import datatree from '@/components/data-tree.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import moment from 'moment';

export default {
    name: 'User',
    components: {
        workflows,
        datatree
    },
    data: function() {
        return {
            isOpen: false,
            isLoading: false,
            statsScope: 'Hour',
            workflowName: '',
            workflowSearchResult: null,
            workflowExists: false,
            arrowCounter: -1,
            agentName: '',
            agentHost: '',
            agentDescription: '',
            agentWorkdir: '',
            agentPrecommands: '',
            agentMaxTime: 0,
            agentExecutor: 'Local',
            agentExecutorOptions: [
                { value: 'Local', text: 'Local' },
                { value: 'SLURM', text: 'SLURM' },
                { value: 'PBS', text: 'PBS' }
            ],
            agentQueue: '',
            agentProject: '',
            agentMaxWalltime: 0,
            agentMaxMem: 0,
            agentMaxCores: 0,
            agentMaxProcesses: 0,
            agentMaxNodes: 0,
            agentHeaderSkip: '',
            agentLauncher: false,
            agentJobArray: false,
            agentPublic: false,
            agentLogo: '',
            togglingPushNotifications: false,
            togglingDarkMode: false,
            currentTab: 0,
            sharedDatasets: [],
            sharingDatasets: [],
            directoryPolicies: [],
            directoryPolicyNodes: [],
            data: {},
            loadingMoreRuns: false,
            agents: [],
            agentsLoading: false,
            alertEnabled: false,
            alertMessage: '',
            runSearchText: '',
            pinnedDatasetsSearchText: '',
            yourDatasetsSearchText: '',
            sharedDatasetsSearchText: '',
            sharingDatasetsSearchText: ''
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('runs', ['runsLoading', 'runs']),
        ...mapGetters('notifications', ['notifications']),
        ...mapGetters('workflows', ['workflows', 'workflowsLoading']),
        ...mapGetters('datasets', ['openedDataset', 'openedDatasetLoading']),
        unreadNotifications() {
            return this.notifications.filter(n => !n.read);
        },
        userWorkflows() {
            if (
                this.workflowsLoading ||
                this.workflows === undefined ||
                this.profile.githubProfile === undefined
            )
                return [];
            return this.workflows.filter(wf => {
                return wf.repo.owner.login === this.profile.githubProfile.login;
            });
        },
        runningRuns() {
            return this.runs.filter(r => !r.is_complete);
        },
        completedRuns() {
            return this.runs.filter(r => r.is_complete);
        },
        filteredRunningRuns() {
            return this.runningRuns.filter(
                r =>
                    (r.workflow_name !== null &&
                        r.workflow_name.includes(this.runSearchText)) ||
                    (r.guid !== null && r.id.includes(this.runSearchText)) ||
                    r.tags.some(t => t.includes(this.runSearchText))
            );
        },
        filteredCompletedRuns() {
            return this.completedRuns.filter(
                r =>
                    (r.workflow_name !== null &&
                        r.workflow_name.includes(this.runSearchText)) ||
                    (r.guid !== null && r.id.includes(this.runSearchText)) ||
                    r.tags.some(t => t.includes(this.runSearchText))
            );
        },
        workflowInvalid() {
            return this.workflowSearchResult === null;
        },
        agentInvalid() {
            return (
                this.agentName === '' ||
                this.agentDescription === '' ||
                this.agentHost === '' ||
                this.agentWorkdir === '' ||
                this.agentPrecommands === '' ||
                this.agentExecutor === '' ||
                (this.agentExecutor !== 'Local' &&
                    (this.agentQueue === '' ||
                        this.agentProject === '' ||
                        this.agentMaxWalltime <= 0 ||
                        this.agentMaxProcesses <= 0 ||
                        this.agentMaxCores <= 0 ||
                        this.agentMaxNodes <= 0 ||
                        this.agentMaxMem <= 0))
            );
        }
    },
    asyncComputed: {
        async userProfile() {
            if (
                this.$router.currentRoute.params.username ===
                this.profile.djangoProfile.username
            )
                return this.profile;
            else {
                return await axios
                    .get(`/apis/v1/users/get_current`)
                    .then(response => {
                        return {
                            djangoProfile: response.data.django_profile,
                            cyverseProfile: response.data.cyverse_profile,
                            githubProfile: response.data.github_profile
                        };
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        if (error.response.status === 500) throw error;
                    });
            }
        }
    },
    async mounted() {
        document.addEventListener('click', this.handleClickOutside);
        await Promise.all([
            this.$store.dispatch('workflows/loadAll'),
            this.$store.dispatch('users/loadAll'),
            this.loadDataset(
                `/iplant/home/${this.profile.djangoProfile.username}/`,
                this.profile.djangoProfile.cyverse_token
            ),
            this.loadAgents(),
            this.loadSharedDatasets(),
            this.loadSharingDatasets()
        ]);
    },
    destroyed() {
        document.removeEventListener('click', this.handleClickOutside);
    },
    watch: {
        // eslint-disable-next-line no-unused-vars
        items: function(value, _) {
            if (this.isAsync) {
                this.workflowSearchResult = value;
                this.isLoading = false;
            }
        }
    },
    methods: {
        onWorkflowNameChange() {
            this.isLoading = true;
            return axios
                .get(
                    `/apis/v1/workflows/${this.profile.githubProfile.login}/${this.workflowName}/search/`
                )
                .then(response => {
                    this.workflowSearchResult = response.data;
                    this.isLoading = false;
                    this.$emit('input', this.workflowName);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.workflowSearchResult = null;
                    this.isLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        setWorkflowName(result) {
            this.workflowName = result;
            this.isOpen = false;
        },
        handleClickOutside(event) {
            if (!this.$el.contains(event.target)) {
                this.arrowCounter = -1;
                this.isOpen = false;
            }
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        },
        prettifyDuration: function(dur) {
            return moment.duration(dur, 'seconds').humanize();
        },
        tabLinkClass(idx) {
            if (this.profile.djangoProfile === null)
                return this.profile.darkMode ? '' : 'text-dark';
            if (this.currentTab === idx) {
                return this.profile.darkMode ? '' : 'text-dark';
            } else {
                return this.profile.darkMode
                    ? 'background-dark text-light'
                    : 'text-dark';
            }
        },
        isJobQueue(executor) {
            return executor !== 'Local';
        },
        isSLURM(executor) {
            return executor === 'SLURM';
        },
        showConnectWorkflowModal() {
            this.$bvModal.show('connectWorkflow');
        },
        connectWorkflow() {},
        refreshWorkflows() {
            this.$store.dispatch('workflows/refreshAll');
        },
        showConnectAgentModal() {
            this.$bvModal.show('connectAgent');
        },
        async connectAgent() {
            let data = {
                auth: {
                    username: this.authenticationUsername,
                    password: this.authenticationPassword
                },
                config: {
                    name: this.agentName,
                    description: this.agentDescription,
                    workdir: this.agentWorkdir,
                    username: this.profile.djangoProfile.username,
                    hostname: this.agentHost,
                    pre_commands: this.agentPrecommands,
                    max_time: this.agentMaxTime,
                    public: this.agentPublic,
                    logo: this.agentLogo,
                    executor: this.agentExecutor
                }
            };

            await axios({
                method: 'post',
                url: `/apis/v1/agents/new/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    alert(response.data.created);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    // TODO probably an auth error: display info and allow user to edit info and retry connection
                    throw error;
                });
        },
        showDeleteRunPrompt(run) {
            this.$bvModal.show('delete ' + run.id);
        },
        deleteRun(run) {
            axios
                .get(`/apis/v1/runs/${run.id}/delete/`)
                .then(response => {
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                        this.$store.dispatch('runs/loadAll');
                        if (
                            this.$router.currentRoute.name === 'run' &&
                            run.id === this.$router.currentRoute.params.id
                        )
                            router.push({
                                name: 'user',
                                params: {
                                    username: this.profile.djangoProfile
                                        .username
                                }
                            });
                    } else {
                        this.showFailedToCancelAlert = true;
                    }
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        async loadAgents() {
            this.agentsLoading = true;
            return axios
                .get(`/apis/v1/agents/get_by_username/`)
                .then(response => {
                    this.agentsLoading = false;
                    this.agents = response.data.agents;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.agentsLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        async loadDataset(path, token) {
            return axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    this.data = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadSharingDatasets() {
            await axios
                .get(`/apis/v1/datasets/sharing/`)
                .then(response => {
                    this.sharingDatasets = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadSharedDatasets() {
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(response => {
                    this.sharedDatasets = response.data;
                    this.sharedDataLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.sharedDataLoading = false;
                    throw error;
                });
        },
        openDataset() {
            this.$store.dispatch('datasets/updateLoading', true);
            let data = { agent: this.agent.name };
            // if (this.mustAuthenticate)
            //     data['auth'] = {
            //         username: this.authenticationUsername,
            //         password: this.authenticationPassword
            //     };

            axios({
                method: 'post',
                url: `/apis/v1/datasets/open/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    await this.$store.dispatch(
                        'datasets/updateOpened',
                        response.data.session
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async unshareDataset(directory) {
            await axios({
                method: 'post',
                url: `/apis/v1/datasets/unshare/`,
                data: {
                    user: directory.guest,
                    path: directory.path,
                    role: directory.role
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(() => {
                    this.loadSharingDatasets();
                    this.alertMessage = `Unshared dataset ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to unshare dataset ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.alertEnabled = true;
                    throw error;
                });
        },
        async togglePushNotifications() {
            this.togglingPushNotifications = true;
            await this.$store.dispatch('user/togglePushNotifications');
            this.togglingPushNotifications = false;
            this.alertMessage = `Push notifications ${this.profile.pushNotifications}`;
            this.alertEnabled = true;
        },
        async toggleDarkMode() {
            this.togglingDarkMode = true;
            this.$store.dispatch('user/toggleDarkMode');
            this.togglingDarkMode = false;
            this.alertMessage = `Dark mode ${this.profile.pushNotifications}`;
            this.alertEnabled = true;
        },
        goToAgent: function(agent) {
            router.push({
                name: 'agent',
                params: {
                    name: agent.name
                }
            });
        },
        goToRun: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id,
                    username: this.profile.djangoProfile.username
                }
            });
        },
        goToWorkflow: function(workflow) {
            router.push({
                name: 'workflow',
                params: {
                    owner: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
                }
            });
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>

<style lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.autocomplete-result.is-active
  .autocomplete-result:hover
    background-color: #4AAE9B
    color: white

.background-dark
  background-color: $dark !important
  color: $light

.background-success
  background-color: $success !important
  color: $dark !important
</style>
