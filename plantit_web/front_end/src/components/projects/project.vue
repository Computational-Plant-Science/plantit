<template>
    <div>
        <b-container class="p-2 vl" fluid>
            <b-row v-if="projectsLoading"
                ><b-col
                    ><b-spinner
                        small
                        v-if="projectsLoading"
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="mr-1"
                    ></b-spinner
                    ><span
                        :class="profile.darkMode ? 'text-white' : 'text-dark'"
                        >Loading project...</span
                    ></b-col
                ></b-row
            >
            <b-card
                v-else
                :bg-variant="profile.darkMode ? 'dark' : 'white'"
                border-variant="secondary"
                :header-text-variant="profile.darkMode ? 'white' : 'dark'"
                :text-variant="profile.darkMode ? 'white' : 'dark'"
                :body-text-variant="profile.darkMode ? 'white' : 'dark'"
                no-body
            >
                <b-card-body>
                    <b-row
                        ><b-col>
                            <h4
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                {{ getProject.title }}
                            </h4></b-col
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
                    <i>{{ getProject.guid }}</i>
                    <h6 v-if="getProject.description !== null">
                        {{ getProject.description }}
                    </h6>
                    <span v-if="getProject.submission_date !== null">
                        <small
                            >Submitted:
                            {{
                                prettifyDate(getProject.submission_date)
                            }}</small
                        >
                        <br />
                    </span>
                    <span v-if="getProject.public_release_date !== null">
                        <small
                            >Released:
                            {{
                                prettifyDate(getProject.public_release_date)
                            }}</small
                        >
                        <br />
                    </span>
                    <br />
                    <b-row>
                        <b-col
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Studies
                            </h5></b-col
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
                                v-if="profile.hints"
                                triggers="hover"
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
                    <b-card
                        v-for="study in getProject.studies"
                        v-bind:key="study.title"
                        class="mt-2 pt-1"
                        :bg-variant="profile.darkMode ? 'dark' : 'white'"
                        :header-text-variant="
                            profile.darkMode ? 'white' : 'dark'
                        "
                        border-variant="secondary"
                        :text-variant="profile.darkMode ? 'white' : 'dark'"
                        :body-text-variant="profile.darkMode ? 'white' : 'dark'"
                        no-body
                    >
                        <b-card-body>
                            <b-row
                                ><b-col>
                                    <b>{{ study.title }}</b></b-col
                                ><b-col
                                    class="ml-0"
                                    md="auto"
                                    align-self="center"
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
                                            'Edit ' + study.title + ' details'
                                        "
                                        @click="showEditStudyModal(study)"
                                    >
                                        <i class="fas fa-edit fa-fw"></i>
                                        Edit
                                    </b-button></b-col
                                ><b-col
                                    class="ml-0"
                                    md="auto"
                                    align-self="center"
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
                            ><b-row
                                ><b-col
                                    ><span
                                        v-if="
                                            study.description !== null &&
                                            study.description !== ''
                                        "
                                        >{{ study.description }}<br />
                                    </span>
                                    <span v-else
                                        ><i>No description</i><br />
                                    </span>
                                    <span v-if="study.start_date !== null">
                                        <small
                                            ><b>Started</b>
                                            {{
                                                prettifyDate(study.start_date)
                                            }}</small
                                        >
                                        <br />
                                    </span>
                                    <span v-if="study.end_date !== null">
                                        <small
                                            ><b>Ends</b>
                                            {{
                                                prettifyDate(study.end_date)
                                            }}</small
                                        >
                                        <br />
                                    </span>
                                    <span
                                        v-if="
                                            study.contact_institution !== null
                                        "
                                    >
                                        <small
                                            ><b>Contact Institution:</b>
                                            {{
                                                study.contact_institution
                                            }}</small
                                        >
                                        <br />
                                    </span>
                                    <span v-if="study.country !== null">
                                        <small
                                            ><b>Country:</b>
                                            {{ study.country }}</small
                                        >
                                        <br />
                                    </span>
                                    <span v-if="study.site_name !== null">
                                        <small
                                            ><b>Site:</b>
                                            {{ study.site_name }}</small
                                        >
                                        <br />
                                    </span>
                                    <span v-if="study.latitude !== null">
                                        <small
                                            ><b>Latitude:</b>
                                            {{ study.latitude }}</small
                                        >
                                        <br />
                                    </span>
                                    <span v-if="study.longitude !== null">
                                        <small
                                            ><b>Longitude:</b>
                                            {{ study.longitude }}</small
                                        >
                                        <br />
                                    </span>
                                    <span v-if="study.altitude !== null">
                                        <small
                                            ><b>Altitude:</b>
                                            {{ study.altitude }}</small
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
                                            ><b>Experimental Design:</b> [{{
                                                study.experimental_design_type
                                            }}]
                                        </small>
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
                                            study.observation_unit_description !==
                                            null
                                        "
                                    >
                                        <small
                                            ><b>Observation Unit:</b>
                                            <span
                                                v-if="
                                                    study.observation_unit_level_hierarchy !==
                                                    null
                                                "
                                            >
                                                [{{
                                                    study.observation_unit_level_hierarchy
                                                }}]</span
                                            >
                                        </small>
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
                                            study.growth_facility_type !== null
                                        "
                                    >
                                        <small
                                            ><b>Growth Facility:</b> [{{
                                                study.growth_facility_type
                                            }}]
                                        </small>
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
                                        v-if="study.cultural_practices !== null"
                                    >
                                        <small
                                            ><b>Cultural Practices:</b>
                                            {{
                                                study.cultural_practices
                                            }}</small
                                        >
                                    </span></b-col
                                ></b-row
                            >
                        </b-card-body>
                    </b-card>
                    <br />
                    <br />
                    <b-row>
                        <b-col
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Team Members
                            </h5></b-col
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
                                @click="specifyTeamMember()"
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
                                v-if="profile.hints"
                                triggers="hover"
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
                        v-bind:key="member.username"
                        ><b-col align-self="center"
                            ><b-img
                                v-if="avatarUrl(member) !== undefined"
                                class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                                style="
                                    width: 2rem;
                                    height: 2rem;
                                    left: -3px;
                                    top: 1.5px;
                                    border: 1px solid #e2e3b0;
                                "
                                rounded="circle"
                                :src="avatarUrl(member)"
                            ></b-img>
                            <i v-else class="far fa-user fa-fw mr-1"></i>
                            <b>{{ member.name }}</b>
                            ({{ member.username }}),
                            <span>{{ member.affiliation }}</span></b-col
                        ><b-col class="ml-0" md="auto" align-self="center"
                            ><b-button
                                class="ml-0"
                                variant="outline-danger"
                                size="sm"
                                v-b-tooltip.hover
                                :title="
                                    'Remove ' +
                                    member.username +
                                    ' from this project'
                                "
                                @click="showRemoveTeamMemberModal(member)"
                            >
                                <i class="fas fa-times-circle fa-fw"></i>
                                Remove
                            </b-button></b-col
                        >
                    </b-row>
                    <br />
                    <br />
                    <b-row>
                        <b-col
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Workflows
                            </h5></b-col
                        >
                    </b-row>
                    <span v-if="getWorkflows.length === 0"
                        >This project has no associated workflows.</span
                    >
                    <b-card-group deck columns v-else>
                        <b-card
                            v-for="workflow in getWorkflows"
                            :key="`${workflow.repo.owner.login}/${workflow.repo.name}/${workflow.branch.name}`"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-bg-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            border-variant="default"
                            :header-border-variant="
                                profile.darkMode ? 'secondary' : 'default'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
                            style="min-width: 30rem"
                            class="overflow-hidden mb-4"
                        >
                            <workflowblurb
                                :linkable="true"
                                :workflow="workflow"
                            ></workflowblurb>
                        </b-card>
                    </b-card-group>
                    <br />
                    <br />
                    <b-row>
                        <b-col
                            ><h5
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Tasks
                            </h5></b-col
                        >
                    </b-row>
                    <b-row
                        class="text-left m-0 p-0 mt-1"
                        v-if="projectTasks.length > 0"
                        ><b-col>
                            <taskblurb
                                v-for="task in projectTasks"
                                v-bind:key="task.guid"
                                :task="task"
                                :project="false"
                            ></taskblurb>
                        </b-col>
                    </b-row>
                    <b-row v-else
                        ><b-col
                            >You haven't run any tasks associated with this
                            project.</b-col
                        ></b-row
                    >
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
                            style="
                                width: 2rem;
                                height: 2rem;
                                left: -3px;
                                top: 1.5px;
                                border: 1px solid #e2e3b0;
                            "
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
                    :class="profile.darkMode ? 'input-dark' : 'input-light'"
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
                    :class="profile.darkMode ? 'input-dark' : 'input-light'"
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
            :title="`Remove ${
                this.teamMemberToRemove !== null
                    ? this.teamMemberToRemove.username
                    : 'team member'
            }?`"
            @ok="removeTeamMember"
            ok-variant="danger"
        >
            <p :class="profile.darkMode ? 'text-light' : 'text-dark'">
                This person will no longer have access to this project.
            </p>
        </b-modal>
        <b-modal
            id="editStudy"
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
            :title="`Edit ${
                this.studyToEdit !== null ? this.studyToEdit.title : 'study'
            }`"
            @ok="editStudy"
            ok-variant="success"
        >
            <div v-if="studyToEdit !== null">
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >A brief description of this study.</span
                        ></template
                    >
                    <b-form-textarea
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyDescription"
                        :placeholder="
                            studyToEdit.description !== ''
                                ? studyToEdit.description
                                : 'Enter a description'
                        "
                        required
                    ></b-form-textarea>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study's start date.</span
                        ></template
                    >
                    <b-form-datepicker
                        v-model="studyStartDate"
                        :max="today"
                        :placeholder="
                            studyToEdit.start_date !== ''
                                ? studyToEdit.start_date
                                : 'Select a start date'
                        "
                        required
                    ></b-form-datepicker>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study's end date.</span
                        ></template
                    >
                    <b-form-datepicker
                        v-model="studyEndDate"
                        :min="today"
                        :placeholder="
                            studyToEdit.end_date !== ''
                                ? studyToEdit.end_date
                                : 'Select an end date'
                        "
                        required
                    ></b-form-datepicker>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study's contact institution.</span
                        ></template
                    >
                    <b-form-input
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyContactInstitution"
                        :placeholder="
                            studyToEdit.contact_institution !== ''
                                ? studyToEdit.contact_institution
                                : 'Enter an institution'
                        "
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study site's country.</span
                        ></template
                    >
                    <b-form-input
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyCountry"
                        :placeholder="
                            studyToEdit.country !== ''
                                ? studyToEdit.country
                                : 'Enter a country'
                        "
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study site's name.</span
                        ></template
                    >
                    <b-form-input
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studySiteName"
                        :placeholder="
                            studyToEdit.site_name !== ''
                                ? studyToEdit.site_name
                                : 'Enter a site name'
                        "
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study site's latitude.</span
                        ></template
                    >
                    <b-form-spinbutton
                        v-model="studyLatitude"
                        :placeholder="
                            studyToEdit.latitude !== 0
                                ? studyToEdit.latitude
                                : 'Select a latitude'
                        "
                        required
                    ></b-form-spinbutton>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study site's longitude.</span
                        ></template
                    >
                    <b-form-spinbutton
                        v-model="studyLongitude"
                        :placeholder="
                            studyToEdit.longitude !== 0
                                ? studyToEdit.longitude
                                : 'Select a longitude'
                        "
                        required
                    ></b-form-spinbutton>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study site's altitude.</span
                        ></template
                    >
                    <b-form-spinbutton
                        v-model="studyAltitude"
                        :placeholder="
                            studyToEdit.altitude !== 0
                                ? studyToEdit.altitude
                                : 'Select an altitude'
                        "
                        required
                    ></b-form-spinbutton>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >Altitude units.</span
                        ></template
                    >
                    <b-form-select
                        v-model="studyAltitudeUnits"
                        :options="studyAltitudeUnitsOptions"
                        :placeholder="
                            studyToEdit.altitude_units !== ''
                                ? studyToEdit.altitude_units
                                : 'Select altitude units'
                        "
                        required
                    ></b-form-select>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >A brief description of this study's experimental
                            design.</span
                        ></template
                    >
                    <b-form-textarea
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyExperimentalDesignDescription"
                        :placeholder="
                            studyToEdit.experimental_design_description !== ''
                                ? studyToEdit.experimental_design_description
                                : 'Enter an experimental design description'
                        "
                        required
                    ></b-form-textarea>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >A brief description of this study's experimental
                            type.</span
                        ></template
                    >
                    <b-form-input
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyExperimentalDesignType"
                        :placeholder="
                            studyToEdit.experimental_design_type !== ''
                                ? studyToEdit.experimental_design_type
                                : 'Enter an experimental design type'
                        "
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >A brief description of this study's observation
                            unit.</span
                        ></template
                    >
                    <b-form-textarea
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyObservationUnitDescription"
                        :placeholder="
                            studyToEdit.observation_unit_description !== ''
                                ? studyToEdit.observation_unit_description
                                : 'Enter an observation unit description'
                        "
                        required
                    ></b-form-textarea>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >A brief description of this study's growth
                            facility.</span
                        ></template
                    >
                    <b-form-textarea
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyGrowthFacilityDescription"
                        :placeholder="
                            studyToEdit.growth_facility_description !== ''
                                ? studyToEdit.growth_facility_description
                                : 'Enter a growth facility description'
                        "
                        required
                    ></b-form-textarea>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >This study's growth facility type.</span
                        ></template
                    >
                    <b-form-input
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyGrowthFacilityType"
                        :placeholder="
                            studyToEdit.growth_facility_type !== ''
                                ? studyToEdit.growth_facility_type
                                : 'Enter a growth facility type'
                        "
                        required
                    ></b-form-input>
                </b-form-group>
                <b-form-group>
                    <template #description
                        ><span
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                            >Any relevant cultural practices.</span
                        ></template
                    >
                    <b-form-input
                        :class="profile.darkMode ? 'input-dark' : 'input-light'"
                        v-model="studyCulturalPractices"
                        :placeholder="
                            studyToEdit.cultural_practices !== ''
                                ? studyToEdit.cultural_practices
                                : 'Enter cultural practices'
                        "
                        required
                    ></b-form-input>
                </b-form-group>
                <hr />
                <b-row>
                    <b-col>
                        <div class="a-var-title mb-2">
                            <h5
                                id="additional-variables"
                                v-b-tooltip.hover
                                title="Use this section to define any additional variables."
                            >
                                Additional Variables
                            </h5>
                        </div>
                    </b-col>
                </b-row>

                <b-row>
                    <b-col
                        ><b-form-group
                            ><b-form-input
                                :class="
                                    profile.darkMode
                                        ? 'input-dark'
                                        : 'input-light'
                                "
                                v-model="environmentParameterKey"
                                placeholder="Enter a key"
                                required
                            ></b-form-input></b-form-group></b-col
                    ><b-col
                        ><b-form-group
                            ><b-form-input
                                :class="
                                    profile.darkMode
                                        ? 'input-dark'
                                        : 'input-light'
                                "
                                v-model="environmentParameterValue"
                                placeholder="Enter a value"
                                required
                            ></b-form-input></b-form-group
                    ></b-col>
                    <b-col
                        ><b-button @click="addEnvironmentParameter"
                            >Add</b-button
                        ></b-col
                    >
                </b-row>
                <b-row>
                    <b-col> <u>Key/Variable</u> </b-col>
                    <b-col> <u>Value</u></b-col>
                    <b-col></b-col>
                </b-row>

                <b-row
                    v-for="key in Object.keys(environmentParameters)"
                    v-bind:key="key"
                    class="mb-3"
                    ><b-col>{{ key }}</b-col>
                    <b-col> {{ environmentParameters[key] }}</b-col>
                    <b-col
                        ><b-button @click="removeEnvironmentParameter(key)"
                            >Remove</b-button
                        ></b-col
                    ></b-row
                >
            </div>
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
            :title="`Remove ${
                this.studyToRemove !== null ? this.studyToRemove.title : 'study'
            }?`"
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
import workflowblurb from '@/components/workflows/workflow-blurb.vue';
import taskblurb from '@/components/tasks/task-blurb.vue';

export default {
    name: 'project',
    components: {
        workflowblurb,
        taskblurb,
    },
    data: function () {
        return {
            addingTeamMember: false,
            removingTeamMember: false,
            teamMemberToRemove: null,
            addingStudy: false,
            removingStudy: false,
            studyTitle: '',
            studyDescription: '',
            studyStartDate: '',
            studyEndDate: '',
            studyContactInstitution: '',
            studyCountry: '',
            studySiteName: '',
            studyLatitude: 0,
            studyLongitude: 0,
            studyAltitude: 0,
            studyAltitudeUnits: 'ft',
            studyAltitudeUnitsOptions: [
                { value: 'ft', text: 'Feet' },
                { value: 'm', text: 'Meters' },
            ],
            studyExperimentalDesignDescription: '',
            studyExperimentalDesignType: '',
            // studyExperimentalDesignMap: '',
            // studyObservationUnitLevelHierarchy: '',
            studyObservationUnitDescription: '',
            studyGrowthFacilityDescription: '',
            studyGrowthFacilityType: '',
            studyCulturalPractices: '',
            studyToRemove: null,
            studyToEdit: null,
            deleting: false,

            environmentParameterKey: '',
            environmentParameterValue: '',
            environmentParameters: {},
        };
    },
    methods: {
        addEnvironmentParameter() {
            if (this.environmentParameterKey in this.environmentParameters) {
                alert('This is a duplicate key');
                this.environmentParameterKey = '';
                this.environmentParameterValue = '';
                return;
            }

            this.$set(
                this.environmentParameters,
                this.environmentParameterKey,
                this.environmentParameterValue
            );

            (this.environmentParameterKey = ''),
                (this.environmentParameterValue = '');
        },
        removeEnvironmentParameter(key) {
            if (key in this.environmentParameters) {
                this.$delete(this.environmentParameters, key);
            }
        },
        showEditStudyModal(study) {
            this.studyToEdit = study;
            this.$bvModal.show('editStudy');
        },
        hideEditStudyModal() {
            this.studyToEdit = null;
            this.$bvModal.hide('editStudy');
        },
        async editStudy() {
            this.editingStudy = true;
            let data = {
                title: this.studyToEdit.title,
                description:
                    this.studyDescription !== ''
                        ? this.studyDescription
                        : this.studyToEdit.description,
                start_date:
                    this.studyStartDate !== ''
                        ? this.studyStartDate
                        : this.studyToEdit.start_date,
                end_date:
                    this.studyEndDate !== ''
                        ? this.studyEndDate
                        : this.studyToEdit.end_date,
                contact_institution:
                    this.studyContactInstitution !== ''
                        ? this.studyContactInstitution
                        : this.studyToEdit.contact_institution,
                country:
                    this.studyCountry !== ''
                        ? this.studyCountry
                        : this.studyToEdit.country,
                site_name:
                    this.studySiteName !== ''
                        ? this.studySiteName
                        : this.studyToEdit.site_name,
                latitude:
                    this.studyLatitude !== 0
                        ? this.studyLatitude
                        : this.studyToEdit.latitude,
                longitude:
                    this.studyLongitude !== 0
                        ? this.studyLongitude
                        : this.studyToEdit.longitude,
                altitude:
                    this.studyAltitude !== 0
                        ? this.studyAltitude
                        : this.studyToEdit.altitude,
                experimental_design_description:
                    this.studyExperimentalDesignDescription !== ''
                        ? this.studyExperimentalDesignDescription
                        : this.studyToEdit.experimental_design_description,
                experimental_design_type:
                    this.studyExperimentalDesignType !== ''
                        ? this.studyExperimentalDesignType
                        : this.studyToEdit.experimental_design_type,
                // experimental_design_map: this.studyToEdit.experimental_design_map,
                // observation_unit_level_hierarchy: this.studyToEdit.observation_unit_level_hierarchy,
                observation_unit_description:
                    this.studyObservationUnitDescription !== ''
                        ? this.studyObservationUnitDescription
                        : this.studyToEdit.observation_unit_description,
                growth_facility_description:
                    this.studyGrowthFacilityDescription !== ''
                        ? this.studyGrowthFacilityDescription
                        : this.studyToEdit.growth_facility_description,
                growth_facility_type:
                    this.studyGrowthFacilityType !== ''
                        ? this.studyGrowthFacilityType
                        : this.studyToEdit.growth_facility_type,
                cultural_practices:
                    this.studyCulturalPractices !== ''
                        ? this.studyCulturalPractices
                        : this.studyToEdit.cultural_practices,
                environment_parameters:
                    Object.keys(this.environmentParameters).length > 0
                        ? this.environmentParameters
                        : this.studyToEdit.environment_parameters,
            };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}/edit_study/`,
                headers: { 'Content-Type': 'application/json' },
                data: data,
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await Promise.all([
                            this.$store.dispatch(
                                'projects/addOrUpdate',
                                response.data
                            ),
                            this.$store.dispatch('alerts/add', {
                                variant: 'success',
                                message: `Updated study ${this.studyToEdit.title}`,
                                guid: guid().toString(),
                            }),
                        ]);
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to update study ${this.studyToEdit.title}`,
                            guid: guid().toString(),
                        });
                    }
                    this.editingStudy = false;
                    this.hideEditStudyModal();
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to update study ${this.studyToEdit.title}`,
                        guid: guid().toString(),
                    });
                    this.editingStudy = false;
                    throw error;
                });
        },
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
                headers: { 'Content-Type': 'application/json' },
            })
                .then((response) => {
                    if (response.status === 200) {
                        this.$store.dispatch(
                            'projects/setUser',
                            response.data.projects
                        );
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Deleted project ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}`,
                            guid: guid().toString(),
                        });
                        router.push({
                            name: 'projects',
                        });
                    } else {
                        this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to delete project ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}`,
                            guid: guid().toString(),
                        });
                    }
                    this.deleting = false;
                    this.hideDeleteProjectModal();
                })
                .catch((error) => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to delete project ${this.$router.currentRoute.params.owner}/${this.$router.currentRoute.params.title}`,
                        guid: guid().toString(),
                    });
                    this.deleting = false;
                    throw error;
                });
        },
        avatarUrl(user) {
            let found = this.otherUsers.find(
                (u) => u.username === user.username
            );
            if (found === undefined) return undefined;
            if (found.github_profile === undefined) return undefined;
            if (found.github_profile.avatar_url === '') return undefined;
            return found.github_profile.avatar_url;
        },
        specifyTeamMember() {
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
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Added team member ${user.username} to project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add team member ${user.username} to project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    }
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to add team member ${user.username} to project ${this.getProject.title}`,
                        guid: guid().toString(),
                    });
                    this.$bvModal.hide('addTeamMember');
                    this.addingTeamMember = false;
                    throw error;
                });
        },
        async removeTeamMember() {
            this.removingTeamMember = true;
            let user = this.teamMemberToRemove;
            let data = { username: user.username };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.getProject.owner}/${this.getProject.title}/remove_team_member/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Removed team member ${user.username} from project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove team member ${user.username} from project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    }
                    this.teamMemberToRemove = null;
                    this.removingTeamMember = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove team member ${user.username} from project ${this.getProject.title}`,
                        guid: guid().toString(),
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
                description: this.studyDescription,
            };
            await axios({
                method: 'post',
                url: `/apis/v1/miappe/${this.getProject.owner}/${this.getProject.title}/add_study/`,
                data: data,
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Added study ${this.studyTitle} to project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to add study ${this.studyTitle} to project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    }
                    this.hideAddStudyModal();
                    this.addingStudy = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to add study ${this.studyTitle} to project ${this.getProject.title}`,
                        guid: guid().toString(),
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
                headers: { 'Content-Type': 'application/json' },
            })
                .then(async (response) => {
                    if (response.status === 200) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Removed study ${study.title} from project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    } else {
                        await this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to remove study ${study.title} from project ${this.getProject.title}`,
                            guid: guid().toString(),
                        });
                    }
                    this.removingStudy = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to remove study ${study.title} from project ${this.getProject.title}`,
                        guid: guid().toString(),
                    });
                    this.removingStudy = false;
                    throw error;
                });
        },
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        prettifyDate: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY'
            )})`;
        },
    },
    watch: {
        studyToEdit() {
            // this.userProjects.map(() => {});
        },
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        ...mapGetters('projects', [
            'userProjects',
            'othersProjects',
            'projectsLoading',
        ]),
        ...mapGetters('workflows', [
            'projectWorkflows',
            'projectWorkflowsLoading',
        ]),
        ...mapGetters('tasks', [
            'tasks',
            'tasksRunning',
            'tasksCompleted',
            'tasksLoading',
        ]),
        today() {
            let now = new Date();
            return new Date(now.getFullYear(), now.getMonth(), now.getDate());
        },
        getWorkflows() {
            // return this.projectWorkflows[this.getProject.guid];
            return this.getProject.workflows;
        },
        projectTasks() {
            return this.tasks.filter(
                (t) =>
                    t.project !== null &&
                    t.project.guid === this.getProject.guid
            );
        },
        ownsProject() {
            return (
                this.getProject.owner === this.profile.djangoProfile.username
            );
        },
        getProject() {
            let project = this.userProjects.find(
                (p) =>
                    p.owner === this.$router.currentRoute.params.owner &&
                    p.title === this.$router.currentRoute.params.title
            );
            if (project !== undefined && project !== null) return project;
            return null;
        },
        studyTitleExists() {
            return this.getProject.studies.some(
                (s) => s.title === this.studyTitle
            );
        },
        studyTitleValid() {
            return this.studyTitle !== '' && !this.studyTitleExists;
        },
        studyDescriptionValid() {
            return this.studyDescription !== '';
        },
        studyStartDateValid() {
            return this.studyStartDate !== '';
        },
        studyEndDateValid() {
            return true;
            // return this.studyEndDate !== '';
        },
        studyContactInstitutionValid() {
            return true;
            // return this.studyContactInstitution !== '';
        },
        studyCountryValid() {
            return true;
            // return this.studyCountry !== '';
        },
        studySiteNameValid() {
            return true;
            // return this.studyCountry !== '';
        },
        studyLatitudeValid() {
            return true;
            // return this.studyLatitude !== 0;
        },
        studyLongitudeValid() {
            return true;
            // return this.studyLongitude !== 0;
        },
        studyAltitudeValid() {
            return true;
            // return this.studyAltitude !== 0;
        },
        studyAltitudeUnitsValid() {
            return true;
        },
        studyExperimentalDesignDescriptionValid() {
            return true;
            // return this.studyExperimentalDesignDescription !== '';
        },
        studyExperimentalDesignTypeValid() {
            return true;
            // return this.studyExperimentalDesignType !== '';
        },
        studyObservationUnitDescriptionValid() {
            return true;
            // return this.studyObservationUnitDescription !== '';
        },
        studyGrowthFacilityDescriptionValid() {
            return true;
            // return this.studyGrowthFacilityDescription !== '';
        },
        studyGrowthFacilityTypeValid() {
            return true;
            // return this.studyGrowthFacilityType !== '';
        },
        studyCulturalPracticesValid() {
            return true;
            // return this.studyCulturalPractices !== '';
        },
        studyInfoValid() {
            return this.studyTitleValid && this.studyDescriptionValid;
        },
        otherUsers() {
            return this.allUsers.filter(
                (u) =>
                    u.username !== this.profile.djangoProfile.username &&
                    !this.getProject.team.some(
                        (ua) => ua.username === u.username
                    )
            );
        },
    },
};
</script>

<style scoped>
.a-var-title {
    display: flex;
    justify-content: center;
}
</style>
