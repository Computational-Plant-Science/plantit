<template>
    <div class="m-0 p-0 mb-4">
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
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                class="text-left m-0"
                                @click="hide"
                            >
                                Hide
                                <i class="fas fa-arrow-right fa-1x fa-fw"></i>
                            </b-button>
                        </b-col>
                    </b-row>
                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group
                                v-if="notificationsUnread.length > 0"
                                class="text-left m-0 p-0"
                            >
                                <b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="notification in notificationsUnread"
                                    v-bind:key="notification.id"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light bg-dark m-0 p-2 mb-2 overflow-hidden'
                                            : 'text-dark bg-white m-0 p-2 mb-2 overflow-hidden'
                                    "
                                >
                                    <b-row>
                                        <b-col>
                                            <p>
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
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                class="text-left m-0"
                                                @click="
                                                    markNotificationRead(
                                                        notification
                                                    )
                                                "
                                            >
                                                <i
                                                    class="fas fa-check fa-fw"
                                                ></i>
                                                Dismiss
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
                                v-if="notificationsUnread.length === 0"
                            >
                                No unread notifications.
                            </p>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="sm"
            class="logo py-0"
            fixed="top"
            :type="profile.darkMode ? 'dark' : 'secondary'"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-collapse is-nav align="center">
                <b-navbar-nav class="overflow-hidden" align="center"
                    ><b-nav-item class="overflow-hidden" href="/">
                        <h5
                            :class="
                                profile.darkMode ? 'text-white' : 'text-theme'
                            "
                            style="text-decoration: underline; z-index: 100"
                        >
                            <b-img
                                style="
                                    max-width: 1.5rem;
                                    position: absolute;
                                    top: -5px;
                                    left: 10px;
                                "
                                :src="require('../assets/logo.png')"
                                left
                                class="m-0 p-0"
                            ></b-img
                            >plant<small
                                class="text-success"
                                style="
                                    text-decoration: underline;
                                    text-shadow: 1px 1px 2px black;
                                    z-index: 100;
                                "
                                ><small>IT</small></small
                            >
                            <small
                                ><small
                                    ><small
                                        ><b-badge variant="success"
                                            ><span v-if="version !== 0">{{
                                                version
                                            }}</span
                                            ><i
                                                class="fas fa-spinner"
                                                v-else
                                            ></i></b-badge></small></small
                            ></small></h5
                    ></b-nav-item>
                    <b-row align-v="center" class="pl-3 pr-3">
                        <b-nav-item
                            title="about"
                            to="/about"
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
                                ><i
                                    class="fas fa-question-circle fa-1x fa-fw"
                                ></i
                                > About</span
                            ></b-nav-item
                        >
                        <b-nav-item
                            title="docs"
                            class="mr-1"
                            href="/apis/v1/swagger/"
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
                                ><i class="fas fa-laptop-code fa-1x fa-fw"></i
                                > API</span
                            ></b-nav-item
                        >
                        <b-nav-item
                            class="mr-1"
                            href="https://plantit.readthedocs.io/en/latest"
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
                                > Docs</span
                            ></b-nav-item
                        >
                        <b-nav-item
                            class="mr-1"
                            href="https://github.com/Computational-Plant-Science/plantit"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="github"
                        >
                            <span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fab fa-github fa-1x fa-fw"></i
                                > GitHub</span
                            >
                        </b-nav-item>
                        <b-nav-item
                            class="mr-1"
                            to="/stats"
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
                                ><i class="fas fa-chart-bar fa-1x fa-fw"></i
                                > Stats</span
                            ></b-nav-item
                        >
                        <b-nav-item
                            class="mr-1"
                            title="status"
                            href="https://stats.uptimerobot.com/yAgPxH7KNJ"
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
                                ><i
                                    class="fas fa-satellite-dish fa-1x fa-fw"
                                ></i
                                > Status</span
                            ></b-nav-item
                        >
                    </b-row>
                    <!--<b-nav-item
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
                        </b-nav-item>-->
                </b-navbar-nav>
                <b-navbar-nav class="ml-auto p-0 m-0">
                    <b-popover
                        :variant="profile.darkMode ? 'dark' : 'outline-light'"
                        v-if="profile.first && !ackedFirst"
                        triggers="manual"
                        :show.sync="profile.first"
                        target="usr"
                        placement="bottomleft"
                        ><h4 class="mt-2">Welcome!</h4>
                        <hr />
                        <h5>Hints</h5>
                        An <i class="fas fa-question fa-fw"></i> icon in the
                        navigation bar indicates hints are enabled. To see
                        hints, click
                        <b-badge
                            :variant="
                                profile.darkMode ? 'outline-dark' : 'light'
                            "
                            ><i class="fas fa-question-circle fa-fw"></i> Enable
                            Hints</b-badge
                        >, then try hovering the mouse over an option in the
                        context menu on the left side of the screen.
                        <b-button
                            block
                            size="sm"
                            class="mt-2 text-left"
                            title="Show hints"
                            @click="toggleHints"
                            :variant="
                                profile.darkMode ? 'outline-dark' : 'light'
                            "
                        >
                            <i class="fas fa-question-circle fa-fw"></i>
                            <span v-if="profile.hints"> Disable</span
                            ><span v-else> Enable</span> hints
                            <b-spinner
                                small
                                v-if="togglingHints"
                                label="Loading..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="ml-2 mb-1"
                            ></b-spinner>
                        </b-button>
                        <hr />
                        <h5>Workflows</h5>
                        You're ready to start submitting! Head over to
                        <b-badge
                            :variant="
                                profile.darkMode ? 'outline-dark' : 'light'
                            "
                            ><i class="fas fa-stream fa-fw"></i>
                            Workflows</b-badge
                        >
                        to explore available phenotyping tools.
                        <span v-if="!profile.loggedIntoGitHub"
                            >Note that to integrate your own workflows, you'll
                            first need to bind your GitHub account.
                            <b-button
                                class="mt-2 text-left"
                                :variant="
                                    profile.darkMode ? 'outline-dark' : 'light'
                                "
                                size="sm"
                                block
                                href="/apis/v1/idp/github_request_identity/"
                            >
                                <i class="fab fa-github fa-fw"></i>
                                Log in to GitHub
                            </b-button>
                        </span>
                        <hr />
                        <b-button
                            block
                            size="sm"
                            title="Hide"
                            @click="ackFirstLogin"
                            class="text-left mt-2 mb-2"
                            :variant="
                                profile.darkMode ? 'outline-dark' : 'light'
                            "
                            ><i class="fas fa-times fa-fw"></i>
                            Dismiss</b-button
                        ></b-popover
                    >
                    <b-nav-item-dropdown
                        id="usr"
                        right
                        v-if="profile.loggedIn"
                        :title="profile.djangoProfile.username"
                        class="p-0 mr-0 ml-0"
                        :menu-class="
                            profile.darkMode ? 'theme-dark' : 'theme-light'
                        "
                        style="font-size: 13pt"
                    >
                        <template #button-content>
                            <b-button
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                class="ml-0 mr-0 text-left dropdown-custom"
                                size="md"
                            >
                                <span
                                    :title="
                                        'Notifications (' +
                                        notificationsUnread.length +
                                        ')'
                                    "
                                    v-if="notificationsUnread.length > 0"
                                    class="mr-2"
                                    ><i
                                        v-if="profile.darkMode"
                                        class="fas fa-bell fa-1x text-light"
                                    ></i
                                    ><i
                                        v-else
                                        class="fas fa-bell fa-1x text-dark"
                                    ></i
                                ></span>
                                <span
                                    :title="'Showing Hints'"
                                    v-if="profile.hints"
                                    class="mr-2"
                                    ><i
                                        v-if="profile.darkMode"
                                        class="fas fa-question fa-1x text-light"
                                    ></i
                                    ><i
                                        v-else
                                        class="fas fa-question fa-1x text-dark"
                                    ></i
                                ></span>
                                <b-img
                                    id="avatar"
                                    v-if="profile.loggedIntoGitHub"
                                    class="avatar m-0 mb-1 p-0 github-hover logo"
                                    style="
                                        min-width: 20px;
                                        min-height: 20px;
                                        position: relative;
                                        left: -3px;
                                        top: 0.5px;
                                        border: 1px solid #e2e3b0;
                                    "
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
                        <b-dropdown-item
                            title="Home"
                            to="/home/"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-desktop fa-1x fa-fw"></i>
                            Home
                        </b-dropdown-item>
                        <b-dropdown-item
                            :title="
                                'Notifications (' +
                                notificationsUnread.length +
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
                            <span v-if="notificationsUnread.length > 0"
                                >({{ notificationsUnread.length }} unread)</span
                            >
                        </b-dropdown-item>
                        <b-dropdown-item
                            :title="
                                profile.darkMode ? 'Light Mode' : 'Dark Mode'
                            "
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            @click="toggleDarkMode"
                        >
                            <b-spinner
                                small
                                v-if="togglingDarkMode"
                                label="Loading..."
                                :variant="profile.darkMode ? 'light' : 'dark'"
                                class="ml-2 mb-1"
                            ></b-spinner
                            ><span v-else-if="profile.darkMode"
                                ><i class="fas fa-sun fa-fw"></i> Light
                                Mode</span
                            ><span v-else
                                ><i class="fas fa-moon fa-fw"></i> Dark
                                Mode</span
                            ></b-dropdown-item
                        >
                        <b-dropdown-item
                            title="Toggle Hints"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            @click="toggleHints"
                        >
                            <i class="fas fa-question-circle fa-fw"></i>
                            <b-spinner
                                small
                                v-if="togglingHints"
                                label="Loading..."
                                :variant="profile.hints ? 'light' : 'dark'"
                                class="ml-2 mb-1"
                            ></b-spinner>
                            <span v-else-if="profile.hints"> Hide</span
                            ><span v-else> Show</span> Hints</b-dropdown-item
                        >
                        <b-dropdown-item
                            title="
                                Feedback
                            "
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            @click="showFeedbackModal"
                        >
                            <i class="fas fa-comment-alt fa-1x fa-fw"></i>
                            Feedback
                        </b-dropdown-item>
                        <b-dropdown-item
                            title="
                               Contact
                            "
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            href="mailto:wbonelli@uga.edu"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-envelope fa-1x fa-fw"></i>
                            Contact
                        </b-dropdown-item>
                        <b-dropdown-item
                            v-if="!profile.loggedIntoGitHub"
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            title="Log in to GitHub"
                            href="/apis/v1/idp/github_request_identity/"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fab fa-github fa-fw"></i>
                            Log in to GitHub
                        </b-dropdown-item>
                        <b-dropdown-item
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            title="DIRT migration"
                            @click="showDirtMigrationModal"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                        >
                            <i class="fas fa-folder-open fa-fw"></i>
                            DIRT Migration
                            <i
                                v-if="!profileLoading && profile.migration.completed !== null"
                                class="fas fa-check text-success fa-fw"
                            ></i>
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
                    <b-nav-item
                        href="/apis/v1/idp/cyverse_login/"
                        v-else-if="maintenance === undefined && !profileLoading"
                    >
                        <b-button
                            variant="white"
                            block
                            size="sm"
                            class="text-center"
                        >
                            Log in with
                            <b-img
                                :src="
                                    require('@/assets/sponsors/cyversebw-notext.png')
                                "
                                height="14px"
                                alt="Cyverse"
                            ></b-img>
                            <b>CyVerse</b>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <b-navbar
            v-if="profile.loggedIn"
            toggleable="md"
            class="p-0 pt-1 pb-2"
            style="height: 0px; z-index: 1000"
            fixed="bottom"
            :type="profile.darkMode ? 'dark' : 'secondary'"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-container fluid class="p-0 m-0">
                <b-row style="position: relative; top: -10px">
                    <!--<b-col md="auto"
                        ><b-navbar-nav class="m-0 p-0 mr-1">
                            <b-nav-item
                                class="m-0 p-0"
                                @click="showTasksSidebar"
                            >
                                <b-button
                                    :class="
                                        profile.loggedIn
                                            ? 'brand-img m-0 p-0'
                                            : 'brand-img-nl m-0 p-0'
                                    "
                                    variant="outline-white"
                                    @click="showTasksSidebar"
                                    @mouseenter="brandEnter"
                                    @mouseleave="brandLeave"
                                >
                                    <b-img
                                        class="m-0 p-0 mb-3"
                                        center
                                        width="30px"
                                        :src="require('../assets/logo.png')"
                                        alt="Plant IT"
                                    ></b-img>
                                </b-button>
                            </b-nav-item> </b-navbar-nav
                    ></b-col>-->
                    <b-col v-if="titleContent === 'sidebar'" md="auto">
                        <b-alert
                            class="m-0"
                            :variant="profile.darkMode ? 'dark' : 'light'"
                            :show="true"
                        >
                            <b>
                                View your tasks ({{ tasksRunning.length }}
                                running,
                                {{ profile.stats.total_tasks }} total)
                            </b>
                        </b-alert>
                    </b-col>
                    <b-col v-if="alerts.length > 0">
                        <b-alert
                            class="m-0"
                            :show="dismissCountDown"
                            :variant="alerts[0].variant"
                            dismissible
                            @dismissed="dismissCountDown = 0"
                            @dismiss-count-down="countdownChanged"
                            ><b>{{ alerts[0].message }}</b>
                            {{ prettifyShort(alerts[0].time)
                            }}<b-progress
                                variant="dark"
                                :max="dismissSecs"
                                :value="dismissCountDown"
                                height="4px"
                            ></b-progress
                        ></b-alert>
                    </b-col>
                </b-row>
            </b-container>
        </b-navbar>
        <br />
        <div class="mt-2" v-if="maintenance !== undefined">
            <b-alert variant="warning" :show="true"
                >CyVerse is undergoing maintenance scheduled to complete
                {{ prettify(maintenance.end) }}. You will be logged out in a few
                moments.</b-alert
            >
        </div>
        <b-modal
            v-if="!profileLoading && this.profile.migration !== null"
            id="migration"
            title="DIRT Migration"
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
            :body-text-variant="profile.darkMode ? 'white' : 'dark'"
            hide-footer
            busy
        >
            <template #modal-header
                ><h4 :class="profile.darkMode ? 'text-white' : 'text-dark'">
                    <i class="fas fa-folder-open fa-fw"></i> DIRT Migration
                </h4></template
            >
            <b-row v-if="profile.migration.completed === null">
                <b-col>
                    <p v-if="profile.migration.started === null">
                        You haven't migrated your datasets from DIRT yet.
                    </p>
                    <b-alert :show="migrationDataDuplicate" variant="danger">
                        You already have a collection with path
                        <code
                            >/iplant/home/{{
                                profile.djangoProfile.username
                            }}/dirt_migration</code
                        >. Please rename this collection to allow the migration
                        to proceed.
                    </b-alert>
                    <b-button
                        :disabled="
                            migrationSubmitting ||
                            profile.migration.started !== null ||
                            (profile.migration.started !== null &&
                                profile.migration.completed === null)
                        "
                        @click="startDirtMigration"
                        :variant="
                            profile.darkMode ? 'outline-success' : 'success'
                        "
                        block
                    >
                        <b-spinner
                            small
                            v-if="
                                migrationSubmitting ||
                                profile.migration.started !== null ||
                                (profile.migration.started !== null &&
                                    profile.migration.completed === null)
                            "
                            label="Running..."
                            variant="dark"
                            class="mr-2"
                        ></b-spinner
                        ><i v-else class="fas fa-chevron-right fa-fw mr-1"></i>
                        {{
                            migrationSubmitting ||
                            profile.migration.started !== null
                                ? 'Running'
                                : 'Start'
                        }}</b-button
                    >
                    <p v-if="profile.migration.started !== null">
                        <br />
                        <span v-if="profile.migration.num_folders !== null"
                            >You have
                            {{ profile.migration.num_folders }} dataset(s) to
                            migrate,
                            {{
                                profile.migration.num_folders === null
                                    ? '?'
                                    : profile.migration.num_folders -
                                      uploadedFolders.length + 1
                            }}
                            remaining.</span
                        >
                        <b-progress
                            v-if="profile.migration.num_folders !== null"
                            :value="uploadedFolders.length"
                            :max="profile.migration.num_folders"
                            animated
                            variant="success"
                        ></b-progress>
                        <br />
                        <b>Started:</b>
                        {{ prettify(profile.migration.started) }}
                        <br />
                        <b>Collection:</b>
                        {{ profile.migration.target_path }}
                        <br />
                        <b-list-group
                            style="
                                max-height: 10rem;
                                overflow: scroll;
                                -webkit-overflow-scrolling: touch;
                            "
                        >
                            <b-list-group-item
                                :variant="profile.darkMode ? 'dark' : 'light'"
                                v-for="folder in uploadedFolders"
                                v-bind:key="folder.name"
                            >
                                <i
                                    class="fas text-success fa-check fa-1x fa-fw"
                                ></i>
                                {{ folder.name }},
                                {{ folder.files.length }} file(s)
                            </b-list-group-item>
                        </b-list-group>
                    </p>
                </b-col>
            </b-row>
            <b-row v-else
                ><b-col>
                    <p>
                        Your datasets have been successfully migrated from DIRT.
                    </p>
                    <p>
                        <b>Started:</b>
                        {{ prettify(profile.migration.started) }}
                        <br />
                        <b>Completed:</b>
                        {{ prettify(profile.migration.completed) }}
                        <br />
                        <b>Collection:</b>
                        {{ profile.migration.target_path }}
                    </p>
                </b-col>
            </b-row>
        </b-modal>
        <b-modal
            id="feedback"
            title="Thanks for your feedback!"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            size="xl"
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :body-text-variant="profile.darkMode ? 'white' : 'dark'"
            ok-variant="success"
            :ok-disabled="!feedbackValid"
            @ok="submitFeedback"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                Feel free to answer one or more of the following questions, or
                <b-link
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    href="mailto:wbonelli@uga.edu"
                    >send us an email</b-link
                >
                to share free-form feedback.
            </p>
            <br />
            <b>Has PlantIT helped you?</b>
            <b-form-textarea
                :class="profile.darkMode ? 'input-dark' : 'input-light'"
                v-model="feedbackUsed"
                placeholder="How have you used PlantIT? Do you have any success stories?"
            ></b-form-textarea>
            <br />
            <b>How could PlantIT be better?</b>
            <b-form-textarea
                :class="profile.darkMode ? 'input-dark' : 'input-light'"
                v-model="feedbackWanted"
                placeholder="How could PlantIT better serve your use case? Have you found anything frustrating?"
            ></b-form-textarea>
            <br />
            <b>Could PlantIT be more accessible?</b>
            <b-form-textarea
                :class="profile.darkMode ? 'input-dark' : 'input-light'"
                v-model="feedbackEase"
                placeholder="Can you think of anything that might make PlantIT easier to use?"
            ></b-form-textarea>
            <br />
            <b>Do you have feature requests?</b>
            <b-form-textarea
                :class="profile.darkMode ? 'input-dark' : 'input-light'"
                v-model="feedbackFeatures"
                placeholder="Are there any particular features you'd like to see in PlantIT?"
            ></b-form-textarea>
            <br />
            <b-form-checkbox
                :class="profile.darkMode ? 'input-dark' : 'input-light'"
                v-model="feedbackAnonymous"
                ><b>Anonymize?</b> By default all feedback is anonymous. Uncheck
                this box if you'd like us to be able to see who you are. We
                might get in touch to ask if we can display your comments on the
                site!</b-form-checkbox
            >
        </b-modal>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment-timezone';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import jwtDecode from 'jwt-decode';
import { guid } from '@/utils';

export default {
    name: 'Navigation',
    data() {
        return {
            // user data
            ackedFirst: false,
            // websockets
            socket: null,
            // breadcrumb & brand
            crumbs: [],
            titleContent: 'brand',
            // task sidebar & toasts
            taskPage: 0,
            taskToasted: null,
            taskSearchText: '',
            tasksSidebarOpen: false,
            // flags
            togglingDarkMode: false,
            togglingHints: false,
            notFound: false,
            // version
            version: 0,
            // feedback
            feedbackUsed: '',
            feedbackWanted: '',
            feedbackEase: '',
            feedbackFeatures: '',
            feedbackAnonymous: true,
            // alert countdown
            dismissSecs: 10,
            dismissCountDown: 0,
            maintenanceWindows: [],
            // DIRT migration
            migrationDataDuplicate: false,
            migrationSubmitting: false,
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('alerts', ['alerts']),
        ...mapGetters('tasks', [
            'tasks',
            'tasksLoading',
            'tasksRunning',
            'tasksCompleted',
        ]),
        ...mapGetters('notifications', [
            'notifications',
            'notificationsLoading',
            'notificationsRead',
            'notificationsUnread',
        ]),
        storageFolders() {
            if (this.profileLoading || this.profile === null || this.profile.migration.storage.length === 0) return [];
            let grouped = this.groupBy(
                this.profile.migration.storage,
                'folder'
            );
            return Object.entries(grouped).map((pair) => {
                return { name: pair[0], files: pair[1] };
            });
        },
        uploadedFolders() {
            if (this.profileLoading || this.profile === null || this.profile.migration.uploads.length === 0) return [];
            let grouped = this.groupBy(
                this.profile.migration.uploads,
                'folder'
            );
            return Object.entries(grouped).map((pair) => {
                return { name: pair[0], files: pair[1] };
            });
        },
        maintenance() {
            let now = moment();
            return this.maintenanceWindows.find((w) => {
                let start = moment(w.start);
                let end = moment(w.end);
                return start.isBefore(now) && end.isAfter(now);
            });
        },
        feedbackValid() {
            return (
                this.feedbackUsed !== '' ||
                this.feedbackWanted !== '' ||
                this.feedbackEase !== '' ||
                this.feedbackFeatures !== ''
            );
        },
        filteredRunningTasks() {
            return this.tasksRunning.filter(
                (sub) =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.taskSearchText)) ||
                    sub.tags.some((tag) => tag.includes(this.taskSearchText))
            );
        },
        filteredCompletedTasks() {
            return this.tasksCompleted.filter(
                (sub) =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.taskSearchText)) ||
                    sub.tags.some((tag) => tag.includes(this.taskSearchText))
            );
        },
    },
    created: async function () {
        this.crumbs = this.$route.meta.crumb;

        // no need to load all user data if we're in the about or stats view
        if (this.$route.name === 'about' || this.$route.name === 'stats') {
            await Promise.all([
                this.getVersion(),
                this.$store.dispatch('workflows/loadPublic'),
                // this.$store.dispatch('datasets/loadPublic'),
            ]);
            return;
        }

        let begin = Date.now();
        console.log(begin);

        await Promise.all([
            this.loadVersion(),
            this.loadDataModel(),
            this.loadMaintenanceWindows(),
        ]);

        let timing = Date.now() - begin;
        console.log('Load time: ' + timing + 'ms');

        // TODO move websockets to vuex
        // connect to this user's event stream, pushed from backend channel
        let wsProtocol = location.protocol === 'https:' ? 'wss://' : 'ws://';
        this.socket = new WebSocket(
            `${wsProtocol}${window.location.host}/ws/${this.profile.djangoProfile.username}/`
        );
        this.socket.onmessage = this.handleUserEvent;
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        },
        alerts() {
            this.dismissCountDown = this.dismissSecs;
        },
    },
    methods: {
        // https://stackoverflow.com/a/34890276
        groupBy(xs, key) {
            return xs.reduce(function (rv, x) {
                (rv[x[key]] = rv[x[key]] || []).push(x);
                return rv;
            }, {});
        },
        showDirtMigrationModal() {
            this.$bvModal.show('migration');
        },
        hideDirtMigrationModal() {
            this.$bvModal.hide('migration');
        },
        startDirtMigration() {
            this.migrationDataDuplicate = false;
            this.migrationSubmitting = true;
            axios
                .get(`/apis/v1/users/start_dirt_migration/`)
                .then(async (response) => {
                    await Promise.all([
                        this.$store.dispatch(
                            'user/setDirtMigration',
                            response.data.migration
                        ),
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Started DIRT migration (target collection: ${response.data.migration.target_path})`,
                            guid: guid().toString(),
                        }),
                    ]);
                    this.migrationSubmitting = false;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (
                        error.response.status === 400 &&
                        error.response.data.includes(
                            'migration collection already exists'
                        )
                    ) {
                        this.migrationDataDuplicate = true;
                    }
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to start DIRT migration`,
                        guid: guid().toString(),
                    });
                    this.migrationSubmitting = false;
                    if (error.response.status === 500) throw error;
                });
        },
        async loadDataModel() {
            // feature flag to toggle between the old/new state loading method
            if (process.env.VUE_APP_LOAD_STATE_SEPARATELY) {
                await this.$store.dispatch('user/loadProfile');
                await Promise.all([
                    this.$store.dispatch('users/loadAll'),
                    this.$store.dispatch('tasks/loadAll'),
                    this.$store.dispatch('tasks/loadDelayed'),
                    this.$store.dispatch('tasks/loadRepeating'),
                    this.$store.dispatch('notifications/loadAll'),
                    this.$store.dispatch('workflows/loadPublic'),
                    this.$store.dispatch('workflows/loadUser'),
                    this.$store.dispatch('workflows/loadOrg'),
                    this.$store.dispatch('workflows/loadProject'),
                    this.$store.dispatch('agents/loadAll'),
                    this.$store.dispatch('datasets/loadPublic'),
                    this.$store.dispatch('datasets/loadUser'),
                    this.$store.dispatch('datasets/loadShared'),
                    this.$store.dispatch('datasets/loadSharing'),
                    this.$store.dispatch('projects/loadUser'),
                    this.$store.dispatch('projects/loadOthers'),
                ]);
                return;
            }

            await this.$store.dispatch('user/setProfileLoading', true);
            await axios
                .get(`/apis/v1/users/get_current/`)
                .then((response) => {
                    // determine whether user is logged into CyVerse
                    let decoded = jwtDecode(
                        response.data.django_profile.cyverse_token
                    );
                    let now = Math.floor(Date.now() / 1000);
                    if (now > decoded.exp)
                        this.$store.dispatch('user/setLoggedIn', false);
                    else this.$store.dispatch('user/setLoggedIn', true);

                    // determine whether user is logged into GitHub
                    this.$store.dispatch(
                        'user/setLoggedIntoGithub',
                        response.data.github_profile !== undefined &&
                            response.data.github_profile !== null
                    );

                    // load user profile info into Vuex
                    this.$store.dispatch(
                        'user/setDjangoProfile',
                        response.data.django_profile
                    );
                    this.$store.dispatch(
                        'user/setCyverseProfile',
                        response.data.cyverse_profile
                    );
                    this.$store.dispatch(
                        'user/setGithubProfile',
                        response.data.github_profile
                    );
                    this.$store.dispatch(
                        'user/setOrganizations',
                        response.data.organizations
                    );
                    this.$store.dispatch(
                        'user/setFirst',
                        response.data.django_profile.first
                    );
                    this.$store.dispatch(
                        'user/setDarkMode',
                        response.data.django_profile.dark_mode
                    );
                    this.$store.dispatch(
                        'user/setHints',
                        response.data.django_profile.hints
                    );
                    this.$store.dispatch(
                        'user/setPushNotifications',
                        response.data.django_profile.push_notifications
                    );
                    this.$store.dispatch('user/setStats', response.data.stats);
                    this.$store.dispatch(
                        'user/setDirtMigration',
                        response.data.migration
                    );
                    this.$store.dispatch('user/setProfileLoading', false);

                    // load notifications into Vuex
                    this.$store.dispatch(
                        'notifications/setAll',
                        response.data.notifications
                    );
                    this.$store.dispatch('notifications/setLoading', false);

                    // load other users into Vuex
                    this.$store.dispatch('users/setAll', response.data.users);
                    this.$store.dispatch('users/setLoading', false);

                    // load tasks into Vuex
                    this.$store.dispatch(
                        'tasks/setAll',
                        response.data.tasks.tasks
                    );
                    this.$store.dispatch(
                        'tasks/setDelayed',
                        response.data.delayed_tasks
                    );
                    this.$store.dispatch(
                        'tasks/setRepeating',
                        response.data.repeating_tasks
                    );
                    this.$store.dispatch(
                        'tasks/setTriggered',
                        response.data.triggered_tasks
                    );
                    this.$store.dispatch('tasks/setLoading', false);

                    // load workflows into Vuex
                    this.$store.dispatch(
                        'workflows/setPublic',
                        response.data.workflows.public
                    );
                    this.$store.dispatch(
                        'workflows/setUser',
                        response.data.workflows.user
                    );
                    this.$store.dispatch(
                        'workflows/setOrg',
                        response.data.workflows.org
                    );
                    this.$store.dispatch(
                        'workflows/loadProject',
                        response.data.workflows.project
                    );
                    this.$store.dispatch('workflows/setPublicLoading', false);
                    this.$store.dispatch('workflows/setUserLoading', false);
                    this.$store.dispatch('workflows/setOrgLoading', false);
                    this.$store.dispatch('workflows/setProjectLoading', false);

                    // load agents into Vuex
                    this.$store.dispatch('agents/setAll', response.data.agents);
                    this.$store.dispatch('agents/setLoading', false);

                    // load projects into Vuex
                    this.$store.dispatch(
                        'projects/setUser',
                        response.data.projects
                    );
                    this.$store.dispatch(
                        'projects/setOthers',
                        response.data.projects
                    );
                    this.$store.dispatch('projects/setLoading', false);
                })

                .catch((error) => {
                    this.$store.dispatch('user/setProfileLoading', false);
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                    else if (
                        error.response.status === 401 ||
                        error.response.status === 403
                    ) {
                        // if we get a 401 or 403, log the user out
                        sessionStorage.clear();
                        window.location.replace('/apis/v1/idp/cyverse_logout/');
                    }
                });
            await this.loadDatasets();
        },
        async loadDatasets() {
            await Promise.all([
                this.$store.dispatch('datasets/loadPublic'),
                this.$store.dispatch('datasets/loadUser'),
                this.$store.dispatch('datasets/loadShared'),
                this.$store.dispatch('datasets/loadSharing'),
            ]);
        },
        async loadMaintenanceWindows() {
            await axios
                .get('/apis/v1/misc/maintenance/')
                .then((response) => {
                    this.maintenanceWindows = response.data.windows;
                    if (this.maintenance !== undefined)
                        setInterval(this.logOut, 5000);
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        async ackFirstLogin() {
            await axios({
                method: 'get',
                url: `/apis/v1/users/acknowledge_first_login/`,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch('user/setFirst', false);
                        this.ackedFirst = true;
                    }
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to connect to ${this.agentName}`,
                        guid: guid().toString(),
                        time: moment().format(),
                    });
                    throw error;
                });
        },
        countdownChanged(dismissCountDown) {
            this.dismissCountDown = dismissCountDown;
        },
        async submitFeedback() {
            if (!this.feedbackValid) return;
            let data = {
                used: this.feedbackUsed,
                wanted: this.feedbackWanted,
                ease: this.feedbackEase,
                features: this.feedbackFeatures,
                anonymous: this.feedbackAnonymous,
            };
            await axios({
                method: 'post',
                url: `/apis/v1/feedback/`,
                headers: { 'Content-Type': 'application/json' },
                data: data,
            })
                .then(() => {
                    alert('Submitted feedback!');
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        showFeedbackModal() {
            this.$bvModal.show('feedback');
        },
        showTasksSidebar() {
            // this.$refs.tasks.show();
            if (this.profile.loggedIn) this.tasksSidebarOpen = true;
        },
        brandEnter() {
            if (this.profile.loggedIn) {
                this.titleContent = 'sidebar';
            }
        },
        brandLeave() {
            this.titleContent = 'brand';
        },
        async loadVersion() {
            await axios({
                method: 'get',
                url: `https://api.github.com/repos/Computational-Plant-Science/plantit/tags`,
                headers: { 'Content-Type': 'application/json' },
            })
                .then((response) => {
                    this.version = response.data[0].name;
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        removeAlert(alert) {
            this.$store.dispatch('alerts/remove', alert);
        },
        async toggleDarkMode() {
            this.togglingDarkMode = true;
            await this.$store.dispatch('user/toggleDarkMode');
            this.togglingDarkMode = false;
        },
        async toggleHints() {
            this.togglingHints = true;
            await this.$store.dispatch('user/toggleHints');
            this.togglingHints = false;
        },
        markAllNotificationsRead() {
            // TODO
        },
        async markNotificationRead(notification) {
            await axios({
                method: 'delete',
                url: `/apis/v1/notifications/${this.profile.djangoProfile.username}/${notification.id}/`,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    await this.$store.dispatch(
                        'notifications/setAll',
                        response.data.notifications
                    );
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        async handleUserEvent(event) {
            let data = JSON.parse(event.data);
            if (data.task !== undefined) {
                // task event
                await this.handleTaskEvent(data.task);
            } else if (data.notification !== undefined) {
                // notification event
                await this.handleNotificationEvent(data.notification);
            } else if (data.migration !== undefined) {
                // DIRT migration status event
                await this.handleMigrationEvent(data.migration);
            } else {
                // TODO: log unrecognized event type
            }
        },
        async handleMigrationEvent(migration) {
            await this.$store.dispatch('user/setDirtMigration', migration);

            // check if completed and update user profile & create an alert if so
            let completed = migration.completed;
            if (completed !== null && completed !== undefined)
                await this.$store.dispatch('alerts/add', {
                    variant: 'success',
                    message: `DIRT migration completed (target collection: ${migration.target_path})`,
                    guid: guid().toString(),
                });
        },
        async handleNotificationEvent(notification) {
            await this.$store.dispatch('notifications/update', notification);
        },
        async handleTaskEvent(task) {
            await this.$store.dispatch('tasks/addOrUpdate', task);
            await this.$store.dispatch('alerts/add', {
                variant: 'success',
                message: `Task ${task.name} ${this.getTaskStatus(task)} on ${
                    task.agent.name
                }: ${
                    task.orchestrator_logs[task.orchestrator_logs.length - 1]
                }`,
                guid: guid().toString(),
            });
        },
        getTaskStatus(task) {
            if (!task.is_complete) {
                if (task.job_status === null) return task.status.toUpperCase();
                else return task.job_status.toUpperCase();
            }
            return task.status.toUpperCase();
        },
        removeTask(task) {
            axios
                .get(`/apis/v1/tasks/${task.owner}/${task.name}/delete/`)
                .then((response) => {
                    if (response.status === 200) {
                        this.showCanceledAlert = true;
                        this.canceledAlertMessage = response.data;
                        this.$store.dispatch('tasks/loadAll');
                        if (
                            this.$router.currentRoute.name === 'task' &&
                            task.name === this.$router.currentRoute.params.name
                        )
                            router.push({
                                name: 'user',
                                params: {
                                    username:
                                        this.profile.djangoProfile.username,
                                },
                            });
                    } else {
                        this.showFailedToCancelAlert = true;
                    }
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    return error;
                });
        },
        showDeletePrompt(task) {
            this.$bvModal.show('remove ' + task.name);
        },
        now() {
            return moment().format('MMMM Do YYYY, h:mm:ss a');
        },
        logOut() {
            sessionStorage.clear();
            window.location.replace('/apis/v1/idp/cyverse_logout/');
        },
        prettify: function (date) {
            let tz = moment.tz.guess();
            let mom = moment(date).tz(tz);
            return `${mom.fromNow()} (${mom.format('MMMM Do YYYY, h:mm a')})`;
        },
        prettifyShort: function (date) {
            return `${moment(date).fromNow()}`;
        },
    },
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

.brand-img-nl
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
    font-size: 14px
    font-weight: 400
    color: white !important

.dropdown-custom
    border: none !important

.dropdown-custom:hover
    background-color: transparent !important
    border: none !important
    box-shadow: none !important

.crumb-light
    font-size: 14px
    font-weight: 400
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
