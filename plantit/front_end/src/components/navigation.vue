<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="tasks"
            v-model="tasksSidebarOpen"
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
                            class="mr-0 pl-0 pt-0 pr-0"
                            align-self="center"
                            md="auto"
                        >
                            <b-button
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                class="text-left m-0"
                                @click="hide"
                            >
                                <i class="fas fa-arrow-left fa-1x fa-fw"></i>
                                Hide
                            </b-button>
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
                                    v-model="taskSearchText"
                                ></b-form-input>
                            </b-input-group>
                        </b-col>
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
                                Tasks
                            </h4>
                        </b-col>
                    </b-row>
                    <br />
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Running</b></b-col>
                    </b-row>
                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group
                                v-if="tasksRunning.length > 0"
                                class="text-left m-0 p-0"
                            >
                                <taskblurb
                                    v-for="task in filteredRunningTasks"
                                    v-bind:key="task.name"
                                    :task="task"
                                    :project="true"
                                ></taskblurb>
                                <!--<b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="task in filteredRunningTasks"
                                    v-bind:key="task.name"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light bg-dark m-0 p-2 mb-3 overflow-hidden'
                                            : 'text-dark bg-white m-0 p-2 mb-3 overflow-hidden'
                                    "
                                    :to="{
                                        name: 'task',
                                        params: {
                                            owner: task.owner,
                                            name: task.name
                                        }
                                    }"
                                >
                                    <b-img
                                        v-if="
                                            task.workflow_image_url !==
                                                undefined &&
                                                task.workflow_image_url !== null
                                        "
                                        rounded
                                        class="card-img-right"
                                        style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                        right
                                        :src="task.workflow_image_url"
                                    ></b-img>
                                    <b-link
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        :to="{
                                            name: 'task',
                                            params: {
                                                owner: task.owner,
                                                name: task.name
                                            }
                                        }"
                                        replace
                                        >{{ task.name }}</b-link
                                    ><span>
                                        v-if=" task.tags !== undefined &&
                                        task.tags.length > 0 " >
                                        <b-badge
                                            v-for="tag in task.tags"
                                            v-bind:key="tag"
                                            class="mr-1"
                                            variant="secondary"
                                            >{{ tag }}
                                        </b-badge>
                                    </span>
                                    <span v-if="task.project !== null">
                                        <b-badge class="mr-2" variant="info">{{
                                            task.project.title
                                        }}</b-badge
                                        ><small v-if="task.study !== null"
                                            ><b-badge
                                                class="mr-2"
                                                variant="info"
                                                >{{ task.study.title }}</b-badge
                                            ></small
                                        ></span
                                    >
                                    <br />
                                    <b-spinner
                                        class="mr-1"
                                        small
                                        v-if="!task.is_complete"
                                        variant="warning"
                                    >
                                    </b-spinner>
                                    <b-badge
                                        :variant="
                                            task.is_failure || task.is_timeout
                                                ? 'danger'
                                                : task.is_success
                                                ? 'success'
                                                : task.is_cancelled
                                                ? 'secondary'
                                                : 'warning'
                                        "
                                        >{{
                                            task.status.toUpperCase()
                                        }}</b-badge
                                    >
                                    <small> on </small>
                                    <b-badge
                                        class="ml-0 mr-0"
                                        variant="secondary"
                                        >{{ task.agent.name }}</b-badge
                                    ><small>
                                        {{ prettify(task.updated) }}</small
                                    >
                                    <br />
                                    <small
                                        v-if="task.workflow_name !== null"
                                        class="mr-1"
                                        ><a
                                            :class="
                                                profile.darkMode
                                                    ? 'text-light'
                                                    : 'text-dark'
                                            "
                                            :href="
                                                `https://github.com/${task.workflow_owner}/${task.workflow_name}`
                                            "
                                            ><i class="fab fa-github fa-fw"></i>
                                            {{ task.workflow_owner }}/{{
                                                task.workflow_name
                                            }}</a
                                        >
                                    </small>
                                </b-list-group-item>-->
                            </b-list-group>
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-center text-light pl-3 pr-3'
                                        : 'text-center text-dark pl-3 pr-3'
                                "
                                v-if="tasksRunning.length === 0"
                            >
                                No tasks are running right now.
                            </p>
                        </b-col></b-row
                    >
                    <br />
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Completed</b></b-col>
                    </b-row>

                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col
                            v-if="!tasksLoading && tasksCompleted.length > 0"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <b-list-group class="text-left m-0 p-0">
                                <taskblurb
                                    v-for="task in filteredCompletedTasks"
                                    v-bind:key="task.name"
                                    :task="task"
                                    :project="true"
                                ></taskblurb>
                                <!--<b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="task in filteredCompletedTasks"
                                    v-bind:key="task.name"
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
                                                    task.workflow_image_url !==
                                                        undefined &&
                                                        task.workflow_image_url !==
                                                            null
                                                "
                                                rounded
                                                class="card-img-right"
                                                style="max-width: 3rem;opacity: 0.8;position: absolute;right: -15px;top: -10px;z-index:1;"
                                                right
                                                :src="task.workflow_image_url"
                                            ></b-img>
                                            <b-link
                                                :class="
                                                    profile.darkMode
                                                        ? 'text-light mr-1'
                                                        : 'text-dark mr-1'
                                                "
                                                :to="{
                                                    name: 'task',
                                                    params: {
                                                        owner: task.owner,
                                                        name: task.name
                                                    }
                                                }"
                                                replace
                                                >{{ task.name }}</b-link
                                            ><span
                                                v-if="
                                                    task.tags !== undefined &&
                                                        task.tags.length > 0
                                                "
                                            >
                                                <b-badge
                                                    v-for="tag in task.tags"
                                                    v-bind:key="tag"
                                                    class="mr-2"
                                                    variant="secondary"
                                                    >{{ tag }}
                                                </b-badge>
                                            </span>
                                            <span v-if="task.project !== null">
                                                <b-badge
                                                    class="mr-2"
                                                    variant="info"
                                                    >{{
                                                        task.project.title
                                                    }}</b-badge
                                                ><small
                                                    v-if="task.study !== null"
                                                    ><b-badge
                                                        class="mr-2"
                                                        variant="info"
                                                        >{{
                                                            task.study.title
                                                        }}</b-badge
                                                    ></small
                                                ></span
                                            >
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col>
                                            <b-badge
                                                :variant="
                                                    task.is_failure ||
                                                    task.is_timeout
                                                        ? 'danger'
                                                        : task.is_success
                                                        ? 'success'
                                                        : task.is_cancelled
                                                        ? 'secondary'
                                                        : 'warning'
                                                "
                                                >{{
                                                    task.status.toUpperCase()
                                                }}</b-badge
                                            >
                                            <small> on </small>
                                            <b-badge
                                                class="ml-0 mr-0"
                                                variant="secondary"
                                                >{{ task.agent.name }}</b-badge
                                            ><small>
                                                {{
                                                    prettify(task.updated)
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
                                                        `https://github.com/${task.workflow_owner}/${task.workflow_name}`
                                                    "
                                                    ><i
                                                        class="fab fa-github fa-fw"
                                                    ></i>
                                                    {{ task.workflow_owner }}/{{
                                                        task.workflow_name
                                                    }}</a
                                                >
                                            </small>
                                        </b-col>
                                        </b-row
                                    >
                                    <b-modal
                                        :id="'remove ' + task.name"
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
                                        title="Delete this task?"
                                        @ok="removeTask(task)"
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
                                </b-list-group-item>-->
                            </b-list-group>
                        </b-col>
                        <b-col
                            v-if="tasksLoading"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <b-spinner
                                type="grow"
                                variant="secondary"
                            ></b-spinner
                        ></b-col>
                        <b-col
                            v-if="!tasksLoading && tasksCompleted.length === 0"
                            class="m-0 pl-0 pr-0 text-center"
                        >
                            <p
                                :class="
                                    profile.darkMode
                                        ? 'text-center text-light pl-3 pr-3'
                                        : 'text-center text-dark pl-3 pr-3'
                                "
                            >
                                No tasks completed.
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
            class="logo p-0 pt-1 pb-1"
            style="min-height: 40px; max-height: 40px; z-index: 1000"
            fixed="top"
            :type="profile.darkMode ? 'dark' : 'secondary'"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-collapse class="m-0 p-0" is-nav>
                <b-navbar-nav class="m-0 p-0 pl-3 mr-1">
                    <b-nav-item class="m-0 p-0" @click="showTasksSidebar">
                        <b-button
                            :class="
                                profile.loggedIn
                                    ? 'brand-img m-0 p-0'
                                    : 'brand-img-nl m-0 p-0'
                            "
                            variant="outline-white"
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
                    </b-nav-item>
                </b-navbar-nav>
                <transition name="component-fade" mode="out-in">
                    <b-breadcrumb
                        class="m-o p-0 mt-1"
                        style="background-color: transparent"
                        v-if="titleContent === 'sidebar'"
                    >
                        <b-breadcrumb-item
                            disabled
                            class="ml-4 mt-1"
                            :class="
                                profile.darkMode ? 'crumb-dark' : 'crumb-light'
                            "
                        >
                            <b
                                :class="
                                    profile.darkMode
                                        ? 'crumb-dark'
                                        : 'crumb-light'
                                "
                            >
                                View your tasks ({{
                                    tasksRunning.length
                                }}
                                running, {{ profile.stats.total_tasks }} total)
                            </b>
                        </b-breadcrumb-item>
                    </b-breadcrumb>
                    <b-navbar-nav class="m-0 p-0" align="center"
                        ><b-nav-item class="mt-1" href="/"
                            ><h4
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                                style="text-decoration: underline"
                            >
                                plant<small
                                    class="mb-3 text-success"
                                    style="
                                        text-decoration: underline;
                                        text-shadow: 1px 1px 2px black;
                                    "
                                    >it</small
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
                                ></small></h4
                        ></b-nav-item>
                        <b-nav-item
                            title="about"
                            to="/about"
                            class="mt-1"
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
                                >About</span
                            ></b-nav-item
                        >
                        <!--<b-nav-item
                            to="/beta"
                            class="mt-2"
                            :link-class="
                                profile.darkMode
                                    ? 'text-secondary'
                                    : 'text-dark'
                            "
                            title="Beta Test"
                            ><span
                                :class="
                                    profile.darkMode
                                        ? 'text-secondary'
                                        : 'text-dark'
                                "
                                ><i class="fas fa-vial fa-1x fa-fw"></i>Beta
                                Testing</span
                            ></b-nav-item
                        >-->
                        <b-nav-item
                            title="stats"
                            to="/stats"
                            class="mt-1"
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
                                >Stats</span
                            ></b-nav-item
                        >
                        <b-nav-item
                            title="docs"
                            href="https://plantit.readthedocs.io/en/latest"
                            class="mt-1"
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
                            class="mt-1"
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
                                >Github</span
                            >
                        </b-nav-item>
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
                </transition>
                <b-navbar-nav class="ml-auto p-0 m-0">
                    <b-nav-item
                        v-if="
                            profile.loggedIn
                                ? profile.githubProfile === null ||
                                  profile.githubProfile === undefined
                                : false
                        "
                        title="Log in to GitHub"
                        href="/apis/v1/idp/github_request_identity/"
                        class="p-0 mt-1 ml-0 mr-0"
                    >
                        <b-button
                            class="mt-2 text-left"
                            variant="warning"
                            size="md"
                        >
                            <i class="fab fa-github"></i>
                            Log in to GitHub
                        </b-button>
                    </b-nav-item>
                    <b-popover
                        :variant="profile.darkMode ? 'dark' : 'outline-light'"
                        v-if="profile.first && !ackedFirst"
                        triggers="manual"
                        :show.sync="profile.first"
                        target="usr"
                        placement="bottomleft"
                        >Welcome!
                        <hr />
                        The <i class="fas fa-question fa-fw"></i> icon in the
                        navigation bar indicates hints are enabled. Click
                        <b-badge
                            :variant="
                                profile.darkMode ? 'outline-dark' : 'light'
                            "
                            ><i class="fas fa-question-circle fa-fw"></i> Enable
                            Hints</b-badge
                        >, then try hovering the mouse over an option in the
                        context menu on the left side of the screen to trigger a
                        hint box.
                        <hr />
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
                        class="p-1 m-2 mr-0 ml-0"
                        :menu-class="
                            profile.darkMode ? 'theme-dark' : 'theme-light'
                        "
                        style="font-size: 14pt"
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
                                    class="fa-stack mr-2"
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
                                    v-if="profile.githubProfile"
                                    class="avatar m-0 mb-1 p-0 github-hover logo"
                                    style="
                                        min-width: 22px;
                                        min-height: 22px;
                                        position: relative;
                                        left: -3px;
                                        top: 1.5px;
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
                            title="Log Out"
                            @click="logOut"
                            class="text-danger"
                            link-class="text-danger"
                        >
                            <i class="fas fa-door-closed fa-1x fa-fw"></i>
                            Log Out
                        </b-dropdown-item>
                    </b-nav-item-dropdown>
                    <b-nav-item href="/apis/v1/idp/cyverse_login/" v-else>
                        <b-button
                            variant="white"
                            block
                            class="text-center mt-1"
                        >
                            Log in with
                            <b-img
                                :src="
                                    require('@/assets/sponsors/cyversebw-notext.png')
                                "
                                height="18px"
                                alt="Cyverse"
                            ></b-img>
                            <b>CyVerse</b>
                        </b-button>
                    </b-nav-item>
                </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        <b-navbar
            toggleable="md"
            class="p-0 pt-1 pb-2"
            style="height: 0px; z-index: 1000"
            fixed="bottom"
            :type="profile.darkMode ? 'dark' : 'secondary'"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-container fluid>
                <b-row
                    v-if="alerts.length > 0"
                    style="position: relative; top: -10px"
                >
                    <b-col>
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
        <br />
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
import moment from 'moment';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
import store from '@/store/store';
import taskblurb from '@/components/tasks/task-blurb.vue';
import { guid } from '@/utils';

export default {
    name: 'Navigation',
    components: {
        taskblurb,
    },
    data() {
        return {
            // user data
            ackedFirst: false,
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
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
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
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

        // no need to load user model if we're in about or stats view
        if (this.$route.name === 'about' || this.$route.name === 'stats') {
            await this.getVersion();
            return;
        }

        // otherwise need to fetch user profile first to get tokens/etc for other API requests
        await Promise.all([
            store.dispatch('user/loadProfile'),
            this.getVersion(),
        ]);

        // load the rest of the model
        await Promise.all([
            this.$store.dispatch('users/loadAll'),
            this.$store.dispatch('tasks/loadAll'),
            this.$store.dispatch('notifications/loadAll'),
            this.$store.dispatch('workflows/loadPublic'),
            this.$store.dispatch(
                'workflows/loadPersonal',
                this.profile.githubProfile.login
            ),
            this.$store.dispatch(
                'workflows/loadOrg',
                this.profile.githubProfile.login
            ),
            this.$store.dispatch('agents/loadPublic'),
            this.$store.dispatch(
                'agents/loadPersonal',
                this.profile.djangoProfile.username
            ),
            this.$store.dispatch(
                'agents/loadGuest',
                this.profile.djangoProfile.username
            ),
            this.$store.dispatch('datasets/loadPublic'),
            this.$store.dispatch('datasets/loadPersonal'),
            this.$store.dispatch('datasets/loadShared'),
            this.$store.dispatch('datasets/loadSharing'),
            this.$store.dispatch('projects/loadPersonal'),
            this.$store.dispatch('projects/loadOthers'),
        ]);

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
        hideFeedbackModal() {
            this.$bvModal.hide('feedback');
        },
        showTasksSidebar() {
            // this.$refs.tasks.show();
            if (this.profile.loggedIn) this.tasksSidebarOpen = true;
        },
        hideTasksSidebar() {
            this.tasksSidebarOpen = false;
        },
        brandEnter() {
            if (this.profile.loggedIn) {
                this.titleContent = 'sidebar';
            }
        },
        brandLeave() {
            this.titleContent = 'brand';
        },
        async getVersion() {
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
                await this.handleTask(data.task);
            } else if (data.notification !== undefined) {
                // notification event
                await this.handleNotification(data.notification);
            } else {
                // unrecognized event type
            }
        },
        async handleTask(task) {
            // this.taskToasted = task;
            // this.$bvToast.show('toast');
            await this.$store.dispatch('tasks/addOrUpdate', task);
            await this.$store.dispatch('alerts/add', {
                variant: 'success',
                message: `Task ${task.name} ${
                    !task.agent.is_local &&
                    !task.is_complete &&
                    task.job_status !== null
                        ? task.job_status.toUpperCase()
                        : task.status.toUpperCase()
                } on ${task.agent.name}: ${
                    task.orchestrator_logs[task.orchestrator_logs.length - 1]
                }`,
                guid: guid().toString(),
            });
        },
        async handleNotification(notification) {
            await this.$store.dispatch('notifications/update', notification);
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
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
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
  // text-decoration: underline
  // text-decoration-color: $color-button

.dropdown-custom:hover
  background-color: transparent !important
  border: 1px transparent !important
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
