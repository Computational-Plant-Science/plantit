<template>
    <div class="m-0 p-0">
        <b-sidebar
            id="tasks"
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
                                Tasks
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
                                    v-model="taskSearchText"
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
                                <b-list-group-item
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
                                    >
                                    <br />
                                    <div
                                        v-if="
                                            task.tags !== undefined &&
                                                task.tags.length > 0
                                        "
                                    >
                                        <b-badge
                                            v-for="tag in task.tags"
                                            v-bind:key="tag"
                                            class="mr-1"
                                            variant="secondary"
                                            >{{ tag }}
                                        </b-badge>
                                        <br />
                                    </div>
                                    <small v-if="!task.is_complete"
                                        >Running</small
                                    >
                                    <b-badge
                                        :variant="
                                            task.is_failure || task.is_timeout
                                                ? 'danger'
                                                : task.is_cancelled
                                                ? 'secondary'
                                                : 'success'
                                        "
                                        v-else
                                        >{{ task.job_status }}</b-badge
                                    >
                                    <small> on </small>
                                    <b-badge
                                        class="ml-0 mr-0"
                                        variant="secondary"
                                        >{{ task.agent }}</b-badge
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
                                </b-list-group-item>
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
                                <b-list-group-item
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
                                            >
                                        </b-col>
                                    </b-row>
                                    <b-row
                                        ><b-col>
                                            <div
                                                v-if="
                                                    task.tags !== undefined &&
                                                        task.tags.length > 0
                                                "
                                            >
                                                <b-badge
                                                    v-for="tag in task.tags"
                                                    v-bind:key="tag"
                                                    class="mr-1"
                                                    variant="secondary"
                                                    >{{ tag }}
                                                </b-badge>
                                                <br
                                                    v-if="task.tags.length > 0"
                                                />
                                            </div>
                                            <small v-if="!task.is_complete"
                                                >Running</small
                                            >
                                            <b-badge
                                                :variant="
                                                    task.is_failure ||
                                                    task.is_timeout
                                                        ? 'danger'
                                                        : task.is_cancelled
                                                        ? 'secondary'
                                                        : 'success'
                                                "
                                                v-else
                                                >{{ task.job_status }}</b-badge
                                            >
                                            <small> on </small>
                                            <b-badge
                                                class="ml-0 mr-0"
                                                variant="secondary"
                                                >{{ task.agent }}</b-badge
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
                                        <b-col md="auto">
                                            <b-button
                                                v-if="task.is_complete"
                                                variant="outline-danger"
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Delete Run"
                                                class="text-right"
                                                @click="showDeletePrompt(task)"
                                            >
                                                <i class="fas fa-trash"></i>
                                                Delete
                                            </b-button>
                                        </b-col></b-row
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
                                </b-list-group-item>
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
                                No workflow tasks.
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
                    <br />
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Unread</b></b-col>
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
                                                @click="
                                                    markNotificationRead(
                                                        notification
                                                    )
                                                "
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
                                v-if="notificationsUnread.length === 0"
                            >
                                No notifications to show.
                            </p>
                        </b-col>
                    </b-row>
                    <br />
                    <b-row
                        class="m-3 mb-1 pl-0 pr-0 text-center"
                        align-v="center"
                    >
                        <b-col><b>Read</b></b-col>
                    </b-row>
                    <b-row class="m-3 mb-1 pl-0 pr-0" align-v="center"
                        ><b-col class="m-0 pl-0 pr-0 text-center">
                            <b-list-group
                                v-if="notificationsRead.length > 0"
                                class="text-left m-0 p-0"
                            >
                                <b-list-group-item
                                    variant="default"
                                    style="box-shadow: -2px 2px 2px #adb5bd"
                                    v-for="notification in notificationsRead"
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
                                v-if="notificationsRead.length === 0"
                            >
                                No notifications.
                            </p>
                        </b-col>
                    </b-row>
                </b-container>
            </template>
        </b-sidebar>
        <b-navbar
            toggleable="sm"
            class="logo p-0 pt-1 pb-2"
            style="min-height: 44px; max-height: 46px; z-index: 1000"
            fixed="top"
            :type="profile.darkMode ? 'dark' : 'secondary'"
            :variant="profile.darkMode ? 'dark' : 'white'"
        >
            <b-collapse class="m-0 p-0" is-nav>
                <b-navbar-nav class="m-0 p-0 pl-3 mr-1">
                    <b-nav-item class="m-0 p-0" v-b-toggle.tasks>
                        <b-button
                            class="brand-img m-0 p-0"
                            v-bind:class="{ 'not-found': notFound }"
                            variant="outline-white"
                            @mouseenter="titleContent = 'sidebar'"
                            @mouseleave="titleContent = 'brand'"
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
                                Your Tasks ({{ tasksRunning.length }}
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
                        >
                        <b-nav-item
                            title="About"
                            to="/about"
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
                                ><i
                                    class="fas fa-question-circle fa-1x fa-fw"
                                ></i
                                >About</span
                            ></b-nav-item
                        >
                        <b-nav-item
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
                        class="p-0 mt-2 ml-0 mr-0"
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
                                class="ml-0 mr-0 mt-1 text-left"
                                size="md"
                            >
                                <span
                                    :title="
                                        'Notifications (' +
                                            notificationsUnread.length +
                                            ')'
                                    "
                                    v-if="notificationsUnread.length > 0"
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
                                    style="min-width: 27px; min-height: 27px; position: relative; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
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
                            title="Dashboard"
                            to="/dashboard/"
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
                            Dashboard
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
        <br />
        <br />
        <div v-if="alerts.length > 0">
            <b-alert
                class="m-0"
                show
                v-for="alert in alerts"
                v-bind:key="alert.guid"
                :variant="alert.variant"
                dismissible
                @dismissed="removeAlert(alert)"
                ><b>{{ alert.message }}</b>
                {{ prettifyShort(alert.time) }}</b-alert
            >
        </div>
        <b-toast
            auto-hide-delay="10000"
            v-if="$route.name !== 'task' && taskToasted !== null"
            id="toast"
            :variant="profile.darkMode ? 'dark text-light' : 'light text-dark'"
            solid
        >
            <template #toast-title
                ><b-link
                    class="text-dark"
                    :to="{
                        name: 'task',
                        params: {
                            name: taskToasted.name,
                            owner: taskToasted.owner
                        }
                    }"
                    >{{ `Task ${taskToasted.name}` }}</b-link
                ></template
            >
            <small>
                <b v-if="!taskToasted.is_complete">Running</b>
                <b class="ml-0 mr-0" v-else>{{ taskToasted.job_status }}</b>
                on
                <b>{{ taskToasted.agent }}</b>
                {{ prettifyShort(taskToasted.updated) }}
                <br />
                {{ taskToasted.task_logs[taskToasted.task_logs.length - 1] }}
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
            // user data
            djangoProfile: null,
            cyverseProfile: null,
            githubProfile: null,
            // websockets
            workflowSocket: null,
            taskSocket: null,
            notificationSocket: null,
            interactiveSocket: null,
            // breadcrumb & brand
            crumbs: [],
            titleContent: 'brand',
            // task sidebar & toasts
            taskPage: 0,
            taskToasted: null,
            taskSearchText: '',
            // flags
            togglingDarkMode: false,
            notFound: false
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('alerts', ['alerts']),
        ...mapGetters('tasks', [
            'tasks',
            'tasksLoading',
            'tasksRunning',
            'tasksCompleted'
        ]),
        ...mapGetters('notifications', [
            'notifications',
            'notificationsLoading',
            'notificationsRead',
            'notificationsUnread'
        ]),
        filteredRunningTasks() {
            return this.tasksRunning.filter(
                sub =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.taskSearchText)) ||
                    sub.tags.some(tag => tag.includes(this.taskSearchText))
            );
        },
        filteredCompletedTasks() {
            return this.tasksCompleted.filter(
                sub =>
                    (sub.workflow_name !== null &&
                        sub.workflow_name.includes(this.taskSearchText)) ||
                    sub.tags.some(tag => tag.includes(this.taskSearchText))
            );
        }
    },
    created: async function() {
        if (this.profile.djangoProfile === null) this.logOut();

        this.crumbs = this.$route.meta.crumb;

        await Promise.all([
            this.$store.dispatch('tasks/loadAll'),
            this.$store.dispatch('notifications/loadAll'),
            this.$store.dispatch('workflows/loadPublic'),
            this.$store.dispatch(
                'workflows/loadPersonal',
                this.profile.githubProfile.login
            ),
            this.$store.dispatch('agents/loadPublic'),
            this.$store.dispatch(
                'agents/loadPersonal',
                this.profile.djangoProfile.username
            ),
            this.$store
                .dispatch('datasets/loadPublic')
                .catch(error => this.logOutIfForbidden(error)),
            this.$store
                .dispatch('datasets/loadPersonal')
                .catch(error => this.logOutIfForbidden(error)),
            this.$store
                .dispatch('datasets/loadShared')
                .catch(error => this.logOutIfForbidden(error)),
            this.$store
                .dispatch('datasets/loadSharing')
                .catch(error => this.logOutIfForbidden(error))
        ]);

        // TODO move websockets to vuex
        let wsProtocol = location.protocol === 'https:' ? 'wss://' : 'ws://';

        this.workflowSocket = new WebSocket(
            `${wsProtocol}${window.location.host}/ws/workflows/${this.profile.githubProfile.login}/`
        );
        this.workflowSocket.onmessage = this.handleWorkflowEvent;

        this.taskSocket = new WebSocket(
            `${wsProtocol}${window.location.host}/ws/tasks/${this.profile.djangoProfile.username}/`
        );
        this.taskSocket.onmessage = this.handleTaskEvent;

        this.notificationSocket = new WebSocket(
            `${wsProtocol}${window.location.host}/ws/notifications/${this.profile.djangoProfile.username}/`
        );
        this.notificationSocket.onmessage = this.handleNotificationEvent;
    },
    watch: {
        $route() {
            this.crumbs = this.$route.meta.crumb;
        }
    },
    methods: {
        removeAlert(alert) {
            this.$store.dispatch('alerts/remove', alert);
        },
        async toggleDarkMode() {
            this.togglingDarkMode = true;
            await this.$store.dispatch('user/toggleDarkMode');
            this.togglingDarkMode = false;
        },
        markAllNotificationsRead() {},
        markNotificationRead(notification) {
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
        async handleWorkflowEvent(event) {
            let data = JSON.parse(event.data);
            let operation = data.operation;
            let workflow = data.workflow;
            if (operation === 'update')
                await this.$store.dispatch('workflows/addOrUpdate', workflow);
            else if (operation === 'remove')
                await this.$store.dispatch('workflows/remove', workflow);
        },
        async handleTaskEvent(event) {
            let data = JSON.parse(event.data);
            let task = data.task;
            this.taskToasted = task;
            this.$bvToast.show('toast');
            await this.$store.dispatch('tasks/update', task);
        },
        async handleNotificationEvent(event) {
            let data = JSON.parse(event.data);
            let notification = data.notification;
            await this.$store.dispatch('notifications/update', notification);
        },
        removeTask(task) {
            axios
                .get(`/apis/v1/tasks/${task.owner}/${task.name}/delete/`)
                .then(response => {
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
        showDeletePrompt(task) {
            this.$bvModal.show('remove ' + task.name);
        },
        now() {
            return moment().format('MMMM Do YYYY, h:mm:ss a');
        },
        logOutIfForbidden(error) {
          alert(error);
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
