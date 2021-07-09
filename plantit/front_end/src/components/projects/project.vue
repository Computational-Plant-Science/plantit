<template>
    <div>
        <b-container class="p-2 vl" fluid>
            <b-row v-if="projectsLoading"
                ><b-col
                    ><b-spinner
                        variant="secondary"
                        type="grow"
                    ></b-spinner></b-col
            ></b-row>
            <b-card
                v-else
                :title="getProject.title"
                :sub-title="getProject.unique_id"
                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :text-variant="profile.darkMode ? 'white' : 'dark'"
                :body-text-variant="profile.darkMode ? 'white' : 'dark'"
                no-body
            >
                <b-card-body>
                    <b-row
                        ><b-col>
                            <h4>{{ getProject.title }}</h4> </b-col
                        ><b-col
                            v-if="ownsProject"
                            class="m-0"
                            align-self="end"
                            md="auto"
                            ><b-button
                                @click="showDeleteProjectModal"
                                v-b-tooltip.hover
                                :title="'Remove ' + getProject.title"
                                size="sm"
                                variant="outline-danger"
                                ><i class="fas fa-times-circle fa-fw fa-1x"></i>
                                Remove</b-button
                            ></b-col
                        >
                    </b-row>
                    <h6 v-if="getProject.description !== null">
                        {{ getProject.description }}
                    </h6>
                    <span v-if="getProject.submission_date !== null">
                        <small
                            >Submission:
                            {{ prettify(getProject.submission_date) }}</small
                        >
                        <br />
                    </span>
                    <span v-if="getProject.public_release_date !== null">
                        <small
                            >Release:
                            {{
                                prettify(getProject.public_release_date)
                            }}</small
                        >
                        <br />
                    </span>
                    <br />
                    <b-row>
                        <b-col><h5>Studies</h5></b-col
                        ><b-col md="auto"
                            ><b-button
                                id="add-study"
                                :disabled="addingStudy"
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                size="sm"
                                v-b-tooltip.hover
                                title="Create a new study"
                                @click="showAddStudyModal"
                                class="ml-0 mt-0 mr-0"
                            >
                                <b-spinner
                                    small
                                    v-if="addingStudy"
                                    label="Adding..."
                                    :variant="
                                        profile.darkMode ? 'light' : 'dark'
                                    "
                                    class="mr-1"
                                ></b-spinner
                                ><i v-else class="fas fa-plus mr-1"></i
                                >Add</b-button
                            ><b-popover
                                :show.sync="profile.tutorials"
                                triggers="manual"
                                placement="bottomleft"
                                target="add-study"
                                title="Create Study"
                                >Click here to add a new study to this
                                project.</b-popover
                            ></b-col
                        >
                    </b-row>
                    <span v-if="getProject.studies.length === 0"
                        >This project has no studies.</span
                    >
                    <b-card-group>
                        <b-card
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-text-variant="
                                profile.darkMode ? 'white' : 'dark'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
                            :body-text-variant="
                                profile.darkMode ? 'white' : 'dark'
                            "
                            v-for="study in getProject.studies"
                            v-bind:key="study.title"
                            no-body
                            ><b-card-body>
                                <b-row
                                    ><b-col>
                                        <b>{{ study.title }}</b></b-col
                                    ><b-col
                                        class="ml-0"
                                        md="auto"
                                        align-self="middle"
                                        ><b-button
                                            class="ml-0"
                                            variant="outline-danger"
                                            size="sm"
                                            v-b-tooltip.hover
                                            :title="
                                                'Remove ' +
                                                    study.title +
                                                    ' from this project'
                                            "
                                            @click="showRemoveStudyModal(study)"
                                        >
                                            <i
                                                class="fas fa-times-circle fa-fw"
                                            ></i>
                                            Remove
                                        </b-button></b-col
                                    ></b-row
                                >
                                <span
                                    v-if="
                                        study.description !== null &&
                                            study.description !== ''
                                    "
                                    >{{ study.description }}<br />
                                </span>
                                <span v-else><i>No description</i><br /> </span>
                                <span v-if="study.start_date !== null">
                                    <small
                                        >Start:
                                        {{ prettify(study.start_date) }}</small
                                    >
                                    <br />
                                </span>
                                <span v-if="study.end_date !== null">
                                    <small
                                        >End:
                                        {{ prettify(study.end_date) }}</small
                                    >
                                    <br />
                                </span>
                                <span v-if="study.contact_institution !== null">
                                    <small
                                        >Contact Institution:
                                        {{ study.contact_institution }}</small
                                    >
                                    <br />
                                </span>
                                <span v-if="study.country !== null">
                                    <small>Country: {{ study.country }}</small>
                                    <br />
                                </span>
                                <span v-if="study.site_name !== null">
                                    <small>Site: {{ study.site_name }}</small>
                                    <br />
                                </span>
                                <span
                                    v-if="
                                        study.experimental_design_type !== null
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
                                    v-if="study.growth_facility_type !== null"
                                >
                                    <small
                                        >Growth Facility:
                                        {{ study.growth_facility_type }}</small
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
                                <span v-if="study.cultural_practices !== null">
                                    <small
                                        >Cultural Practices:
                                        {{ study.cultural_practices }}</small
                                    >
                                </span>
                            </b-card-body></b-card
                        ></b-card-group
                    >
                    <br />
                    <b-row>
                        <b-col><h5>Team Members</h5></b-col
                        ><b-col md="auto"
                            ><b-button
                                id="add-member"
                                :disabled="addingTeamMember"
                                :variant="
                                    profile.darkMode ? 'outline-light' : 'white'
                                "
                                size="sm"
                                v-b-tooltip.hover
                                title="Add a team member"
                                @click="specifyTeamMember(getProject)"
                                class="ml-0 mt-0 mr-0"
                            >
                                <b-spinner
                                    small
                                    v-if="addingTeamMember"
                                    label="Adding..."
                                    :variant="
                                        profile.darkMode ? 'light' : 'dark'
                                    "
                                    class="mr-1"
                                ></b-spinner
                                ><i v-else class="fas fa-plus mr-1"></i
                                >Add</b-button
                            ><b-popover
                                :show.sync="profile.tutorials"
                                triggers="manual"
                                placement="bottomleft"
                                target="add-member"
                                title="Add Team Member"
                                >Click here to add a team member to this
                                project.</b-popover
                            ></b-col
                        >
                    </b-row>
                    <span v-if="getProject.team.length === 0"
                        >You are the only researcher in this project.</span
                    >
                    <b-row
                        v-for="member in getProject.team"
                        v-bind:key="member.id"
                        ><b-col align-self="middle"
                            ><b-img
                                v-if="avatarUrl(member) !== ''"
                                class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                                style="width: 2rem; height: 2rem; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                                rounded="circle"
                                :src="avatarUrl(member)"
                            ></b-img>
                            <b>{{ member.name }}</b>
                            ({{ member.id }}),
                            <span>{{ member.affiliation }}</span></b-col
                        ><b-col class="ml-0" md="auto" align-self="middle"
                            ><b-button
                                class="ml-0"
                                variant="outline-danger"
                                size="sm"
                                v-b-tooltip.hover
                                :title="
                                    'Remove ' + member.id + ' from this project'
                                "
                                @click="showRemoveTeamMemberModal(member)"
                            >
                                <i class="fas fa-times-circle fa-fw"></i>
                                Remove
                            </b-button></b-col
                        >
                    </b-row>
                </b-card-body>
            </b-card>
        </b-container>
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
                            @click="addTeamMember(user)"
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
        <b-modal
            id="addStudy"
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
            title="Create a new study"
            @ok="addStudy"
            @close="resetStudyInfo"
            :ok-disabled="!studyInfoValid"
            ok-title="Create"
            hide-header
            hide-header-close
        >
            <b-row class="mb-2"
                ><b-col
                    ><h4 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Create a new study
                    </h4></b-col
                ></b-row
            >
            <b-alert variant="danger" :show="studyTitleExists"
                >This title is already in use. Please pick another.</b-alert
            >
            <b-form-group>
                <template #description
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >A title for this study.</span
                    ></template
                >
                <b-form-input
                    :state="studyTitleValid"
                    v-model="studyTitle"
                    type="text"
                    placeholder="Enter a title"
                    required
                ></b-form-input>
            </b-form-group>
            <b-form-group>
                <template #description
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >A brief description of this study.</span
                    ></template
                >
                <b-form-textarea
                    :state="studyDescriptionValid"
                    v-model="studyDescription"
                    placeholder="Enter a description"
                    required
                ></b-form-textarea>
            </b-form-group>
            <!--<b-form-group>
                <template #description
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >This study's start date.</span
                    ></template
                >
                <b-form-datepicker
                    :state="studyStartDateValid"
                    v-model="studyStartDate"
                    placeholder="Enter a start date"
                ></b-form-datepicker>
            </b-form-group>
            <b-form-group>
                <template #description
                    ><span
                        :class="profile.darkMode ? 'text-light' : 'text-dark'"
                        >This study's end date.</span
                    ></template
                >
                <b-form-datepicker
                    :state="studyEndDateValid"
                    v-model="studyEndDate"
                    placeholder="Enter an end date"
                ></b-form-datepicker>
            </b-form-group>-->
        </b-modal>
        <b-modal
            id="removeTeamMember"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="
                `Remove ${
                    this.teamMemberToRemove !== null
                        ? this.teamMemberToRemove.id
                        : 'team member'
                }?`
            "
            @ok="removeTeamMember"
            ok-variant="danger"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                This person will no longer have access to this project.
            </p>
        </b-modal>
        <b-modal
            id="removeStudy"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="
                `Remove ${
                    this.studyToRemove !== null
                        ? this.studyToRemove.title
                        : 'study'
                }?`
            "
            @ok="removeStudy"
            ok-variant="danger"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                You {{ ownsProject ? '' : 'and your teammates' }} will no longer
                be able to access this study and its metadata.
            </p>
        </b-modal>
        <b-modal
            id="delete"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            centered
            close
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :title="`Delete ${this.getProject.title}?`"
            @ok="deleteProject"
            ok-variant="danger"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                You {{ ownsProject ? '' : 'and your teammates' }} will no longer
                be able to access this project and its metadata.
            </p>
        </b-modal>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import { guid } from '@/utils';
import * as Sentry from '@sentry/browser';
import moment from 'moment';
import router from '@/router';

export default {
    name: 'project',
    data: function() {
        return {
            addingTeamMember: false,
            removingTeamMember: false,
            teamMemberToRemove: null,
            addingStudy: false,
            removingStudy: false,
            studyTitle: '',
            studyDescription: '',
            studyToRemove: null,
            deleting: false
        };
    },
    methods: {
        resetStudyInfo() {
            this.studyTitle = '';
            this.studyDescription = '';
        },
        showDeleteProjectModal() {
            this.$bvModal.show('delete');
        },
        hideDeleteProjectModal() {
            this.$bvModal.hide('delete');
        },
        async deleteProject() {
            this.deleting = true;
            await axios({
                method: 'delete',
                url: `/apis/v1/miappe/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}/`,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(response => {
                    if (response.status === 200) {
                        this.$store.dispatch(
                            'projects/setPersonal',
                            response.data.projects
                        );
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Deleted project ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}`,
                            guid: guid().toString()
                        });
                        router.push({
                            name: 'projects'
                        });
                    } else {
                        this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to delete project ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.deleting = false;
                    this.hideDeleteProjectModal();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to delete project ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}`,
                        guid: guid().toString()
                    });
                    this.deleting = false;
                    throw error;
                });
        },
        avatarUrl(user) {
            let found = this.otherUsers.find(u => u.username === user.id);
            if (found === undefined) return undefined;
            return found.github_profile.avatar_url;
        },
        specifyTeamMember(project) {
            this.selectedInvestigation = project;
            this.$bvModal.show('addTeamMember');
        },
        showRemoveTeamMemberModal(member) {
            this.teamMemberToRemove = member;
            this.$bvModal.show('removeTeamMember');
        },
        hideRemoveTeamMemberModal() {
            this.$bvModal.hide('removeTeamMember');
        },
        async addTeamMember(user) {
            this.addingTeamMember = true;
            let data = { username: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.getProject.owner}/${this.getProject.title}/add_team_member/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Added team member ${user.username} to project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add team member ${user.username} to project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to add team member ${user.username} to project ${this.getProject.title}`,
                        guid: guid().toString()
                    });
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                    throw error;
                });
        },
        async removeTeamMember() {
            this.removingTeamMember = true;
            let user = this.teamMemberToRemove;
            let data = { username: user.id };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.getProject.owner}/${this.getProject.title}/remove_team_member/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Removed team member ${user.id} from project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove team member ${user.id} from project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.teamMemberToRemove = null;
                    this.removingTeamMember = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove team member ${user.id} from project ${this.getProject.title}`,
                        guid: guid().toString()
                    });
                    this.removingTeamMember = false;
                    throw error;
                });
        },
        async refreshUsers() {
            await this.$store.dispatch('users/loadAll');
        },
        showAddStudyModal() {
            this.$bvModal.show('addStudy');
        },
        hideAddStudyModal() {
            this.$bvModal.hide('addStudy');
        },
        showRemoveStudyModal(study) {
            this.studyToRemove = study;
            this.$bvModal.show('removeStudy');
        },
        hideRemoveStudyModal() {
            this.$bvModal.hide('removeStudy');
        },
        async addStudy() {
            this.addingStudy = true;
            let data = {
                title: this.studyTitle,
                description: this.studyDescription
            };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.getProject.owner}/${this.getProject.title}/add_study/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Added study ${this.studyTitle} to project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add study ${this.studyTitle} to project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.hideAddStudyModal();
                    this.addingStudy = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to add study ${this.studyTitle} to project ${this.getProject.title}`,
                        guid: guid().toString()
                    });
                    this.hideAddStudyModal();
                    this.addingStudy = false;
                    throw error;
                });
        },
        async removeStudy() {
            this.removingStudy = true;
            let study = this.studyToRemove;
            let data = { title: study.title };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.getProject.owner}/${this.getProject.title}/remove_study/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Removed study ${study.title} from project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove study ${study.title} from project ${this.getProject.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.removingStudy = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove study ${study.title} from project ${this.getProject.title}`,
                        guid: guid().toString()
                    });
                    this.removingStudy = false;
                    throw error;
                });
        },
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
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
        ownsProject() {
            return (
                this.getProject.owner === this.profile.djangoProfile.username
            );
        },
        getProject() {
            let project = this.personalProjects.find(
                p =>
                    p.owner === this.$router.currentRoute.params.owner &&
                    p.title === this.$router.currentRoute.params.title
            );
            if (project !== undefined && project !== null) return project;
            return null;
        },
        studyTitleExists() {
            return this.getProject.studies.some(
                s => s.title === this.studyTitle
            );
        },
        studyTitleValid() {
            return this.studyTitle !== '' && !this.studyTitleExists;
        },
        studyDescriptionValid() {
            return this.studyDescription !== '';
        },
        studyInfoValid() {
            return this.studyTitleValid && this.studyDescriptionValid;
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
