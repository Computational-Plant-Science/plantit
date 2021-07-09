<template>
  <div>
        <b-container class="p-2 vl" fluid >
            <b-row v-if="projectsLoading"><b-col><b-spinner variant="secondary" type="grow"></b-spinner></b-col></b-row>
            <b-card v-else
                :title="getProject.title"
                :sub-title="getProject.unique_id"
                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :text-variant="profile.darkMode ? 'white' : 'dark'"
                :body-text-variant="profile.darkMode ? 'white' : 'dark'"
                no-body
            >
                <b-card-body>
                    <h4>{{ getProject.title }}</h4>
                    <h6 v-if="getProject.description !== null">
                        {{ getProject.description }}
                    </h6>
                    <small v-if="getProject.submission_date !== null"
                        >Submission:
                        {{ prettify(getProject.submission_date) }}</small
                    >
                    <br />
                    <small v-if="getProject.public_release_date !== null"
                        >Release:
                        {{ prettify(getProject.public_release_date) }}</small
                    >
                    <br />
                    <br />
                    <b-row>
                        <b-col><h5>Studies</h5></b-col><b-col md="auto"></b-col>
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
                                <b>{{ study.title }}</b
                                ><br /><span>{{ study.description }}</span
                                ><br />
                                <br />
                                <small
                                    >Start:
                                    {{ prettify(study.start_date) }}</small
                                >
                                <br />
                                <small
                                    >End: {{ prettify(study.end_date) }}</small
                                >
                                <br />
                                <small
                                    >Contact Institution:
                                    {{ study.contact_institution }}</small
                                >
                                <br />
                                <small>Country: {{ study.country }}</small>
                                <br />
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
                            v-for="member in getProject.team"
                            v-bind:key="member.id"
                            no-body
                            ><b-card-body
                                ><b-row
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
                                        <span>{{
                                            member.affiliation
                                        }}</span></b-col
                                    ><b-col
                                        class="ml-0"
                                        md="auto"
                                        align-self="middle"
                                        ><b-button
                                            class="ml-0"
                                            :variant="
                                                profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            size="sm"
                                            v-b-tooltip.hover
                                            :title="
                                                'Remove ' +
                                                    member.id +
                                                    ' from this project'
                                            "
                                            @click="
                                                removeTeamMember(
                                                    getProject,
                                                    member
                                                )
                                            "
                                        >
                                            <i
                                                class="fas fa-times-circle fa-fw"
                                            ></i>
                                            Remove
                                        </b-button></b-col
                                    >
                                </b-row>
                            </b-card-body></b-card
                        ></b-card-group
                    >
                </b-card-body>
            </b-card>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import { guid } from '@/utils';
import * as Sentry from '@sentry/browser';
import moment from 'moment';

export default {
    name: 'project',
    data: function() {
        return {
            addingTeamMember: false,
            removingTeamMember: false,
            addingStudy: false,
            removingStudy: false
        };
    },
    methods: {
        avatarUrl(user) {
            let found = this.otherUsers.find(u => u.username === user.id);
            if (found === undefined) return undefined;
            return found.github_profile.avatar_url;
        },
        specifyTeamMember(project) {
            this.selectedInvestigation = project;
            this.$bvModal.show('addTeamMember');
        },
        async addTeamMember(project, user) {
            this.addingTeamMember = true;
            let data = { username: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${project.owner}/${project.unique_id}/add_team_member/`,
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
                            message: `Added team member ${user.username} to project ${project.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add team member ${user.username} to project ${project.title}`,
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
                        message: `Failed to add team member ${user.username} to project ${project.title}`,
                        guid: guid().toString()
                    });
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                    throw error;
                });
        },
        async removeTeamMember(project, user) {
            this.removingTeamMember = true;
            let data = { username: user.id };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${project.owner}/${project.unique_id}/remove_team_member/`,
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
                            message: `Removed team member ${user.id} from project ${project.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove team member ${user.id} from project ${project.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.removingTeamMember = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove team member ${user.id} from project ${project.title}`,
                        guid: guid().toString()
                    });
                    this.removingTeamMember = false;
                    throw error;
                });
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
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        ...mapGetters('projects', [
            'personalProjects',
            'othersProjects',
            'projectsLoading'
        ]),
        getProject() {
            let project = this.personalProjects.find(
                p =>
                    p.owner === this.$router.currentRoute.params.owner &&
                    p.title === this.$router.currentRoute.params.title
            );
            if (project !== undefined && project !== null) return project;
            return null;
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
