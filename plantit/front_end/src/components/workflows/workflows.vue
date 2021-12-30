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
                        class="ml-0 mt-0 mr-0"
                        :title="context"
                        ><template #button-content>
                            <span v-if="context === profile.githubProfile.login"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else-if="context === ''"
                                ><i class="fas fa-users"></i> Public</span
                            ><span
                                v-else-if="
                                    profile.collaborators
                                        .map((c) => c.github_username)
                                        .includes(context)
                                "
                            >
                                <b-img
                                    v-if="
                                        profile.collaborators.filter(
                                            (c) => c.github_username
                                        )[0].github_profile.avatar_url
                                    "
                                    class="avatar m-0 mb-1 p-0 github-hover logo"
                                    style="
                                        width: 20px;
                                        height: 20px;
                                        position: relative;
                                        border: 1px solid #e2e3b0;
                                    "
                                    rounded="circle"
                                    :src="
                                        profile.collaborators.filter(
                                            (c) => c.github_username
                                        )[0].github_profile.avatar_url
                                    "
                                ></b-img>
                                {{ context }}</span
                            ><span v-else
                                ><i class="fas fa-building"></i>
                                {{ context }}</span
                            >
                        </template>
                        <b-dropdown-item
                            @click="switchContext(profile.githubProfile.login)"
                            ><i class="fas fa-user fa-fw"></i>
                            Yours</b-dropdown-item
                        >
                        <b-dropdown-item @click="switchContext('')"
                            ><i class="fas fa-users fa-fw"></i>
                            Public</b-dropdown-item
                        >
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-header
                            >Your Organizations</b-dropdown-header
                        >
                        <b-dropdown-item
                            @click="switchContext(org.login)"
                            v-for="org in profile.githubOrganizations"
                            v-bind:key="org.login"
                            ><i class="fas fa-building fa-fw"></i>
                            {{ org.login }}</b-dropdown-item
                        ><b-dropdown-text
                            v-if="profile.githubOrganizations.length === 0"
                            ><i>None to show</i></b-dropdown-text
                        >
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-header
                            >Your Collaborators</b-dropdown-header
                        >
                        <b-dropdown-item
                            @click="switchContext(col.github_username)"
                            v-for="col in profile.collaborators"
                            v-bind:key="col.github_username"
                            ><b-img
                                id="avatar"
                                v-if="col.github_profile.avatar_url"
                                class="avatar m-0 mb-1 p-0 github-hover logo"
                                style="
                                    width: 20px;
                                    height: 20px;
                                    position: relative;
                                    left: -3px;
                                    top: 0.5px;
                                    border: 1px solid #e2e3b0;
                                "
                                rounded="circle"
                                :src="col.github_profile.avatar_url"
                            ></b-img>
                            {{ col.github_username }}</b-dropdown-item
                        >
                        <b-dropdown-text
                            v-if="profile.collaborators.length === 0"
                            ><i>None to show</i></b-dropdown-text
                        >
                    </b-dropdown>
                    <b-popover
                        v-if="profile.hints"
                        triggers="hover"
                        placement="topleft"
                        target="switch-workflow-context"
                        title="Workflow Context"
                        >Click here to toggle between public, organization, and
                        your own personal workflow context.</b-popover
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
                    style="min-width: 30rem"
                    class="overflow-hidden mb-4"
                >
                    <blurb :linkable="true" :workflow="workflow"></blurb>
                </b-card>
            </b-card-group>
            <b-row v-else
                ><b-col :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    ><span v-if="context === ''"
                        >No public workflows have been published yet.</span
                    ><span v-else-if="context === profile.githubProfile.login"
                        >You haven't created any workflow bindings yet. Add a
                        <code>plantit.yaml</code> file to any public repository
                        to bind a workflow.</span
                    ><span
                        v-else-if="
                            profile.collaborators
                                .map((c) => c.github_username)
                                .includes(context)
                        "
                        >This user has no workflow bindings yet.</span
                    ><span v-else
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
            context: '',
            contextToggling: false,
            login: false,
        };
    },
    watch: {
        // TODO get rid of this, it's hacky
        // eslint-disable-next-line no-unused-vars
        personalWorkflows: function () {
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
        switchContext(ctx) {
            this.contextToggling = true;
            this.context = ctx;
            this.contextToggling = false;
        },
        sortWorkflows(a, b) {
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
            else if (this.context === this.profile.githubProfile.login)
                await this.$store.dispatch(
                    'workflows/refreshPersonal',
                    this.profile.githubProfile.login
                );
            else
                await this.$store.dispatch(
                    'workflows/refreshOrg',
                    this.context
                );
        },
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('workflows', [
            'orgWorkflows',
            'orgWorkflowsLoading',
            'personalWorkflows',
            'personalWorkflowsLoading',
            'collaboratorWorkflows',
            'collaboratorWorkflowsLoading',
            'publicWorkflows',
            'publicWorkflowsLoading',
        ]),
        isRootPath() {
            return this.$route.name === 'workflows';
        },
        getWorkflows() {
            return [
                ...(this.context === ''
                    ? this.publicWorkflows
                    : this.context === this.profile.githubProfile.login
                    ? this.personalWorkflows
                    : this.profile.collaborators
                          .map((c) => c.github_username)
                          .includes(this.context)
                    ? this.collaboratorWorkflows[
                          this.profile.collaborators.filter(
                              (c) => c.github_username
                          )[0].github_username
                      ]
                    : this.orgWorkflows[this.context]),
            ].sort(this.sortWorkflows);
        },
        workflowsLoading() {
            return this.context === ''
                ? this.publicWorkflowsLoading
                : this.context === this.profile.githubProfile.login
                ? this.personalWorkflowsLoading
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
    .jv-toggle
      &:before
        padding: 0px 2px
        border-radius: 2px
      &:hover
        &:before
          background: #eee
</style>
