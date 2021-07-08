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
                                style="max-width: 55px"
                                :src="
                                    profile.darkMode
                                        ? require('../../assets/miappe_icon.png')
                                        : require('../../assets/miappe_icon_black.png')
                                "
                            ></b-img>
                            Your MIAPPE Metadata
                        </h2></b-col
                    >
                </b-row>
                <b-row
                    ><b-col
                        ><h5>Your Investigations</h5>
                        <span v-if="personalInvestigations.length === 0"
                            >You haven't started any investigations.</span
                        >
                        <b-card-group
                            ><b-card
                                v-for="investigation in personalInvestigations"
                                v-bind:key="investigation.unique_id"
                                :title="investigation.title"
                                :sub-title="investigation.unique_id"
                                no-body
                            >
                                <b-card-body>
                                    <h4>{{ investigation.title }}</h4>
                                    <h6
                                        v-if="
                                            investigation.description !== null
                                        "
                                    >
                                        {{ investigation.description }}
                                    </h6>
                                    <small
                                        v-if="
                                            investigation.submission_date !==
                                                null
                                        "
                                        >Submission:
                                        {{
                                            prettify(
                                                investigation.submission_date
                                            )
                                        }}</small
                                    >
                                    <br />
                                    <small
                                        v-if="
                                            investigation.public_release_date !==
                                                null
                                        "
                                        >Release:
                                        {{
                                            prettify(
                                                investigation.public_release_date
                                            )
                                        }}</small
                                    >
                                    <br />
                                    <br />
                                    <b-row>
                                        <b-col><h5>Studies</h5></b-col
                                        ><b-col md="auto"></b-col>
                                    </b-row>
                                    <span
                                        v-if="
                                            investigation.studies.length === 0
                                        "
                                        >This investigation has no
                                        studies.</span
                                    >
                                    <b-card-group>
                                        <b-card
                                            v-for="study in investigation.studies"
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
                                        <b-col><h5>Team Members</h5></b-col
                                        ><b-col md="auto"
                                            ><b-button
                                                id="add-member"
                                                :disabled="addingTeamMember"
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                size="sm"
                                                v-b-tooltip.hover
                                                title="Add a team member"
                                                @click="
                                                    specifyTeamMember(
                                                        investigation
                                                    )
                                                "
                                                class="ml-0 mt-0 mr-0"
                                            >
                                                <b-spinner
                                                    small
                                                    v-if="addingTeamMember"
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
                                                target="add-member"
                                                title="Add Team Member"
                                                >Click here to add a team member
                                                to this
                                                investigation.</b-popover
                                            ></b-col
                                        >
                                    </b-row>
                                    <span v-if="investigation.team.length === 0"
                                        >You are the only researcher in this
                                        investigation.</span
                                    >
                                    <b-card-group>
                                        <b-card
                                            v-for="member in investigation.team"
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
                                                        ({{ member.id }}), <span>{{
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
                                                                    ' from this investigation'
                                                            "
                                                            @click="
                                                                removeTeamMember(
                                                                    investigation,
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
                            </b-card></b-card-group
                        ></b-col
                    ><b-col
                        ><h5>Others' Investigations</h5>
                        <span v-if="othersInvestigations.length === 0"
                            >You have not been invited to any
                            investigations.</span
                        >
                        <b-card-group>
                            <b-card
                                v-for="investigation in othersInvestigations"
                                v-bind:key="investigation.unique_id"
                                :title="investigation.title"
                                :sub-title="investigation.unique_id"
                                no-body
                            >
                                <b-card-body>
                                    <h4>{{ investigation.title }}</h4>
                                    <h6
                                        v-if="
                                            investigation.description !== null
                                        "
                                    >
                                        {{ investigation.description }}
                                    </h6>
                                    <small>Owner: {{ investigation.owner }}</small>
                                  <br/>
                                    <small
                                        v-if="
                                            investigation.submission_date !==
                                                null
                                        "
                                        >Submission:
                                        {{
                                            prettify(
                                                investigation.submission_date
                                            )
                                        }}</small
                                    >
                                    <br />
                                    <small
                                        v-if="
                                            investigation.public_release_date !==
                                                null
                                        "
                                        >Release:
                                        {{
                                            prettify(
                                                investigation.public_release_date
                                            )
                                        }}</small
                                    >
                                    <br />
                                    <br />
                                    <b-row>
                                        <b-col><h5>Studies</h5></b-col
                                        ><b-col md="auto"></b-col>
                                    </b-row>
                                    <span
                                        v-if="
                                            investigation.studies.length === 0
                                        "
                                        >This investigation has no
                                        studies.</span
                                    >
                                    <b-card-group>
                                        <b-card
                                            v-for="study in investigation.studies"
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
                                        <b-col><h5>Team Members</h5></b-col
                                        >
                                    </b-row>
                                    <span v-if="investigation.team.length === 1"
                                        >You are the only team member in this
                                        investigation.</span
                                    >
                                    <b-card-group>
                                        <b-card
                                            v-for="member in investigation.team.filter(u => u.id !== profile.djangoProfile.username)"
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
                                                        ({{ member.id }}), <span>{{
                                                            member.affiliation
                                                        }}</span></b-col
                                                    >
                                                </b-row>
                                            </b-card-body></b-card
                                        ></b-card-group
                                    >
                                </b-card-body>
                            </b-card></b-card-group></b-col
                ></b-row>
            </div>
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
                    Select a user to invite to this investigation.
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
import axios from 'axios';
import { guid } from '@/utils';
import * as Sentry from '@sentry/browser';

export default {
    name: 'miappe.vue',
    data: function() {
        return {
            selectedInvestigation: null,
            addingTeamMember: false,
            removingTeamMember: false
        };
    },
    methods: {
        avatarUrl(user) {
            let found = this.otherUsers.find(u => u.username === user.id);
            if (found === undefined) return undefined;
            return found.github_profile.avatar_url;
        },
        specifyTeamMember(investigation) {
            this.selectedInvestigation = investigation;
            this.$bvModal.show('addTeamMember');
        },
        async addTeamMember(investigation, user) {
            this.addingTeamMember = true;
            let data = { username: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${investigation.owner}/${investigation.unique_id}/add_team_member/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'investigations/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Added team member ${user.username} to investigation ${investigation.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add team member ${user.username} to investigation ${investigation.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to add team member ${user.username} to investigation ${investigation.title}`,
                        guid: guid().toString()
                    });
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                    throw error;
                });
        },
        async removeTeamMember(investigation, user) {
            this.removingTeamMember = true;
            let data = { username: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${investigation.owner}/${investigation.unique_id}/remove_team_member/`,
                data: data,
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'investigations/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Removed team member ${user.username} from investigation ${investigation.title}`,
                            guid: guid().toString()
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove team member ${user.username} from investigation ${investigation.title}`,
                            guid: guid().toString()
                        });
                    }
                    this.removingTeamMember = false;
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove team member ${user.username} from investigation ${investigation.title}`,
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
        ...mapGetters('miappe', [
            'personalInvestigations',
            'othersInvestigations'
        ]),
        isRootPath() {
            return this.$route.name === 'miappe';
        },
        investigationSelected() {
            return this.selectedInvestigation !== null;
        },
        otherUsers() {
            return this.allUsers.filter(
                u =>
                    u.username !== this.profile.djangoProfile.username &&
                    ((this.investigationSelected &&
                        !this.selectedInvestigation.team.some(
                            ua => ua.id === u.username
                        )) ||
                        !this.investigationSelected)
            );
        }
    }
};
</script>

<style scoped></style>
