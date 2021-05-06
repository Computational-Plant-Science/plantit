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
                <b-row align-v="start" class="mb-2">
                    <b-col md="auto">
                        <div>
                            <b-row
                                ><b-col
                                    v-if="userProfile.githubProfile"
                                    md="auto"
                                    class="ml-0 mr-0"
                                    align-self="end"
                                >
                                    <b-img
                                        class="avatar"
                                        rounded
                                        style="max-height: 6rem; max-width: 6rem; position: relative; top: 20px; box-shadow: -2px 2px 2px #adb5bd"
                                        :src="
                                            userProfile.githubProfile
                                                ? userProfile.githubProfile
                                                      .avatar_url
                                                : ''
                                        "
                                        v-if="userProfile.githubProfile"
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
                            <b-col class="ml-0 mr-0" align-self="end">
                                <h3
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                >
                                    {{
                                        userProfile.cyverseProfile
                                            ? `${userProfile.cyverseProfile.first_name} ${userProfile.cyverseProfile.last_name} `
                                            : userProfile.githubProfile
                                            ? userProfile.githubProfile.login
                                            : ''
                                    }}<small
                                        :class="
                                            profile.darkMode
                                                ? 'text-warning'
                                                : 'text-dark'
                                        "
                                        v-if="
                                            userProfile.djangoProfile !== null
                                        "
                                        >({{
                                            userProfile.djangoProfile.username
                                        }})</small
                                    >
                                </h3>
                                <a
                                    v-if="userProfile.githubProfile"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    :href="
                                        'https://github.com/' +
                                            userProfile.githubProfile.login
                                    "
                                >
                                    <i class="fab fa-github fa-1x fa-fw"></i>
                                    {{
                                        'https://github.com/' +
                                            userProfile.githubProfile.login
                                    }}
                                </a>
                            </b-col>
                        </b-row>
                    </b-col>
                </b-row>
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
                                v-if="userProfile.djangoProfile"
                                title="Profile"
                                active
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
                                <b-row>
                                    <b-col md="auto">
                                        <p>
                                            <small>Email</small>
                                            <br />
                                            {{
                                                userProfile.cyverseProfile.email
                                            }}
                                            <br />
                                            {{
                                                userProfile.githubProfile
                                                    ? userProfile.githubProfile
                                                          .email
                                                    : ''
                                            }}
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
                                        >Collections</b
                                    >
                                </template>
                                <b-row class="mb-2"
                                    ><b-col>
                                        <b-input-group>
                                            <template #prepend>
                                                <b-input-group-text>
                                                    Your collections
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
                                                    yourCollectionsSearchText
                                                "
                                            ></b-form-input></b-input-group></b-col
                                ></b-row>
                                <b-row>
                                    <b-col>
                                        <datatree
                                            :node="data"
                                            select="directory"
                                            :upload="true"
                                            :download="true"
                                            :clusters="clusters"
                                            :class="
                                                profile.darkMode
                                                    ? 'theme-dark'
                                                    : 'theme-light'
                                            "
                                        ></datatree></b-col
                                ></b-row>
                                <hr />
                                <b-row class="mb-2"
                                    ><b-col>
                                        <b-input-group>
                                            <template #prepend>
                                                <b-input-group-text>
                                                    Shared with you
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
                                                    sharedCollectionsSearchText
                                                "
                                            ></b-form-input></b-input-group></b-col
                                ></b-row>
                                <b-row>
                                    <b-col>
                                        <datatree
                                            :node="sharedCollections"
                                            select="directory"
                                            :clusters="clusters"
                                            :upload="true"
                                            :download="true"
                                            :class="
                                                profile.darkMode
                                                    ? 'theme-dark'
                                                    : 'theme-light'
                                            "
                                        ></datatree></b-col
                                ></b-row>
                                <hr />
                                <b-row class="mb-2"
                                    ><b-col>
                                        <b-input-group>
                                            <template #prepend>
                                                <b-input-group-text>
                                                    Collections you've shared
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
                                                    sharingCollectionsSearchText
                                                "
                                            ></b-form-input></b-input-group></b-col
                                ></b-row>
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
                                            @dismissed="alertEnabled = false"
                                        >
                                            {{ alertMessage }}
                                        </b-alert>
                                    </b-col>
                                </b-row>
                                <b-row
                                    v-for="directory in sharingCollections"
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
                                                unshareCollection(directory)
                                            "
                                            ><i
                                                class="fas fa-user-lock fa-fw"
                                            ></i>
                                            Unshare</b-button
                                        ></b-col
                                    ></b-row
                                >
                                <b-row v-if="sharingCollections.length === 0"
                                    ><b-col
                                        ><p>
                                            <small
                                                >You haven't shared any
                                                collections with anyone.</small
                                            >
                                        </p></b-col
                                    ></b-row
                                ></b-tab
                            >
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
                                    align-v="center"
                                    align-h="center"
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
                                    <workflows
                                        class="m-1"
                                        :github-user="
                                            profile.githubProfile.login
                                        "
                                        :github-token="
                                            profile.djangoProfile.github_token
                                        "
                                        :workflows="userWorkflows"
                                    >
                                    </workflows>
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
                                        >Clusters</b
                                    >
                                </template>
                                <div>
                                    <b-row v-if="clustersLoading">
                                        <b-spinner
                                            type="grow"
                                            label="Loading..."
                                            variant="secondary"
                                        ></b-spinner>
                                    </b-row>
                                    <b-row
                                        class="text-left"
                                        v-if="
                                            !clustersLoading &&
                                                clusters.length === 0
                                        "
                                    >
                                        <b-col>
                                            <b class="text-danger"
                                                >You have no cluster
                                                permissions.</b
                                            ><br />See
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light'
                                                        : 'text-dark'
                                                "
                                                to="/clusters"
                                                ><i
                                                    class="fas fa-server fa-1x fa-fw"
                                                ></i>
                                                Clusters</b-link
                                            >
                                            to request guest access to public
                                            computing resources.
                                        </b-col>
                                    </b-row>
                                    <b-card-group
                                        v-else
                                        deck
                                        columns
                                        class="justify-content-center mt-3"
                                    >
                                        <b-card
                                            v-for="cluster in clusters"
                                            v-bind:key="cluster.name"
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
                                                                clusterSelected(
                                                                    cluster
                                                                )
                                                            "
                                                        >
                                                            {{ cluster.name }}
                                                        </b-link>
                                                    </h2>
                                                    <b-badge
                                                        v-if="!cluster.public"
                                                        class="mr-1"
                                                        variant="warning"
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
                                                        v-if="
                                                            cluster.role !==
                                                                'own'
                                                        "
                                                        variant="warning"
                                                        >Guest</b-badge
                                                    >
                                                    <b-badge
                                                        v-else
                                                        variant="success"
                                                        >Owner</b-badge
                                                    >

                                                    <br />
                                                    <small>
                                                        {{
                                                            cluster.description
                                                        }}
                                                    </small>
                                                    <br />
                                                </b-col>
                                                <b-col cols="1"></b-col>
                                            </b-row>
                                            <b-img
                                                v-if="cluster.logo"
                                                rounded
                                                class="card-img-right overflow-hidden"
                                                style="max-height: 5rem;position: absolute;right: 20px;top: 20px;z-index:1"
                                                right
                                                :src="cluster.logo"
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
                                <b-tabs
                                    nav-class="bg-transparent"
                                    active-nav-item-class="bg-secondary text-dark"
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
                                        <b-input-group
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
                                        </b-input-group>
                                        <b-row
                                            class="m-3 mb-1 pl-0 pr-0"
                                            align-v="center"
                                            ><b-col
                                                class="m-0 pl-0 pr-0 text-center"
                                            >
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
                                                                run.cluster
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
                                                            ? 'text-center text-light pl-3 pr-3'
                                                            : 'text-center text-dark pl-3 pr-3'
                                                    "
                                                    v-if="
                                                        runningRuns.length === 0
                                                    "
                                                >
                                                    No workflows running.
                                                </p>
                                            </b-col></b-row
                                        >
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
                                        <b-input-group
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
                                        </b-input-group>
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
                                                                        run.cluster
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
                                                                        showDeletePrompt(
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
                                                class="m-0 pl-0 pr-0 text-center"
                                            >
                                                <p
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-center text-light pl-3 pr-3'
                                                            : 'text-center text-dark pl-3 pr-3'
                                                    "
                                                >
                                                    You haven't run any
                                                    workflows yet.
                                                </p>
                                            </b-col>
                                        </b-row>
                                    </b-tab></b-tabs
                                >
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </div>
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
            togglingPushNotifications: false,
            togglingDarkMode: false,
            currentTab: 0,
            sharedCollections: [],
            sharingCollections: [],
            directoryPolicies: [],
            directoryPolicyNodes: [],
            data: {},
            loadingMoreRuns: false,
            clusters: [],
            clustersLoading: false,
            alertEnabled: false,
            alertMessage: '',
            runSearchText: '',
            pinnedCollectionsSearchText: '',
            yourCollectionsSearchText: '',
            sharedCollectionsSearchText: '',
            sharingCollectionsSearchText: ''
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('runs', ['runsLoading', 'runs']),
        ...mapGetters('workflows', ['workflows', 'workflowsLoading']),
        ...mapGetters('collections', [
            'openedCollection',
            'openedCollectionLoading'
        ]),
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
        await Promise.all([
            this.$store.dispatch('workflows/loadAll'),
            this.$store.dispatch('users/loadAll'),
            this.loadCollection(
                `/iplant/home/${this.profile.djangoProfile.username}/`,
                this.profile.djangoProfile.cyverse_token
            ),
            this.loadClusters(),
            this.loadSharedCollections(),
            this.loadSharingCollections()
        ]);
    },
    methods: {
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
        onDelete(run) {
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
        showDeletePrompt(run) {
            this.$bvModal.show('delete ' + run.id);
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        },
        openCollection() {
            this.$store.dispatch('collections/updateLoading', true);
            let data = { cluster: this.cluster.name };
            // if (this.mustAuthenticate)
            //     data['auth'] = {
            //         username: this.authenticationUsername,
            //         password: this.authenticationPassword
            //     };

            axios({
                method: 'post',
                url: `/apis/v1/collections/open/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    await this.$store.dispatch(
                        'collections/updateOpened',
                        response.data.session
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        // selectNode(node) {
        //     if (
        //         !this.sessionLoading &&
        //         this.session !== null &&
        //         this.session !== undefined
        //     )
        //         if (node.kind === 'directory')
        //             router.push({
        //                 name: 'collection',
        //                 params: {
        //                     path: node.path
        //                 }
        //             });
        //         else
        //             router.push({
        //                 name: 'artifact',
        //                 params: {
        //                     path: node.path
        //                 }
        //             });
        // },
        async unshareCollection(directory) {
            await axios({
                method: 'post',
                url: `/apis/v1/collections/unshare/`,
                data: {
                    user: directory.guest,
                    path: directory.path,
                    role: directory.role
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(() => {
                    this.loadSharingCollections();
                    this.alertMessage = `Unshared collection ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.alertEnabled = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.alertMessage = `Failed to unshare collection ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.alertEnabled = true;
                    throw error;
                });
        },
        async loadSharingCollections() {
            await axios
                .get(`/apis/v1/collections/sharing/`)
                .then(response => {
                    this.sharingCollections = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadSharedCollections() {
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
                    this.sharedCollections = response.data;
                    this.sharedDataLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.sharedDataLoading = false;
                    throw error;
                });
            // await axios
            //     .get(`/apis/v1/collections/shared/`)
            //     .then(response => {
            //         this.sharedCollections = response.data;
            //     })
            //     .catch(error => {
            //         Sentry.captureException(error);
            //         throw error;
            //     });
        },
        clusterSelected: function(cluster) {
            router.push({
                name: 'cluster',
                params: {
                    name: cluster.name
                }
            });
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
        onRunSelected: function(items) {
            router.push({
                name: 'run',
                params: {
                    id: items[0].id,
                    username: this.profile.djangoProfile.username
                }
            });
        },
        async loadClusters() {
            this.clustersLoading = true;
            return axios
                .get(`/apis/v1/clusters/get_by_username/`)
                .then(response => {
                    this.clustersLoading = false;
                    this.clusters = response.data.clusters;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.clustersLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        workflowSelected: function(workflow) {
            router.push({
                name: 'workflow',
                params: {
                    owner: workflow['repo']['owner']['login'],
                    name: workflow['repo']['name']
                }
            });
        },
        async getDirectory(path) {
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        }
                    }
                )
                .then(response => {
                    this.sharedCollections.push(response.data);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        async loadCollection(path, token) {
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

.background-dark
  background-color: $dark !important
  color: $light

.background-success
  background-color: $success !important
  color: $dark !important
</style>
