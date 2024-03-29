<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent">
        <div v-if="isRootPath">
            <b-row
                ><b-col md="auto"
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        <i class="fas fa-stream fa-fw"></i>
                        Workflows
                    </h4></b-col
                >
                <b-col md="auto" align-self="center" class="mb-1"
                    ><small
                        >powered by
                        <i class="fab fa-github fa-fw fa-1x"></i></small
                    ><b-img
                        class="mt-1"
                        rounded
                        style="max-height: 1.2rem"
                        right
                        :src="
                            profile.darkMode
                                ? require('../../assets/logos/github_white.png')
                                : require('../../assets/logos/github_black.png')
                        "
                    ></b-img
                ></b-col>
                <b-col></b-col>
                <b-col align-self="center" class="mb-1" md="auto">
                    <b-dropdown
                        dropleft
                        id="switch-workflow-context"
                        :disabled="workflowsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        class="ml-0 mt-0 mr-0 darklinks"
                        :title="context"
                        ><template #button-content>
                            <span v-if="context === 'Featured'"
                                ><i class="fas fa-certificate fa-fw"></i>
                                Featured</span
                            >
                            <span v-else-if="context === 'Examples'">
                                <i class="fas fa-thumbtack fa-fw"></i>
                                {{ context }}
                            </span>
                            <span v-else-if="context === 'Public'"
                                ><i class="fas fa-users fa-fw"></i> Public</span
                            >
                            <span v-else-if="context === 'Yours'"
                                ><i class="fas fa-user fa-fw"></i> Yours</span
                            >
                            <span
                                v-else-if="
                                    getProjects
                                        .map((p) => p.title)
                                        .includes(context)
                                "
                                ><b-img
                                    class="mb-1"
                                    style="max-width: 15px"
                                    :src="
                                        profile.darkMode
                                            ? require('../../assets/miappe_icon.png')
                                            : require('../../assets/miappe_icon_black.png')
                                    "
                                ></b-img>
                                {{ context }}</span
                            >
                            <!-- otherwise it's an organization context -->
                            <span v-else
                                ><i class="fas fa-building fa-fw"></i>
                                {{ context }}</span
                            >
                        </template>
                        <b-dropdown-header>Default</b-dropdown-header>
                        <b-dropdown-item
                            @click="switchContext('Featured')"
                            class="darklinks"
                            ><i class="fas fa-certificate fa-fw"></i>
                            Featured</b-dropdown-item
                        >
                        <b-dropdown-item
                            @click="switchContext('Examples')"
                            class="darklinks"
                            ><i class="fas fa-thumbtack fa-fw"></i>
                            Examples</b-dropdown-item
                        >
                        <b-dropdown-item
                            @click="switchContext('Public')"
                            class="darklinks"
                            ><i class="fas fa-users fa-fw"></i>
                            Public</b-dropdown-item
                        >
                        <b-dropdown-item
                            @click="switchContext('Yours')"
                            class="darklinks"
                            ><i class="fas fa-user fa-fw"></i>
                            Yours</b-dropdown-item
                        >
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-header>Organizations</b-dropdown-header>
                        <b-dropdown-item
                            @click="switchContext(org.login)"
                            v-for="org in profile.organizations"
                            v-bind:key="org.login"
                            class="darklinks"
                            ><i class="fas fa-building fa-fw"></i>
                            {{ org.login }}</b-dropdown-item
                        ><b-dropdown-text
                            v-if="profile.organizations.length === 0"
                            ><i>None to show</i></b-dropdown-text
                        >
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-header>Projects</b-dropdown-header>
                        <b-dropdown-item
                            v-for="project in getProjects"
                            @click="switchContext(project.title)"
                            v-bind:key="project.guid"
                            class="darklinks"
                            ><b-img
                                class="mb-1"
                                style="max-width: 15px"
                                :src="
                                    profile.darkMode
                                        ? require('../../assets/miappe_icon.png')
                                        : require('../../assets/miappe_icon_black.png')
                                "
                            ></b-img>
                            {{ project.title }}</b-dropdown-item
                        >
                        <b-dropdown-text v-if="getProjects.length === 0"
                            ><i>None to show</i></b-dropdown-text
                        >
                    </b-dropdown>
                    <b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="topleft"
                        target="switch-workflow-context"
                        title="Workflow Context"
                        >Click here to toggle between example workflows, public
                        workflows, organization-owned workflows, and your own
                        personal workflow context.</b-popover
                    >
                </b-col>
                <b-col md="auto" class="ml-0 mb-1" align-self="center"
                    ><b-button
                        id="refresh-workflows"
                        :disabled="workflowsLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Refresh workflows"
                        @click="refreshWorkflows"
                        class="ml-0 mt-0 mr-0"
                    >
                        <b-spinner
                            small
                            v-if="workflowsLoading"
                            label="Refreshing..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i
                        >Refresh</b-button
                    ><b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="bottomright"
                        target="refresh-workflows"
                        title="Refresh Workflows"
                        >Click here to re-synchronize your workflows with GitHub
                        (helpful if you have introduced changes to a
                        <code>plantit.yaml</code> file).</b-popover
                    ></b-col
                >
            </b-row>
            <b-row v-if="workflowsLoading" class="mt-2">
                <b-col>
                    <b-spinner
                        small
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading workflows...</span
                    >
                </b-col>
            </b-row>
            <b-card-group deck columns v-else-if="getWorkflows.length !== 0">
                <b-card
                    v-for="workflow in getWorkflows"
                    :key="`${workflow.repo.owner.login}/${workflow.repo.name}/${workflow.branch.name}`"
                    :bg-variant="profile.darkMode ? 'dark' : 'white'"
                    :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                    border-variant="default"
                    :header-border-variant="
                        profile.darkMode ? 'secondary' : 'default'
                    "
                    :text-variant="profile.darkMode ? 'white' : 'dark'"
                    style="min-width: 30rem;max-width:47%"
                    class="overflow-hidden mb-4"
                >
                    <blurb :linkable="true" :workflow="workflow"></blurb>
                </b-card>
            </b-card-group>
            <b-row v-else
                ><b-col :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    <span v-if="context === 'Featured'"
                        >No featured workflows to show.</span
                    >
                    <span v-else-if="context === 'Public'"
                        >No public workflows have been published yet.</span
                    ><span v-else-if="context === 'Examples'"
                        >There are no example workflows to show.</span
                    ><span v-else-if="context === 'Yours'">
                        <div v-if="!profile.loggedIntoGitHub">
                            <b-row align-v="center"
                                ><b-col class="text-center" align-self="center">
                                    <br />
                                    <br />
                                    <i
                                        class="fas fa-exclamation-circle fa-fw fa-3x text-warning"
                                    ></i
                                    ><br />
                                    We need to link your
                                    <i class="fab fa-github fa-fw fa-1x"></i
                                    ><b-img
                                        class="m-0"
                                        rounded
                                        style="max-height: 1.2rem"
                                        :src="
                                            profile.darkMode
                                                ? require('../../assets/logos/github_white.png')
                                                : require('../../assets/logos/github_black.png')
                                        "
                                    ></b-img>
                                    account before you can bind your own
                                    workflows.<br />Click the button below to
                                    log in.<br /><br /><b-button
                                        class="mt-1 text-left text-dark"
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
                        <span v-else
                            >You haven't created any workflow bindings yet. Add
                            a <code>plantit.yaml</code> file to any public
                            repository to bind a workflow.</span
                        ></span
                    ><span
                        v-else-if="
                            getProjects.map((c) => c.title).includes(context)
                        "
                        >This project has no associated workflows yet.</span
                    >
                    <span v-else
                        >This organization has no workflow bindings yet.</span
                    ></b-col
                ></b-row
            >
        </div>
        <router-view
            v-else
            :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
        ></router-view>
    </b-container>
</template>

<script>
import blurb from '@/components/workflows/workflow-blurb.vue';
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'workflows',
    components: {
        blurb,
    },
    data: function () {
        return {
            name: '',
            context: 'Featured',
            login: false,
        };
    },
    watch: {
        // eslint-disable-next-line no-unused-vars
        userWorkflows: function () {
            // noop
        },
        publicWorkflows: function () {
            // noop
        },
    },
    methods: {
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        switchContext(context) {
            this.context = context;
        },
        sortWorkflows(a, b) {
            // sort by name alphabetically
            if (a.config.name === b.config.name) {
                if (a.branch.name < b.branch.name) return -1;
                if (a.branch.name > b.branch.name) return 1;
                return 0;
            } else {
                if (a.config.name < b.config.name) return -1;
                if (a.config.name > b.config.name) return 1;
                return 0;
            }
        },
        async refreshWorkflows() {
            if (this.context === '')
                await this.$store.dispatch('workflows/refreshPublic');
            else if (this.context === 'Yours')
                await this.$store.dispatch('workflows/refreshUser');
            else if (
                this.getProjects.map((p) => p.title).includes(this.context)
            )
                await this.$store.dispatch('workflows/refreshProject');
            else if (this.context === 'Examples')
                await this.$store.dispatch('workflows/refreshPublic');
            else await this.$store.dispatch('workflows/refreshOrg');
        },
        filterExamples(workflows) {
            return workflows.filter((wf) => wf.example);
        },
        excludeExamples(workflows) {
            return workflows.filter((wf) => !wf.example);
        },
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('projects', [
            'projectsLoading',
            'othersProjects',
            'userProjects',
        ]),
        ...mapGetters('workflows', [
            'orgWorkflows',
            'orgWorkflowsLoading',
            'projectWorkflows',
            'projectWorkflowsLoading',
            'userWorkflows',
            'userWorkflowsLoading',
            'publicWorkflows',
            'publicWorkflowsLoading',
        ]),
        isRootPath() {
            return this.$route.name === 'workflows';
        },
        getProjects() {
            return this.userProjects.concat(this.othersProjects);
        },
        getWorkflows() {
            if (this.context === 'Public')
                return [...this.excludeExamples(this.publicWorkflows)].sort(
                    this.sortWorkflows
                );
            else if (this.context === 'Yours')
                return [...this.userWorkflows].sort(this.sortWorkflows);
            else if (
                this.getProjects.map((p) => p.title).includes(this.context)
            )
                return [
                    ...this.projectWorkflows[
                        this.getProjects.filter(
                            (p) => p.title === this.context
                        )[0].guid
                    ],
                ].sort(this.sortWorkflows);
            else if (this.context === 'Examples')
                return [...this.filterExamples(this.publicWorkflows)].sort(
                    this.sortWorkflows
                );
            else if (this.context === 'Featured') {
                return [...this.excludeExamples(this.publicWorkflows)].filter(
                    (wf) => wf.featured
                );
            } else
                return [...this.orgWorkflows[this.context]].sort(
                    this.sortWorkflows
                );
        },
        workflowsLoading() {
            return this.context === ''
                ? this.publicWorkflowsLoading
                : this.context === 'Yours'
                ? this.userWorkflowsLoading
                : this.orgWorkflowsLoading;
        },
    },
};
</script>
<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.darkjson
    background: #fff
    white-space: nowrap
    color: #525252
    font-size: 14px
    font-family: Consolas, Menlo, Courier, monospace

.jv-ellipsis
    color: #999
    background-color: #eee
    display: inline-block
    line-height: 0.9
    font-size: 0.9em
    padding: 0px 4px 2px 4px
    border-radius: 3px
    vertical-align: 2px
    cursor: pointer
    user-select: none

.jv-button
    color: #49b3ff
.jv-key
    color: #111111
.jv-item
    &.jv-array
        color: #111111
    &.jv-boolean
        color: #fc1e70
    &.jv-function
        color: #067bca
    &.jv-number
        color: #fc1e70
    &.jv-number-float
        color: #fc1e70
    &.jv-number-integer
        color: #fc1e70
    &.jv-object
        color: #111111
    &.jv-undefined
        color: #e08331
    &.jv-string
        color: #42b983
        word-break: break-word
        white-space: normal
.jv-code
    &:before
        padding: 0px 2px
        border-radius: 2px
    &:hover
        &:before
            background: #eee
</style>
