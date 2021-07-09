<template>
    <div>
        <b-container
            fluid
            class="m-0 p-3"
            style="background-color: transparent;"
        >
            <div v-if="isRootPath">
                <b-row
                    ><b-col
                        ><h2
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            <b-img
                                class="mb-1"
                                style="max-width: 40px"
                                :src="
                                    profile.darkMode
                                        ? require('../../assets/miappe_icon.png')
                                        : require('../../assets/miappe_icon_black.png')
                                "
                            ></b-img>
                            {{ sharedContext ? 'Shared' : 'Your' }} MIAPPE
                            Projects
                        </h2></b-col
                    ><b-col md="auto" class="ml-0 mb-1" align-self="center"
                        ><b-button
                            id="create-project"
                            :disabled="projectsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="sm"
                            class="ml-0 mt-0 mr-0"
                            @click="showCreateProjectModal"
                            title="Create a new project"
                            v-b-tooltip:hover
                            ><i class="fas fa-plus"></i> Create</b-button
                        ><b-popover
                            :show.sync="profile.tutorials"
                            triggers="manual"
                            placement="left"
                            target="create-project"
                            title="Create a new project"
                            >Click here to create a new MIAPPE
                            investigation.</b-popover
                        ></b-col
                    >
                    <b-col md="auto" class="ml-0 mb-1" align-self="center"
                        ><b-button
                            id="switch-projects-context"
                            :disabled="projectsLoading"
                            :variant="
                                profile.darkMode ? 'outline-light' : 'white'
                            "
                            size="sm"
                            class="ml-0 mt-0 mr-0"
                            @click="toggleContext"
                            :title="
                                sharedContext
                                    ? 'View your projects'
                                    : 'View shared projects'
                            "
                            v-b-tooltip:hover
                            ><span v-if="sharedContext"
                                ><i class="fas fa-user"></i> Yours</span
                            ><span v-else
                                ><i class="fas fa-users"></i> Shared</span
                            ></b-button
                        ><b-popover
                            :show.sync="profile.tutorials"
                            triggers="manual"
                            placement="left"
                            target="switch-projects-context"
                            title="MIAPPE Context"
                            >Click here to toggle between your projects and
                            those other users have invited you to.</b-popover
                        ></b-col
                    >
                </b-row>
                <b-row
                    ><b-col v-if="!sharedContext">
                        <span v-if="personalProjects.length === 0"
                            >You haven't started any projects.</span
                        >
                        <projectblurb
                            v-for="project in personalProjects"
                            v-bind:key="project.unique_id"
                            :project="project"
                        ></projectblurb></b-col
                    ><b-col v-else>
                        <span v-if="othersProjects.length === 0"
                            >You have not been invited to any projects.</span
                        >
                        <b-card-group>
                            <b-card
                                v-for="project in othersProjects"
                                v-bind:key="project.unique_id"
                                :title="project.title"
                                :sub-title="project.unique_id"
                                no-body
                            >
                                <b-card-body>
                                    <h4>{{ project.title }}</h4>
                                    <h6 v-if="project.description !== null">
                                        {{ project.description }}
                                    </h6>
                                    <small>Owner: {{ project.owner }}</small>
                                    <br />
                                    <small
                                        v-if="project.submission_date !== null"
                                        >Submission:
                                        {{
                                            prettify(project.submission_date)
                                        }}</small
                                    >
                                    <br />
                                    <small
                                        v-if="
                                            project.public_release_date !== null
                                        "
                                        >Release:
                                        {{
                                            prettify(
                                                project.public_release_date
                                            )
                                        }}</small
                                    >
                                    <br />
                                    <br />
                                    <b-row>
                                        <b-col><h5>Studies</h5></b-col
                                        ><b-col md="auto"
                                            ><b-button
                                                id="add-study"
                                                :disabled="addingStudy"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Add a new study"
                                                @click="specifyStudy(project)"
                                                class="ml-0 mt-0 mr-0"
                                            >
                                                <b-spinner
                                                    small
                                                    v-if="addingStudy"
                                                    label="Adding..."
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'light'
                                                            : 'dark'
                                                    "
                                                    class="mr-1"
                                                ></b-spinner
                                                ><i
                                                    v-else
                                                    class="fas fa-plus mr-1"
                                                ></i
                                                >Add</b-button
                                            ><b-popover
                                                :show.sync="profile.tutorials"
                                                triggers="manual"
                                                placement="bottomleft"
                                                target="add-study"
                                                title="Add Study"
                                                >Click here to add a new study
                                                to this project.</b-popover
                                            ></b-col
                                        >
                                    </b-row>
                                    <span v-if="project.studies.length === 0"
                                        >This project has no studies.</span
                                    >
                                    <b-card-group>
                                        <b-card
                                            v-for="study in project.studies"
                                            v-bind:key="study.unique_id"
                                            no-body
                                            ><b-card-body>
                                                <b>{{ study.title }}</b
                                                ><br /><span>{{
                                                    study.description
                                                }}</span
                                                ><br />
                                                <br />
                                                <small
                                                    >Start:
                                                    {{
                                                        prettify(
                                                            study.start_date
                                                        )
                                                    }}</small
                                                >
                                                <br />
                                                <small
                                                    >End:
                                                    {{
                                                        prettify(study.end_date)
                                                    }}</small
                                                >
                                                <br />
                                                <small
                                                    >Contact Institution:
                                                    {{
                                                        study.contact_institution
                                                    }}</small
                                                >
                                                <br />
                                                <small
                                                    >Country:
                                                    {{ study.country }}</small
                                                >
                                                <br />
                                                <span
                                                    v-if="
                                                        study.site_name !== null
                                                    "
                                                >
                                                    <small
                                                        >Site:
                                                        {{
                                                            study.site_name
                                                        }}</small
                                                    >
                                                    <br />
                                                </span>
                                                <span
                                                    v-if="
                                                        study.experimental_design_type !==
                                                            null
                                                    "
                                                >
                                                    <small
                                                        >Experimental Design:
                                                        {{
                                                            study.experimental_design_type
                                                        }}</small
                                                    >
                                                    <small
                                                        v-if="
                                                            study.experimental_design_description !==
                                                                null
                                                        "
                                                        >{{
                                                            study.experimental_design_description
                                                        }}</small
                                                    >
                                                    <br />
                                                </span>
                                                <span
                                                    v-if="
                                                        study.observation_unit_level_hierarchy !==
                                                            null
                                                    "
                                                >
                                                    <small
                                                        >Observation Unit:
                                                        {{
                                                            study.observation_unit_level_hierarchy
                                                        }}</small
                                                    >
                                                    <small
                                                        v-if="
                                                            study.observation_unit_description !==
                                                                null
                                                        "
                                                        >{{
                                                            study.observation_unit_description
                                                        }}</small
                                                    >
                                                    <br />
                                                </span>
                                                <span
                                                    v-if="
                                                        study.growth_facility_type !==
                                                            null
                                                    "
                                                >
                                                    <small
                                                        >Growth Facility:
                                                        {{
                                                            study.growth_facility_type
                                                        }}</small
                                                    >
                                                    <small
                                                        v-if="
                                                            study.growth_facility_description !==
                                                                null
                                                        "
                                                        >{{
                                                            study.growth_facility_description
                                                        }}</small
                                                    >
                                                    <br />
                                                </span>
                                                <span
                                                    v-if="
                                                        study.cultural_practices !==
                                                            null
                                                    "
                                                >
                                                    <small
                                                        >Cultural Practices:
                                                        {{
                                                            study.cultural_practices
                                                        }}</small
                                                    >
                                                </span>
                                            </b-card-body></b-card
                                        ></b-card-group
                                    >
                                    <br />
                                    <br />
                                    <b-row>
                                        <b-col><h5>Team Members</h5></b-col>
                                    </b-row>
                                    <span v-if="team(project).length === 1"
                                        >You are the only team member in this
                                        project.</span
                                    >
                                    <b-card-group>
                                        <b-card
                                            v-for="member in team(
                                                project
                                            ).filter(
                                                u =>
                                                    u.id !==
                                                    profile.djangoProfile
                                                        .username
                                            )"
                                            v-bind:key="member.id"
                                            no-body
                                            ><b-card-body
                                                ><b-row
                                                    ><b-col align-self="middle"
                                                        ><b-img
                                                            v-if="
                                                                avatarUrl(
                                                                    member
                                                                ) !== ''
                                                            "
                                                            class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                                                            style="width: 2rem; height: 2rem; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                                                            rounded="circle"
                                                            :src="
                                                                avatarUrl(
                                                                    member
                                                                )
                                                            "
                                                        ></b-img>
                                                        <b>{{ member.name }}</b>
                                                        ({{ member.id }}),
                                                        <span>{{
                                                            member.affiliation
                                                        }}</span></b-col
                                                    >
                                                </b-row>
                                            </b-card-body></b-card
                                        ></b-card-group
                                    >
                                </b-card-body>
                            </b-card></b-card-group
                        ></b-col
                    ></b-row
                >
            </div>
        </b-container>
        <b-modal
            id="createProject"
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
            title="Create a new project"
            @ok="createProject"
            @close="resetProjectInfo"
            :ok-disabled="!projectInfoValid"
            ok-title="Create"
            hide-header
            hide-header-close
        >
            <b-row class="mb-2"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Create a new project
                    </h4></b-col
                ></b-row
            >
            <b-alert variant="danger" :show="projectTitleExists"
                >This title is already in use. Please pick another.</b-alert
            >
            <b-form-group>
                <template #description
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >A title for this project.</span
                    ></template
                >
                <b-form-input
                    :state="projectTitleValid"
                    v-model="projectTitle"
                    type="text"
                    placeholder="Enter a title"
                    required
                    @input="onProjectTitleChange"
                ></b-form-input>
            </b-form-group>
            <b-form-group>
                <template #description
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >A brief description of this project.</span
                    ></template
                >
                <b-form-textarea
                    :state="projectDescriptionValid"
                    v-model="projectDescription"
                    placeholder="Enter a description"
                    required
                ></b-form-textarea>
            </b-form-group>
        </b-modal>
        <b-modal
            id="addTeamMember"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            size="lg"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            hide-header
            hide-header-close
            hide-footer
        >
            <b-row class="mb-2"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Select a user
                    </h4></b-col
                >
                <b-col md="auto"
                    ><b-button
                        :disabled="usersLoading"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        size="sm"
                        v-b-tooltip.hover
                        title="Rescan users"
                        @click="refreshUsers"
                        class="text-right"
                    >
                        <b-spinner
                            small
                            v-if="usersLoading"
                            label="Rescanning..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><i v-else class="fas fa-redo mr-1"></i>Rescan
                        Users</b-button
                    ></b-col
                >
            </b-row>
            <div v-if="otherUsers.length !== 0">
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    Select a user to invite to this project.
                </p>
                <b-row class="mb-2"
                    ><b-col
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        ><small
                            >{{ otherUsers.length }} user(s) found</small
                        ></b-col
                    ></b-row
                >
                <b-row v-for="user in otherUsers" v-bind:key="user.username">
                    <b-col
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    >
                        <b-img
                            v-if="user.github_profile"
                            class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                            style="width: 2rem; height: 2rem; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                            rounded="circle"
                            :src="
                                user.github_profile
                                    ? user.github_profile.avatar_url
                                    : ''
                            "
                        ></b-img>
                        <i v-else class="far fa-user fa-fw mr-1"></i>
                        <b>{{ user.first_name }} {{ user.last_name }}</b> ({{
                            user.username
                        }})
                    </b-col>
                    <b-col md="auto" align-self="center"
                        ><b-button
                            :disabled="addingTeamMember"
                            variant="warning"
                            @click="addTeamMember(selectedInvestigation, user)"
                            >Select</b-button
                        ></b-col
                    >
                </b-row>
            </div>
            <div class="text-center" v-else>
                <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                    <i class="fas fa-exclamation-circle fa-fw fa-2x"></i
                    ><br />No other users found.
                </p>
            </div>
        </b-modal>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';
import projectblurb from '@/components/projects/project-blurb';
import axios from 'axios';
import { guid } from '@/utils';
import * as Sentry from '@sentry/browser';

export default {
    name: 'projects.vue',
    components: {
        projectblurb
    },
    data: function() {
        return {
            projectTitleLoading: false,
            projectTitleExists: false,
            projectTitle: '',
            projectDescription: '',
            creatingProject: false,
            togglingContext: false,
            sharedContext: false,
            selectedInvestigation: null,
            addingTeamMember: false,
            removingTeamMember: false,
            addingStudy: false,
            removingStudy: false
        };
    },
    methods: {
        showCreateProjectModal() {
            this.$bvModal.show('createProject');
        },
        hideCreateProjectModal() {
            this.$bvModal.hide('createProject');
        },
        resetProjectInfo() {
            this.projectTitle = '';
            this.projectDescription = '';
        },
        onProjectTitleChange() {
            this.projectTitleLoading = true;
            return axios
                .get(
                    `/apis/v1/miappe/${this.profile.djangoProfile.username}/${this.projectTitle}/exists/`
                )
                .then(response => {
                    this.projectTitleExists = response.data.exists;
                    this.projectTitleLoading = false;
                    this.$emit('input', this.name);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.projectTitleLoading = false;
                    if (error.response.status === 500) throw error;
                });
        },
        async createProject() {
            this.creatingProject = true;
            let data = {
                title: this.projectTitle,
                description: this.projectDescription
            };

            await axios({
                method: 'post',
                url: `/apis/v1/miappe/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'miappe/addOrUpdate',
                                response.data
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Created project ${response.data.title}`,
                                guid: guid().toString(),
                                time: moment().format()
                            })
                        ]);
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to create project ${response.data.title}`,
                            guid: guid().toString(),
                            time: moment().format()
                        });
                    }
                    this.resetProjectInfo();
                    this.hideCreateProjectModal();
                    this.creatingProject = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to create project ${this.projectTitle}`,
                        guid: guid().toString(),
                        time: moment().format()
                    });
                    this.hideCreateProjectModal();
                    this.creatingProject = false;
                    throw error;
                });
            this.creatingProject = false;
        },
        toggleContext() {
            this.togglingContext = true;
            this.sharedContext = !this.sharedContext;
            this.togglingContext = false;
        },
        avatarUrl(user) {
            let found = this.otherUsers.find(u => u.username === user.id);
            if (found === undefined) return undefined;
            return found.github_profile.avatar_url;
        },
        async refreshUsers() {
            await this.$store.dispatch('users/loadAll');
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        }
    },
    watch: {
        personalInvestigations() {
            //
        }
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        ...mapGetters('projects', [
            'personalProjects',
            'othersProjects',
            'projectsLoading'
        ]),
        isRootPath() {
            return this.$route.name === 'projects';
        },
        projectSelected() {
            return this.selectedInvestigation !== null;
        },
        projectUniqueId() {
            return `plantit-projects-${this.profile.djangoProfile.username}-${this.projectTitle}`;
        },
        projectTitleValid() {
            return this.projectTitle !== '';
        },
        projectDescriptionValid() {
            return this.projectDescription !== '';
        },
        projectInfoValid() {
            return this.projectTitleValid && this.projectDescriptionValid;
        },
        otherUsers() {
            return this.allUsers.filter(
                u =>
                    u.username !== this.profile.djangoProfile.username &&
                    ((this.projectSelected &&
                        !this.selectedInvestigation.team.some(
                            ua => ua.id === u.username
                        )) ||
                        !this.projectSelected)
            );
        }
    }
};
</script>

<style scoped></style>
