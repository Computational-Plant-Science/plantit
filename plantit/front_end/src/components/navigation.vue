<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="runs"
            shadow="lg"
            :bg-variant="profile.darkMode ? 'dark' : 'white'"
            :text-variant="profile.darkMode ? 'light' : 'dark'"
            no-header-close
            width="550px"
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-0">
                    <b-row
                        class="ml-3 mr-3 mb-1 mt-0 pt-0 pl-0 pr-0 text-left"
                        align-v="start"
                    >
                        <b-col
                            class="ml-0 mr-0 pl-0 pr-0 pt-0 mt-0"
                            align-self="center"
                            md="auto"
                        >
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light mt-1'
                                        : 'text-dark mt-1'
                                "
                            >
                                Runs
                            </h4>
                        </b-col>
                        <b-col align-self="center"
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
                                    v-model="runSearchText"
                                ></b-form-input>
                            </b-input-group>
                        </b-col>
                        <b-col
                            class="ml-3 mr-0 pl-0 pt-0 pr-0 mt-1"
                            align-self="center"
                            md="auto"
                        >
                            <b-button
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                class="text-left m-0"
                                @click="hide"
                            >
                                <i class="fas fa-arrow-left fa-1x fa-fw"></i>
                                Hide
                            </b-button>
                        </b-col>
                    </b-row>
                    <br/>
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Running</b></b-col>
                    </b-row>
                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group
                                v-if="runningRuns.length > 0"
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
                                        params: { id: run.id }
                                    }"
                                >
                                    <b-img
                                        v-if="
                                            run.workflow_image_url !==
                                                undefined &&
                                                run.workflow_image_url !== null
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
                                            params: { id: run.id }
                                        }"
                                        replace
                                        >{{ run.id }}</b-link
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
                                    <small v-if="!run.is_complete"
                                        >Running</small
                                    >
                                    <b-badge
                                        :variant="
                                            run.is_failure || run.is_timeout
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
                                    ><small> {{ prettify(run.updated) }}</small>
                                    <br />
                                    <small
                                        v-if="run.workflow_name !== null"
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
                                            ><i class="fab fa-github fa-fw"></i>
                                            {{ run.workflow_owner }}/{{
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
                                v-if="runningRuns.length === 0"
                            >
                                No workflows are running right now.
                            </p>
                        </b-col></b-row
                    >
                  <br/>
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Completed</b></b-col>
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
                                                    params: { id: run.id }
                                                }"
                                                replace
                                                >{{ run.id }}</b-link
                                            >
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col>
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
                                                <br
                                                    v-if="run.tags.length > 0"
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
                                                    {{ run.workflow_owner }}/{{
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
                                                @click="showDeletePrompt(run)"
                                            >
                                                <i class="fas fa-trash"></i>
                                                Delete
                                            </b-button>
                                        </b-col></b-row
                                    >
                                    <b-modal
                                        :id="'delete ' + run.id"
                                        :title-class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        centered
                                        close
                                        :header-text-variant="
                                            profile.darkMode ? 'white' : 'dark'
                                        "
                                        :header-bg-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        :footer-bg-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        :body-bg-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        :header-border-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        :footer-border-variant="
                                            profile.darkMode ? 'dark' : 'white'
                                        "
                                        ok-variant="outline-danger"
                                        title="Delete this run?"
                                        @ok="onDelete(run)"
                                    >
                                        <p
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                        >
                                            This cannot be undone.
                                        </p>
                                    </b-modal>
                                </b-list-group-item>
                            </b-list-group>
                        </b-col>
                        <b-col
                            v-if="runsLoading || loadingMoreRuns"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <b-spinner
                                type="grow"
                                variant="secondary"
                            ></b-spinner
                        ></b-col>
                        <!--<b-col
                            v-else-if="completedRuns.length > 0"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <b-nav vertical class="m-0 p-0">
                                <b-nav-item class="m-0 p-0">
                                    <b-button
                                        :variant="
                                            profile.darkMode ? 'dark' : 'light'
                                        "
                                        :disabled="runsLoading"
                                        block
                                        class="text-center m-0"
                                        @click="loadRuns(currentRunPage + 1)"
                                    >
                                        <i
                                            class="fas fa-chevron-down fa-fw"
                                        ></i>
                                        Load More
                                    </b-button>
                                </b-nav-item>
                            </b-nav>
                        </b-col>-->
                        <b-col
                            v-if="!runsLoading && completedRuns.length === 0"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-center text-light pl-3 pr-3'
                                        : 'text-center text-dark pl-3 pr-3'
                                "
                            >
                                You haven't run any workflows yet.
                            </p>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-sidebar
            right
            id="notifications"
            shadow="lg"
            :bg-variant="profile.darkMode ? 'dark' : 'white'"
            :text-variant="profile.darkMode ? 'light' : 'dark'"
            width="550px"
            no-header-close
        >
            <template v-slot:default="{ hide }">
                <b-container class="p-0">
                    <b-row
                        class="ml-3 mr-3 mb-1 mt-0 pt-0 pl-0 pr-0 text-left"
                        align-v="start"
                    >
                        <b-col
                            class="ml-1 mr-0 pl-0 pt-0 pr-0 mt-1"
                            align-self="center"
                        >
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light mt-1'
                                        : 'text-dark mt-1'
                                "
                            >
                                Notifications
                            </h4>
                        </b-col>
                        <b-col
                            class="ml-0 mr-0 pl-0 pr-0 pt-0 mt-0"
                            align-self="center"
                            md="auto"
                        >
                            <!--<b-button
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                class="text-left m-0"
                                @click="markAllRead"
                            >
                                Mark All Read
                                <i class="fas fa-check-double fa-1x fa-fw"></i>
                            </b-button>-->
                            <b-button
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                class="text-left m-0"
                                @click="hide"
                            >
                                Hide
                                <i class="fas fa-arrow-right fa-1x fa-fw"></i>
                            </b-button>
                        </b-col>
                    </b-row>
                  <br/>
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Unread</b></b-col>
                    </b-row>
                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group
                                v-if="unreadNotifications.length > 0"
                                class="text-left m-0 p-0"
                            >
                                <b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="notification in unreadNotifications"
                                    v-bind:key="notification.id"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light bg-dark m-0 p-2 mb-2 overflow-hidden'
                                            : 'text-dark bg-white m-0 p-2 mb-2 overflow-hidden'
                                    "
                                >
                                    <b-row>
                                        <b-col>
                                            <p
                                                v-if="
                                                    notification.policy !==
                                                        undefined
                                                "
                                            >
                                                {{ notification.message }}
                                                <br />
                                                <small>{{
                                                    prettify(
                                                        notification.created
                                                    )
                                                }}</small>
                                            </p>
                                        </b-col>
                                        <b-col md="auto">
                                            <b-button
                                                size="sm"
                                                :disabled="notification.read"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'dark'
                                                        : 'light'
                                                "
                                                class="text-left m-0"
                                                @click="markRead(notification)"
                                            >
                                                Mark Read
                                                <i class="fas fa-check"></i>
                                            </b-button>
                                        </b-col>
                                    </b-row>
                                </b-list-group-item>
                            </b-list-group>
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-center text-light pl-3 pr-3'
                                        : 'text-center text-dark pl-3 pr-3'
                                "
                                v-if="unreadNotifications.length === 0"
                            >
                                No notifications to show.
                            </p>
                        </b-col>
                    </b-row>
                  <br/>
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Read</b></b-col>
                    </b-row>
                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group
                                v-if="readNotifications.length > 0"
                                class="text-left m-0 p-0"
                            >
                                <b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="notification in readNotifications"
                                    v-bind:key="notification.id"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light bg-dark m-0 p-2 mb-2 overflow-hidden'
                                            : 'text-dark bg-white m-0 p-2 mb-2 overflow-hidden'
                                    "
                                >
                                    {{ notification.message }}
                                    <br />
                                    <br />
                                    <small>{{
                                        prettify(notification.created)
                                    }}</small>
                                </b-list-group-item>
                            </b-list-group>
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-center text-light pl-3 pr-3'
                                        : 'text-center text-dark pl-3 pr-3'
                                "
                                v-if="readNotifications.length === 0"
                            >
                                No notifications to show.
                            </p>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="sm"
            class="logo p-0"
            style="min-height: 44px; max-height: 46px; z-index: 1000"
            fixed="top"
            :type="profile.darkMode ? 'dark' : 'secondary'"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-collapse class="m-0 p-0" is-nav>
                <b-navbar-nav class="m-0 p-0 pl-3 mr-1">
                    <b-nav-item class="m-0 p-0" v-b-toggle.runs>
                        <b-button
                            class="brand-img m-0 p-0"
                            v-bind:class="{ 'not-found': notFound }"
                            variant="outline-white"
                            @mouseenter="titleContent = 'sidebar'"
                            @mouseleave="titleContent = 'breadcrumb'"
                        >
                            <b-img
                                class="m-0 p-0 mb-3"
                                center
                                width="39px"
                                :src="require('../assets/logo.png')"
                                alt="Plant IT"
                            ></b-img>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
                <transition name="component-fade" mode="out-in">
                    <b-breadcrumb
                        class="m-o p-0 mt-3"
                        style="background-color: transparent;"
                        v-if="titleContent === 'sidebar'"
                    >
                        <b-breadcrumb-item
                            disabled
                            class="ml-4"
                            :class="
                                profile.darkMode ? 'crumb-dark' : 'crumb-light'
                            "
                        >
                            <h2
                                :class="
                                    profile.darkMode
                                        ? 'crumb-dark'
                                        : 'crumb-light'
                                "
                            >
                                Your Runs ({{ runningRuns.length }}
                                in progress)
                            </h2>
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                    <b-navbar-nav class="m-0 p-0"
                        ><b-nav-item class="mt-1" href="/"
                            ><h3
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                                style="text-decoration: underline;"
                            >
                                plant<small
                                    class="mb-3 text-success"
                                    style="text-decoration: underline;text-shadow: 1px 0 0 #000, 0 -1px 0 #000, 0 1px 0 #000, -1px 0 0 #000;"
                                    >IT</small
                                >
                            </h3></b-nav-item
                        ><b-nav-item
                            title="Docs"
                            href="https://plantit.readthedocs.io/en/latest"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            ><span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fas fa-book fa-1x fa-fw"></i
                                >Docs</span
                            ></b-nav-item
                        >
                        <b-nav-item
                            href="https://github.com/Computational-Plant-Science/plantit"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="GitHub"
                        >
                            <span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fab fa-github fa-1x fa-fw"></i>
                                Github</span
                            >
                        </b-nav-item>
                        <b-nav-item
                            href="#"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Slack"
                        >
                            <span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fab fa-slack fa-1x fa-fw"></i>
                                Slack</span
                            >
                        </b-nav-item>
                    </b-navbar-nav>
                    <b-breadcrumb
                        class="m-o p-0 mt-2 text-warning"
                        style="background-color: transparent"
                        v-if="titleContent === 'breadcrumb'"
                    >
                        <b-breadcrumb-item
                            v-for="crumb in crumbs"
                            :key="crumb.text"
                            :to="crumb.href"
                            :disabled="crumb.text === 'runs'"
                            class="ml-0 mr-0"
                        >
                            <h5
                                :class="
                                    profile.darkMode
                                        ? 'crumb-dark'
                                        : 'crumb-light'
                                "
                            >
                                {{ crumb.text }}
                            </h5>
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                </transition>
                <b-navbar-nav class="ml-auto p-0 mt-1">
                    <b-nav-item
                        v-if="
                            profile.loggedIn
                                ? profile.githubProfile === null ||
                                  profile.githubProfile === undefined
                                : false
                        "
                        title="Log in to GitHub"
                        href="/apis/v1/idp/github_request_identity/"
                        class="p-1 mt-2 ml-0 mr-0"
                    >
                        <b-button
                            class="mt-2 text-left"
                            variant="success"
                            size="md"
                        >
                            <i class="fab fa-github"></i>
                            Log in to GitHub
                        </b-button>
                    </b-nav-item>
                    <b-nav-item-dropdown
                        right
                        v-if="profile.loggedIn"
                        :title="profile.djangoProfile.username"
                        class="p-1 m-2 mr-0 ml-0 dropdown-custom"
                        :menu-class="
                            profile.darkMode ? 'theme-dark' : 'theme-light'
                        "
                        style="font-size: 12pt"
                    >
                        <template #button-content>
                            <b-button
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                class="ml-0 mr-0 mt-2 text-left"
                                size="md"
                            >
                                <span
                                    :title="
                                        'Notifications (' +
                                            unreadNotifications.length +
                                            ')'
                                    "
                                    v-if="unreadNotifications.length > 0"
                                    class="fa-stack mr-2"
                                    ><i
                                        class="fas fa-dot-circle fa-stack-2x text-warning"
                                    ></i
                                    ><i
                                        class="fas fa-bell fa-stack-1x text-dark"
                                    ></i
                                ></span>
                                <b-img
                                    v-if="profile.githubProfile"
                                    class="avatar m-0 mb-1 p-0 github-hover logo"
                                    style="min-width: 32px; min-height: 32px; position: relative; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                                    rounded="circle"
                                    :src="
                                        profile.githubProfile
                                            ? profile.githubProfile.avatar_url
                                            : ''
                                    "
                                ></b-img>
                                <i v-else class="far fa-user"></i>
                                {{
                                    profile.cyverseProfile
                                        ? profile.cyverseProfile.first_name
                                        : profile.djangoProfile.username
                                }}
                                <i class="fas fa-caret-down fa-fw"></i>
                            </b-button>
                        </template>
                        <b-dropdown-text>Resource Context</b-dropdown-text>
                        <b-dropdown-item
                            title="Agents"
                            to="/agents"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-users fa-1x fa-fw"></i>
                            Public
                            <i v-if="$route.name === 'public'" class="fas fa-check fa-1x fa-fw"></i>
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Profile"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            :to="
                                '/user/' + profile.djangoProfile.username + '/'
                            "
                        >
                            <i class="fas fa-user fa-1x fa-fw"></i>
                            Yours
                          <i v-if="$route.name === 'user'" class="fas fa-check fa-1x fa-fw"></i>
                        </b-dropdown-item>
                        <hr class="mt-2 mb-2" style="border-color: gray" />
                        <b-dropdown-text>Your Account</b-dropdown-text>
                        <b-dropdown-item
                            :title="
                                'Notifications (' +
                                    unreadNotifications.length +
                                    ')'
                            "
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            v-b-toggle.notifications
                        >
                            <i class="fas fa-bell fa-1x fa-fw"></i>
                            Notifications
                            <span v-if="unreadNotifications.length > 0"
                                >({{ unreadNotifications.length }} unread)</span
                            >
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="Log Out"
                            @click="logOut"
                            class="text-danger"
                            link-class="text-danger"
                        >
                            <i class="fas fa-door-closed fa-1x fa-fw"></i>
                            Log Out
                        </b-dropdown-item>
                    </b-nav-item-dropdown>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <!--<b-navbar
            v-if="
                openedDatasetLoading ||
                    (openedDataset !== undefined &&
                        openedDataset !== null &&
                        !viewingDataset)
            "
            toggleable="sm"
            fixed="bottom"
            style="border-top: 1px solid gray"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-navbar-nav v-if="openedDatasetLoading">
                <b-spinner
                    :variant="profile.darkMode ? 'light' : 'dark'"
                    small
                    class="mr-2"
                ></b-spinner>
            </b-navbar-nav>
            <b-navbar-nav
                v-else-if="
                    openedDataset !== null && openedDataset !== undefined
                "
            >
                <b :class="profile.darkMode ? 'text-white' : 'text-dark'">
                    <span v-if="openedDataset.opening">
                        <b-spinner
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            small
                            class="mr-2"
                        ></b-spinner
                        >Opening <b>{{ openedDataset.path }}</b> on
                        <b>{{ openedDataset.agent }}</b>
                    </span>
                    <span v-else>
                        <i class="far fa-folder-open fa-fw mr-2"></i>
                        <b>{{ openedDataset.path }}</b> open on
                        <b>{{ openedDataset.agent }}</b
                        >, {{ openedDataset.modified.length }} file(s)
                        modified</span
                    >
                </b></b-navbar-nav
            >
            <b-navbar-nav
                class="ml-auto"
                v-if="
                    openedDataset !== null &&
                        openedDataset !== undefined &&
                        openedDataset.opening
                "
            >
                <small>{{
                    openedDataset.output[openedDataset.output.length - 1]
                }}</small>
            </b-navbar-nav>
            <b-navbar-nav class="ml-auto" v-if="!openedDatasetLoading">
                <b-button
                    :variant="profile.darkMode ? 'outline-light' : 'white'"
                    title="View collection"
                    class="mr-2"
                    :to="{
                        name: 'collection',
                        params: { path: openedDataset.path }
                    }"
                >
                    View
                    <i class="fas fa-th fa-1x fa-fw"></i>
                </b-button>
                <b-dropdown
                    v-if="openedDataset.modified.length !== 0"
                    dropup
                    :variant="profile.darkMode ? 'outline-light' : 'white'"
                    class="mr-2"
                >
                    <template #button-content>
                        Save
                    </template>
                    <b-dropdown-item @click="saveSession(false)"
                        >All files</b-dropdown-item
                    >
                    <b-dropdown-item @click="saveSession(true)"
                        >Only modified files</b-dropdown-item
                    >
                </b-dropdown>
                <b-button
                    variant="outline-danger"
                    title="Close collection"
                    class="text-left m-0"
                    @click="closeDataset"
                >
                    Close
                    <i class="far fa-folder fa-1x fa-fw"></i>
                </b-button>
            </b-navbar-nav>
        </b-navbar>-->
        <b-toast
            auto-hide-delay="10000"
            v-if="$route.name !== 'run' && toastRun !== null"
            id="toast"
            :variant="profile.darkMode ? 'dark text-light' : 'light text-dark'"
            solid
        >
            <template #toast-title
                ><b-link
                    class="text-dark"
                    :to="{
                        name: 'run',
                        params: { id: toastRun.id }
                    }"
                    >{{ `Run ${toastRun.id}` }}</b-link
                ></template
            >
            <small>
                <b v-if="!toastRun.is_complete">Running</b>
                <b class="ml-0 mr-0" v-else>{{ toastRun.job_status }}</b>
                on
                <b>{{ toastRun.agent }}</b>
                {{ prettifyShort(toastRun.updated) }}
                <br />
                {{
                    toastRun.submission_logs[
                        toastRun.submission_logs.length - 1
                    ]
                }}
            </small>
        </b-toast>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';

export default {
    name: 'Navigation',
    components: {},
    data() {
        return {
            viewingDataset: false,
            // deployment target authentication
            authenticationUsername: '',
            authenticationPassword: '',
            // run status constants
            PENDING: 'PENDING',
            STARTED: 'STARTED',
            SUCCESS: 'SUCCESS',
            FAILURE: 'FAILURE',
            REVOKED: 'REVOKED',
            // websockets
            runSocket: null,
            notificationSocket: null,
            interactiveSocket: null,
            // user data
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            crumbs: [],
            notFound: false,
            titleContent: 'breadcrumb',
            currentRunPage: 0,
            loadingMoreRuns: false,
            toastRun: null,
            fields: [
                {
                    key: 'id',
                    label: 'Id',
                    sortable: true
                },
                {
                    key: 'state',
                    label: 'State'
                },
                {
                    key: 'created',
                    sortable: true,
                    formatter: value => {
                        return `${moment(value).fromNow()} (${moment(
                            value
                        ).format('h:mm a')})`;
                    }
                },
                {
                    key: 'workflow_name',
                    label: 'Workflow',
                    sortable: true
                }
            ],
            // run search
            runSearchText: ''
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('runs', ['runsLoading', 'runs']),
        ...mapGetters('notifications', [
            'notificationsLoading',
            'notifications'
        ]),
        ...mapGetters('datasets', ['openedDataset', 'openedDatasetLoading']),
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
                    r.tags.some(t => t.includes(this.runSearchText))
            );
        },
        filteredCompletedRuns() {
            return this.completedRuns.filter(
                r =>
                    (r.workflow_name !== null &&
                        r.workflow_name.includes(this.runSearchText)) ||
                    r.tags.some(t => t.includes(this.runSearchText))
            );
        },
        unreadNotifications() {
            return this.notifications.filter(n => !n.read);
        },
        readNotifications() {
            return this.notifications.filter(n => n.read);
        }
    },
    created: async function() {
        this.crumbs = this.$route.meta.crumb;
        this.viewingDataset = this.$router.currentRoute.name === 'dataset';
        let ws_protocol = location.protocol === 'https:' ? 'wss://' : 'ws://';

        // TODO move websockets to vuex

        // subscribe to run channel
        this.runSocket = new WebSocket(
            `${ws_protocol}${window.location.host}/ws/runs/${this.profile.djangoProfile.username}/`
        );
        this.runSocket.onmessage = this.onRunUpdate;

        // subscribe to notification channel
        this.notificationSocket = new WebSocket(
            `${ws_protocol}${window.location.host}/ws/notifications/${this.profile.djangoProfile.username}/`
        );
        this.notificationSocket.onmessage = this.onNotification;

        await Promise.all([
            this.$store.dispatch('runs/loadAll'),
            this.$store.dispatch('notifications/loadAll')
            // this.$store.dispatch('datasets/loadOpened')
        ]);
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
            this.viewingDataset = this.$router.currentRoute.name === 'dataset';
        },
        openedDataset() {
            // need this so the bottom navbar will hide itself after dataset is closed
        }
    },
    methods: {
        async closeDataset() {
            await this.$bvModal
                .msgBoxConfirm(
                    `Are you sure you want to close ${this.openedDataset.path} on ${this.openedDataset.agent}?`,
                    {
                        title: 'Close Dataset?',
                        size: 'sm',
                        okVariant: 'outline-danger',
                        cancelVariant: 'white',
                        okTitle: 'Yes',
                        cancelTitle: 'No',
                        centered: true
                    }
                )
                .then(async value => {
                    if (value)
                        await this.$store.dispatch('datasets/closeOpened');
                })
                .catch(err => {
                    throw err;
                });
        },
        markAllRead() {},
        markRead(notification) {
            axios({
                method: 'post',
                url: `/apis/v1/notifications/${this.profile.djangoProfile.username}/mark_read/`,
                data: {
                    notification: notification
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    this.$store.dispatch(
                        'updateNotification',
                        response.data.notification
                    );
                })
                .catch(error => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        // TODO move to VUEX
        async onRunUpdate(event) {
            let data = JSON.parse(event.data);
            var run = data.run;
            this.toastRun = run;
            this.$bvToast.show('toast');
            await this.$store.dispatch('runs/update', run);
        },
        async onNotification(event) {
            let data = JSON.parse(event.data);
            let notification = data.notification;
            await this.$store.dispatch('notifications/update', notification);
        },
        async onSessionEvent(event) {
            let data = JSON.parse(event.data);
            await this.$store.dispatch('datasets/updateOpened', data.session);
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
        now() {
            return moment().format('MMMM Do YYYY, h:mm:ss a');
        },
        logOut() {
            sessionStorage.clear();
            window.location.replace('/apis/v1/idp/cyverse_logout/');
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        }
    }
};
</script>

<style scoped lang="sass">
@import '../scss/main.sass'
@import '../scss/_colors.sass'



.not-found
    color: $red
    border: 2px solid $red
    -webkit-transform: rotate(180deg)
        transform: rotate(180deg)

.not-found:hover
    color: $dark
    border: 2px solid $white
    -webkit-transform: rotate(90deg)
        transform: rotate(90deg)

.mirror
    -moz-transform: scale(-1, 1)
    -webkit-transform: scale(-1, 1)
    -o-transform: scale(-1, 1)
    -ms-transform: scale(-1, 1)
    transform: scale(-1, 1)

.breadcrumb > li
    text-align: end
    margin-top: 12px !important
    font-size: 12pt !important
    font-weight: 200
    content: " /"

.breadcrumb > li + li::marker
    margin-top: 12px !important
    font-size: 12pt !important
    font-weight: 200

.breadcrumb > li + li:before + li::marker
    margin-top: 12px !important
    font-size: 12pt !important
    font-weight: 200
    content: " /"

.component-fade-enter-active, .component-fade-leave-active
    transition: opacity .1s ease

.component-fade-enter, .component-fade-leave-to
    opacity: 0

.brand-img
    -webkit-transition: -webkit-transform .1s ease-in-out
        transition: transform .1s ease-in-out

.brand-img:hover
    border: none
    color: white
    -webkit-transform: rotate(90deg)
    transform: rotate(90deg)

.github-hover:hover
  color: $color-highlight !important
  background-color: $dark !important


.avatar
  max-height: 15px
  border: 1px solid $dark

.crumb-dark
  font-size: 16px
  font-weight: 200
  color: white !important
  // text-decoration: underline
  // text-decoration-color: $color-button

.dropdown-custom:hover
  background-color: transparent !important

.crumb-light
  font-size: 16px
  font-weight: 200
  color: $dark !important

a
  text-decoration: none
  text-decoration-color: $color-button

a:hover
  text-decoration: underline
  text-decoration-color: $color-button

.darkk
  background-color: #292b2c
</style>
