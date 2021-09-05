<template>
    <b-list-group flush class="m-0">
        <b-row v-if="showSharedAlert">
            <b-col class="m-0 p-0">
                <b-alert
                    :show="showSharedAlert"
                    :variant="
                        sharedAlertMessage.startsWith('Failed')
                            ? 'danger'
                            : 'success'
                    "
                    dismissible
                    @dismissed="showSharedAlert = false"
                >
                    {{ sharedAlertMessage }}
                </b-alert>
            </b-col>
        </b-row>
        <b-row
            v-if="isDir && internalLoaded && node !== null"
            class="mt-1 mb-1 ml-2 mr-0 p-0 text-left"
        >
            <b-col
                :style="{
                    'font-weight': isDir ? '500' : '300'
                }"
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-button
                    :title="(internalLoaded ? internalNode : node).path"
                    size="sm"
                    :variant="profile.darkMode ? 'outline-light' : 'white'"
                    :disabled="
                        !select ||
                            (select !== 'directory' && select !== 'files')
                    "
                    @click="
                        selectNode(
                            internalLoaded ? internalNode : node,
                            'directory'
                        )
                    "
                    ><i class="fas fa-folder fa-fw mr-2"></i>
                    <i
                        v-if="
                            sprout ===
                                (internalLoaded ? internalNode.path : node.path)
                        "
                        class="fas fa-seedling fa-fw mr-2 text-success"
                    ></i>
                    {{ internalLoaded ? internalNode.label : node.label }}
                </b-button>
            </b-col>
            <b-col class="mt-1" md="auto">
                <small>
                    {{
                        isDir
                            ? `${subDirCount} ${
                                  subDirCount === 1
                                      ? 'subdirectory'
                                      : 'subdirectories'
                              }, ${fileCount} ${
                                  fileCount === 1 ? 'file' : 'files'
                              }`
                            : ''
                    }}</small
                ><small v-if="isShared">, shared by {{ sharedBy }}</small>
            </b-col>
            <b-col
                class="mt-1"
                md="auto"
                v-if="
                    matchingSharingDatasets !== undefined &&
                        matchingSharingDatasets !== null &&
                        matchingSharingDatasets.length > 0
                "
            >
                <small
                    >Shared with
                    {{ matchingSharingDatasets.length }} user(s)</small
                >
            </b-col>
            <b-col
                :id="
                    `associated-studies-${
                        internalLoaded ? internalNode.label : node.label
                    }`
                "
                class="mt-1 ml-1"
                :class="profile.darkMode ? 'text-light' : 'text-dark'"
                md="auto"
                v-if="isPersonalDirectory && !isRoot"
                ><span v-if="associatedStudies.length > 0"
                    ><b-img
                        class="mb-1 mr-1"
                        style="max-width: 18px"
                        :src="
                            profile.darkMode
                                ? require('../../assets/miappe_icon.png')
                                : require('../../assets/miappe_icon_black.png')
                        "
                    ></b-img
                    ><small
                        >{{ associatedStudies.length }} associated
                        {{
                            associatedStudies.length === 1
                                ? 'project/study'
                                : 'projects/studies'
                        }}</small
                    ><b-popover
                        :target="
                            `associated-studies-${
                                internalLoaded ? internalNode.label : node.label
                            }`
                        "
                        placement="bottom"
                        triggers="hover"
                        :variant="profile.darkMode ? 'dark' : 'light'"
                    >
                        <b-row
                            v-for="study in associatedStudies"
                            v-bind:key="study.title"
                            ><b-col align-self="center"
                                ><b-link
                                    class="text-dark"
                                    :to="{
                                        name: 'project',
                                        params: {
                                            owner: study.project_owner,
                                            title: study.project_title
                                        }
                                    }"
                                    ><b class="text-dark"
                                        >{{ study.project_title }},
                                        {{ study.title }}</b
                                    ></b-link
                                ></b-col
                            ><b-col md="auto" align-self="center"
                                ><b-button
                                    title="Unbind project/study"
                                    size="sm"
                                    v-b-tooltip.hover
                                    variant="outline-danger"
                                    @click="
                                        preUnbindProject(
                                            projectFor(study),
                                            study
                                        )
                                    "
                                    ><i
                                        class="fas fa-minus fa-fw"
                                    ></i></b-button></b-col
                        ></b-row> </b-popover></span
                ><b-button
                    title="Bind project/study"
                    size="sm"
                    :variant="profile.darkMode ? 'outline-light' : 'white'"
                    v-else
                    @click="preBindProject"
                    ><b-img
                        class="mb-1 mr-1"
                        style="max-width: 18px"
                        :src="
                            profile.darkMode
                                ? require('../../assets/miappe_icon.png')
                                : require('../../assets/miappe_icon_black.png')
                        "
                    ></b-img
                    >Bind project/study</b-button
                ></b-col
            >
            <b-col md="auto">
                <b-input-group size="sm">
                    <!--<b-form-file
                        v-if="upload && !isShared"
                        style="min-width: 15rem"
                        :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
                        multiple
                        size="sm"
                        v-model="filesToUpload"
                        :placeholder="
                            'Upload to \'' +
                                (internalLoaded
                                    ? internalNode.label
                                    : node.label) +
                                '\''
                        "
                        :drop-placeholder="
                            'Upload to \'' +
                                (internalLoaded
                                    ? internalNode.label
                                    : node.label) +
                                '\''
                        "
                    ></b-form-file>
                    <b-button
                        v-if="upload && !isShared"
                        class="ml-1 mr-1"
                        size="sm"
                        :disabled="filesToUpload.length === 0"
                        @click="
                            uploadFiles(
                                filesToUpload,
                                internalLoaded ? internalNode.path : node.path,
                                profile.djangoProfile.cyverse_token
                            )
                        "
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        ><i class="fas fa-upload fa-fw"></i
                    ></b-button>-->
                    <span v-if="create">
                        <b-button
                            v-if="!isShared"
                            class="ml-1 mr-1"
                            size="sm"
                            title="Create Subdirectory"
                            @click="showCreateDirectoryModal"
                            :variant="
                                profile.darkMode
                                    ? 'outline-light'
                                    : 'outline-dark'
                            "
                            ><i class="fas fa-plus fa-fw"></i
                        ></b-button>
                        <b-button
                            v-if="!isShared && !isRoot"
                            class="ml-1 mr-1"
                            size="sm"
                            :disabled="deletingDirectory"
                            title="Delete Subdirectory"
                            @click="
                                deletePath(
                                    internalLoaded
                                        ? internalNode.path
                                        : node.path,
                                    profile.djangoProfile.cyverse_token
                                )
                            "
                            :variant="
                                profile.darkMode
                                    ? 'outline-light'
                                    : 'outline-dark'
                            "
                            ><i class="fas fa-trash text-danger fa-fw"></i
                        ></b-button>
                        <b-modal
                            :title-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            title="Bind Project"
                            :id="
                                'bindProject' +
                                    (internalLoaded
                                        ? internalNode.label
                                        : node.label)
                            "
                            centered
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
                            close
                            :ok-disabled="selectedProject === null"
                            @ok="
                                bindProject(
                                    internalLoaded
                                        ? internalNode.path
                                        : node.path
                                )
                            "
                        >
                            <b-row
                                ><b-col
                                    ><b
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        Select the MIAPPE project and study this
                                        task corresponds to.
                                    </b>
                                </b-col>
                            </b-row>
                            <b-row
                                v-if="personalProjects.length > 0"
                                class="mt-2"
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    cols="3"
                                    ><i>Project</i></b-col
                                ><b-col
                                    cols="9"
                                    :class="
                                        profile.darkMode
                                            ? 'text-light'
                                            : 'text-dark'
                                    "
                                    v-if="selectedProject !== null"
                                    ><i>Study</i></b-col
                                ></b-row
                            >
                            <b-row v-else class="mt-2"
                                ><b-col cols="3"
                                    ><i
                                        >You haven't started any projects.</i
                                    ></b-col
                                ></b-row
                            >
                            <b-row
                                class="mt-1"
                                v-for="project in personalProjects"
                                v-bind:key="project.title"
                                ><b-col
                                    style="border-top: 2px solid lightgray;"
                                    cols="3"
                                >
                                    <b-button
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        @click="selectedProject = project"
                                        >{{ project.title
                                        }}<i
                                            v-if="
                                                selectedProject !== null &&
                                                    selectedProject.title ===
                                                        project.title
                                            "
                                            class="fas fa-check fa-fw text-success ml-1"
                                        ></i
                                    ></b-button> </b-col
                                ><b-col
                                    style="border-top: 2px solid lightgray; left: -5px"
                                    cols="9"
                                    v-if="selectedProject !== null"
                                    ><b-row
                                        v-for="study in project.studies"
                                        v-bind:key="study.title"
                                        ><b-col
                                            ><b-button
                                                :disabled="
                                                    project.title !==
                                                        selectedProject.title
                                                "
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'white'
                                                "
                                                @click="selectedStudy = study"
                                                >{{ study.title
                                                }}<i
                                                    v-if="
                                                        selectedStudy !==
                                                            null &&
                                                            selectedStudy.title ===
                                                                study.title &&
                                                            selectedProject ===
                                                                project
                                                    "
                                                    class="fas fa-check fa-fw ml-1 text-success"
                                                ></i></b-button></b-col></b-row></b-col></b-row
                        ></b-modal>
                        <b-modal
                            v-if="!isShared"
                            :title-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            title="Create Directory"
                            :id="
                                'createDirectoryModal' +
                                    (internalLoaded
                                        ? internalNode.label
                                        : node.label)
                            "
                            centered
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
                            close
                            @close="hideCreateDirectoryModal"
                            @ok="
                                createDirectory(
                                    (internalLoaded
                                        ? internalNode.path
                                        : node.path) +
                                        '/' +
                                        newDirectoryName,
                                    profile.djangoProfile.cyverse_token
                                )
                            "
                        >
                            <b-form-group>
                                <template #description
                                    ><span
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        >The directory name</span
                                    ></template
                                >
                                <b-form-input
                                    :class="
                                        profile.darkMode
                                            ? 'input-dark'
                                            : 'input-light'
                                    "
                                    size="sm"
                                    v-model="newDirectoryName"
                                    :placeholder="'Enter a directory name'"
                                ></b-form-input>
                            </b-form-group>
                            <div v-if="showingProjectSelection">
                                <b-row class="mb-1"
                                    ><b-col
                                        ><b-button
                                            @click="hideProjectSelection"
                                            block
                                            :variant="
                                                profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            ><i
                                                class="fas fa-times text-danger fa-fw"
                                            ></i>
                                            Hide Project Selection</b-button
                                        ></b-col
                                    ></b-row
                                >
                                <b-row
                                    ><b-col
                                        ><b
                                            :class="
                                                profile.darkMode
                                                    ? 'text-white'
                                                    : 'text-dark'
                                            "
                                        >
                                            Select the MIAPPE project and study
                                            this task corresponds to.
                                        </b>
                                    </b-col>
                                </b-row>
                                <b-row
                                    v-if="personalProjects.length > 0"
                                    class="mt-2"
                                    ><b-col
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        cols="3"
                                        ><i>Project</i></b-col
                                    ><b-col
                                        cols="9"
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        v-if="selectedProject !== null"
                                        ><i>Study</i></b-col
                                    ></b-row
                                >
                                <b-row v-else class="mt-2"
                                    ><b-col cols="3"
                                        ><i
                                            >You haven't started any
                                            projects.</i
                                        ></b-col
                                    ></b-row
                                >
                                <b-row
                                    class="mt-1"
                                    v-for="project in personalProjects"
                                    v-bind:key="project.title"
                                    ><b-col
                                        style="border-top: 2px solid lightgray;"
                                        cols="3"
                                    >
                                        <b-button
                                            :variant="
                                                profile.darkMode
                                                    ? 'outline-light'
                                                    : 'white'
                                            "
                                            @click="selectedProject = project"
                                            >{{ project.title
                                            }}<i
                                                v-if="
                                                    selectedProject !== null &&
                                                        selectedProject.title ===
                                                            project.title
                                                "
                                                class="fas fa-check fa-fw text-success ml-1"
                                            ></i
                                        ></b-button> </b-col
                                    ><b-col
                                        style="border-top: 2px solid lightgray; left: -5px"
                                        cols="9"
                                        v-if="selectedProject !== null"
                                        ><b-row
                                            v-for="study in project.studies"
                                            v-bind:key="study.title"
                                            ><b-col
                                                ><b-button
                                                    :disabled="
                                                        project.title !==
                                                            selectedProject.title
                                                    "
                                                    :variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'white'
                                                    "
                                                    @click="
                                                        selectedStudy = study
                                                    "
                                                    >{{ study.title
                                                    }}<i
                                                        v-if="
                                                            selectedStudy !==
                                                                null &&
                                                                selectedStudy.title ===
                                                                    study.title &&
                                                                selectedProject ===
                                                                    project
                                                        "
                                                        class="fas fa-check fa-fw ml-1 text-success"
                                                    ></i></b-button></b-col></b-row></b-col
                                ></b-row>
                            </div>
                            <b-row v-else
                                ><b-col
                                    ><b-button
                                        @click="showProjectSelection"
                                        block
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
                                        ><b-img
                                            class="mb-1"
                                            style="max-width: 18px"
                                            :src="
                                                profile.darkMode
                                                    ? require('../../assets/miappe_icon.png')
                                                    : require('../../assets/miappe_icon_black.png')
                                            "
                                        ></b-img>
                                        Show Project Selection</b-button
                                    ></b-col
                                ></b-row
                            >
                        </b-modal>
                        <b-modal
                            :title-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            title="Unbind Project"
                            :id="
                                'unbindProject' +
                                    (internalLoaded
                                        ? internalNode.label
                                        : node.label)
                            "
                            centered
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
                            close
                            @ok="unbindProject()"
                            ok-variant="danger"
                        >
                            <p
                                v-if="
                                    projectToUnbind !== null &&
                                        studyToUnbind !== null
                                "
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Project <b>{{ projectToUnbind.title }}</b> study
                                <b>{{ studyToUnbind.title }}</b> will no longer
                                be bound to directory
                                <b>{{
                                    internalLoaded
                                        ? internalNode.path
                                        : node.path
                                }}</b
                                >.
                            </p>
                        </b-modal>
                    </span>
                    <b-button
                        v-if="internalLoaded && !internalLoading"
                        class="ml-1 mr-1"
                        title="Refresh Directory"
                        size="sm"
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        @click="refresh"
                    >
                        <i class="fas fa-sync-alt fa-fw"></i>
                    </b-button>
                    <br />
                    <b-spinner
                        v-if="internalLoaded && internalLoading"
                        variant="secondary"
                        type="grow"
                        label="Loading"
                    ></b-spinner>
                    <b-button
                        v-if="
                            !internalLoading &&
                                internalNode.path.split('/').length > 4 &&
                                !isShared
                        "
                        title="Share Directory"
                        size="sm"
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        @click="showShareDirectoryModal"
                        class="ml-1 mr-1"
                        ><i class="fas fa-share-alt fa-fw"></i
                    ></b-button>
                    <!--<b-dropdown
                        class="mr-1 ml-1"
                        v-if="
                            internalLoaded &&
                                !internalLoading &&
                                internalNode.path.split('/').length > 4
                        "
                        title="Open Dataset"
                        size="sm"
                        dropleft
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                    >
                        <template #button-content>
                            <i class="fas fa-folder-open fa-fw"></i>
                        </template>
                        <b-dropdown-text>
                            Select a agent to open this dataset.
                        </b-dropdown-text>
                        <b-dropdown-divider></b-dropdown-divider>
                        <b-dropdown-text
                            v-if="
                                agents !== undefined &&
                                    agents !== null &&
                                    agents.length === 0
                            "
                            ><b class="text-danger"
                                >You have no agent permissions.</b
                            ><br />See
                            <b-link
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                                to="/agents"
                                ><i class="fas fa-server fa-1x fa-fw"></i>
                                Agents</b-link
                            >
                            to request guest access to public servers, clusters,
                            and supercomputers.</b-dropdown-text
                        >
                        <b-dropdown-item
                            @click="openDataset(agent)"
                            v-for="agent in agents"
                            v-bind:key="agent.name"
                            >{{ agent.name }}</b-dropdown-item
                        >
                    </b-dropdown>-->
                    <b-modal
                        v-if="!isShared"
                        :title-class="
                            profile.darkMode ? 'text-white' : 'text-dark'
                        "
                        :title="
                            'Share ' +
                                (internalLoaded ? internalNode.path : node.path)
                        "
                        size="lg"
                        centered
                        :header-text-variant="
                            profile.darkMode ? 'white' : 'dark'
                        "
                        :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                        :footer-bg-variant="profile.darkMode ? 'dark' : 'white'"
                        :body-bg-variant="profile.darkMode ? 'dark' : 'white'"
                        :header-border-variant="
                            profile.darkMode ? 'dark' : 'white'
                        "
                        :footer-border-variant="
                            profile.darkMode ? 'dark' : 'white'
                        "
                        @ok="shareDataset"
                        @close="hideShareDirectoryModal"
                        :id="
                            'shareDirectoryModal' +
                                (internalLoaded
                                    ? internalNode.label
                                    : node.label)
                        "
                        ><b-container fluid>
                            <b-row
                                ><b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                    ><small
                                        >Choose who to share this directory
                                        with.</small
                                    ></b-col
                                ><b-col md="auto"
                                    ><b-button
                                        :disabled="usersLoading"
                                        :variant="
                                            profile.darkMode
                                                ? 'outline-light'
                                                : 'white'
                                        "
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
                                            :variant="
                                                profile.darkMode
                                                    ? 'light'
                                                    : 'dark'
                                            "
                                            class="mr-1"
                                        ></b-spinner
                                        ><i v-else class="fas fa-redo mr-1"></i
                                        >Rescan Users</b-button
                                    ></b-col
                                >
                            </b-row>
                            <b-row v-if="usersLoading"
                                ><b-col align-self="end" class="text-center">
                                    <b-spinner
                                        type="grow"
                                        label="Loading..."
                                        variant="secondary"
                                    ></b-spinner> </b-col
                            ></b-row>
                            <b-row
                                v-else-if="sharingUsers.length > 0"
                                align-v="center"
                                align-h="center"
                            >
                                <b-col>
                                    <b-form>
                                        <b-form-group
                                            v-slot="{ ariaDescribedby }"
                                        >
                                            <b-form-checkbox-group
                                                v-model="sharedUsers"
                                                stacked
                                                :aria-describedby="
                                                    ariaDescribedby
                                                "
                                                buttons
                                                :variant="
                                                    profile.darkMode
                                                        ? 'outline-light'
                                                        : 'outline-dark'
                                                "
                                                size="lg"
                                            >
                                                <b-form-checkbox
                                                    size="sm"
                                                    button
                                                    :button-variant="
                                                        profile.darkMode
                                                            ? 'outline-light'
                                                            : 'outline-dark'
                                                    "
                                                    v-for="user in sharingUsers"
                                                    v-model="sharedUsers"
                                                    v-bind:key="user.username"
                                                    :value="user.username"
                                                    ><b-img
                                                        v-if="
                                                            user.github_profile
                                                        "
                                                        class="avatar m-0 mb-1 mr-2 p-0 github-hover logo"
                                                        style="width: 2rem; height: 2rem; left: -3px; top: 1.5px; border: 1px solid #e2e3b0;"
                                                        rounded="circle"
                                                        :src="
                                                            user.github_profile
                                                                ? user
                                                                      .github_profile
                                                                      .avatar_url
                                                                : ''
                                                        "
                                                    ></b-img>
                                                    <i
                                                        v-else
                                                        class="far fa-user fa-fw mr-2 ml-2"
                                                    ></i
                                                    ><b
                                                        >{{ user.first_name }}
                                                        {{ user.last_name }}</b
                                                    >
                                                    ({{ user.username }})
                                                    <i
                                                        v-if="
                                                            sharedUsers.includes(
                                                                user.username
                                                            )
                                                        "
                                                        class="fas fa-check"
                                                    ></i
                                                ></b-form-checkbox>
                                            </b-form-checkbox-group>
                                        </b-form-group>
                                    </b-form>
                                    <!--<b-card-group
                                        deck
                                        columns
                                        class="justify-content-center"
                                    >
                                        <b-card
                                            v-for="user in users"
                                            :key="user.username"
                                            :bg-variant="
                                                profile.darkMode ? 'dark' : 'white'
                                            "
                                            :header-bg-variant="
                                                profile.darkMode ? 'dark' : 'white'
                                            "
                                            border-variant="default"
                                            :header-border-variant="
                                                profile.darkMode
                                                    ? 'secondary'
                                                    : 'default'
                                            "
                                            :text-variant="
                                                profile.darkMode ? 'white' : 'dark'
                                            "
                                            style="min-width: 30rem; max-width: 40rem;"
                                            class="overflow-hidden mb-4"
                                        >
                                            <b-row align-v="center">
                                                <b-col
                                                    style="color: white; cursor: pointer"
                                                    @click="userSelected(user)"
                                                >
                                                    <h5
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-white'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        {{ user.first_name }}
                                                        {{ user.last_name }}
                                                        <small
                                                            :class="
                                                                profile.darkMode
                                                                    ? 'text-warning'
                                                                    : 'text-dark'
                                                            "
                                                            >({{
                                                                user.username
                                                            }})</small
                                                        >
                                                    </h5>
                                                </b-col>
                                            </b-row>
                                            <b-row align-v="center">
                                                <b-col
                                                    :class="
                                                        profile.darkMode
                                                            ? 'text-white'
                                                            : 'text-dark'
                                                    "
                                                >
                                                    {{
                                                        user.github_profile
                                                            ? user
                                                                  .github_profile
                                                                  .bio
                                                            : ''
                                                    }}
                                                </b-col>
                                            </b-row>
                                            <br />
                                            <b-row
                                                v-if="user.github_username"
                                                align-v="center"
                                            >
                                                <b-col>
                                                    <b-link
                                                        :class="
                                                            profile.darkMode
                                                                ? 'text-white'
                                                                : 'text-dark'
                                                        "
                                                        :href="
                                                            'https://github.com/' +
                                                                user.github_username
                                                        "
                                                    >
                                                        <i
                                                            class="fab fa-github fa-fw fa-1x mr-2 ml-1 pl-1"
                                                        ></i>
                                                        <small>{{
                                                            user.github_username
                                                        }}</small>
                                                    </b-link>
                                                </b-col>
                                                <b-col
                                                    class="ml-0 mr-0"
                                                    align-self="left"
                                                >
                                                    <b-img
                                                        right
                                                        rounded
                                                        class="avatar card-img-right"
                                                        style="max-height: 4rem; max-width: 4rem; opacity: 0.9; position: absolute; right: -15px; top: -25px; z-index:1;"
                                                        :src="
                                                            user.github_profile
                                                                .avatar_url
                                                        "
                                                    ></b-img>
                                                </b-col>
                                            </b-row>
                                        </b-card>
                                    </b-card-group>-->
                                </b-col>
                            </b-row>
                            <b-row v-else><b-col></b-col></b-row> </b-container
                    ></b-modal>
                    <!--<b-button
                        v-if="
                            internalLoaded &&
                                (internalLoaded
                                    ? internalNode.path
                                    : node.path
                                ).split('/').length > 4 &&
                                !isShared
                        "
                        class="ml-1 mr-1"
                        size="sm"
                        title="Delete Directory"
                        @click="
                            deletePath(
                                internalLoaded ? internalNode.path : node.path,
                                profile.djangoProfile.cyverse_token
                            )
                        "
                        variant="outline-danger"
                        ><i class="fas fa-trash fa-fw"></i
                    ></b-button>-->
                    <b-button
                        class="ml-1 mr-1"
                        title="Expand Directory"
                        v-if="!isOpen"
                        size="sm"
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        @click="toggle"
                    >
                        <i class="fas fa-caret-up fa-fw"></i> </b-button
                    ><b-button
                        class="ml-1 mr-1"
                        title="Collapse Directory"
                        v-else
                        size="sm"
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        @click="toggle"
                        :disabled="deleting"
                    >
                        <i class="fas fa-caret-down fa-fw"></i>
                    </b-button> </b-input-group
            ></b-col>
        </b-row>
        <b-row
            align-h="center"
            align-v="center"
            class="text-center text-secondary"
        >
            <b-col v-if="uploading">
                <small>Uploading...</small>
                <b-spinner class="ml-1" variant="secondary" small></b-spinner>
            </b-col>
        </b-row>
        <b-row
            align-h="center"
            align-v="center"
            class="text-center text-secondary"
        >
            <b-col v-if="creatingDirectory">
                <small>Creating directory...</small>
                <b-spinner class="ml-1" variant="secondary" small></b-spinner>
            </b-col>
        </b-row>
        <b-row
            align-h="center"
            align-v="center"
            class="text-center text-secondary"
        >
            <b-col v-if="deleting">
                <small>Deleting...</small>
                <b-spinner class="ml-1" variant="secondary" small></b-spinner>
            </b-col>
        </b-row>
        <b-row v-if="isDir && !internalLoaded" class="mt-0 mb-0 ml-2 mr-0 p-0">
            <b-col :class="profile.darkMode ? 'theme-dark' : 'theme-light'">
                <b-button
                    size="sm"
                    :variant="profile.darkMode ? 'outline-light' : 'white'"
                    class="ml-1 mr-1"
                    :disabled="
                        !select ||
                            (select !== 'directory' && select !== 'files')
                    "
                    @click="
                        selectNode(
                            internalLoaded ? internalNode : node,
                            'directory'
                        )
                    "
                    ><i class="fas fa-folder fa-fw mr-2"></i
                    >{{
                        internalLoaded ? internalNode.label : node.label
                    }}</b-button
                >
            </b-col>
            <b-col
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
                md="auto"
            >
                <b-button
                    v-if="
                        internalLoaded &&
                            (internalLoaded
                                ? internalNode.path
                                : node.path
                            ).split('/').length > 4 &&
                            !isShared
                    "
                    class="ml-1 mr-1"
                    size="sm"
                    :disabled="deletingDirectory"
                    title="Delete Directory"
                    @click="
                        deletePath(
                            internalLoaded ? internalNode.path : node.path,
                            profile.djangoProfile.cyverse_token
                        )
                    "
                    variant="outline-danger"
                    ><i class="fas fa-trash fa-fw"></i
                ></b-button>
                <b-button
                    title="Expand Directory"
                    class="ml-1 mr-1"
                    size="sm"
                    :variant="profile.darkMode ? 'outline-light' : 'white'"
                    @click="
                        loadDirectory(
                            internalLoaded ? internalNode.path : node.path,
                            profile.djangoProfile.cyverse_token
                        )
                    "
                    ><i
                        v-if="!internalLoaded && !internalLoading"
                        class="fas fa-caret-up fa-fw"
                    ></i>
                    <b-spinner
                        small
                        v-else-if="!internalLoaded && internalLoading"
                        variant="secondary"
                        type="grow"
                        label="Loading"
                    ></b-spinner
                ></b-button>
            </b-col>
        </b-row>
        <b-list-group-item
            class="mt-2 mb-1 ml-2 mr-0 p-0"
            style="background-color: transparent;"
            v-show="isOpen"
            v-if="isDir && internalLoaded"
            :variant="profile.darkMode ? 'outline-light' : 'outline-dark'"
        >
            <b-row v-show="numFiles > filePageSize"
                ><b-col md="auto" align-self="center" class="ml-2">
                    <b-pagination
                        v-model="filePage"
                        pills
                        class="mt-3"
                        size="md"
                        :total-rows="numFiles"
                        :per-page="filePageSize"
                        aria-controls="files"
                    >
                        <template class="theme-dark" #page="{ page, active }">
                            <b v-if="active">{{ page }}</b>
                            <i v-else>{{ page }}</i>
                        </template>
                    </b-pagination>
                </b-col></b-row
            >
            <b-row
                id="files"
                class="mt-1 mb-1 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5);"
                v-for="(child, index) in filteredFiles"
                :key="index"
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-col>
                    <b-img-lazy
                        v-if="previewsLoaded && fileIsImage(child.label)"
                        :src="getFileURL(child)"
                        style="width: 3rem; height: 3rem"
                    ></b-img-lazy>
                    <b-button
                        class="mt-1 mb-1 ml-4"
                        :disabled="!select || select !== 'file'"
                        size="sm"
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        @click="selectNode(child, 'file')"
                        ><i class="fas fa-file fa-fw"></i>
                        {{ child.label }}</b-button
                    >
                </b-col>
                <b-col md="auto" align-self="center"
                    ><small>{{ formatBytes(child['file-size']) }}</small></b-col
                >
                <b-col md="auto" align-self="center">
                    <b-button
                        id="popover-reactive-1"
                        :disabled="!fileIsImage(child.label)"
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        class="m-1"
                        size="sm"
                        v-b-tooltip.hover
                        :title="'View ' + child.label"
                        @click="viewFile(child)"
                    >
                        <i class="fas fa-eye fa-fw"></i>
                    </b-button>
                    <b-button
                        v-if="!isShared"
                        class="m-1"
                        size="sm"
                        title="Delete File"
                        @click="
                            deletePath(
                                child.path,
                                profile.djangoProfile.cyverse_token
                            )
                        "
                        variant="outline-danger"
                        ><i class="fas fa-trash fa-fw"></i></b-button
                    ><b-button
                        class="m-1"
                        size="sm"
                        title="Download File"
                        @click="
                            downloadFile(
                                child.path,
                                profile.djangoProfile.cyverse_token
                            )
                        "
                        :variant="
                            profile.darkMode ? 'outline-light' : 'outline-dark'
                        "
                        ><i class="fas fa-download fa-fw"></i></b-button
                ></b-col>
            </b-row>
        </b-list-group-item>
        <b-list-group-item
            class="mt-2 mb-1 ml-2 mr-0 p-0"
            style="background-color: transparent;"
            v-for="(child, index) in internalLoaded
                ? internalLoadedFolders
                : node.folders"
            v-bind:key="child.path"
            v-show="isOpen"
            :variant="profile.darkMode ? 'outline-light' : 'outline'"
        >
            <data-tree
                class="pt-1 pb-1 mb-0 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5); border-left: 2px solid rgba(211, 211, 211, .5)"
                :select="select"
                :upload="upload"
                :download="download"
                :create="create"
                :agents="agents"
                :sprout="sprout"
                title="Upload file(s)"
                @selectPath="selectNode(child, 'directory')"
                @deleted="waitForDeletion(child.path)"
                :key="index"
                :node="child"
            ></data-tree>
        </b-list-group-item>
        <b-modal
            v-if="
                internalLoaded && internalNode !== null && selectedFile !== null
            "
            ok-only
            :body-bg-variant="profile.darkMode ? 'dark' : 'light'"
            :header-bg-variant="profile.darkMode ? 'dark' : 'light'"
            :footer-bg-variant="profile.darkMode ? 'dark' : 'light'"
            :title-class="profile.darkMode ? 'text-white' : 'text-dark'"
            :header-text-variant="profile.darkMode ? 'white' : 'dark'"
            :body-text-variant="profile.darkMode ? 'white' : 'dark'"
            :footer-border-variant="profile.darkMode ? 'dark' : 'white'"
            :header-border-variant="profile.darkMode ? 'dark' : 'white'"
            ok-variant="secondary"
            ok-title="Close"
            size="xl"
            centered
            :title="selectedFileTitle"
            :id="'selectedFile' + internalNode.path"
            class="overflow-hidden"
            @close="onSelectedFileClosed"
        >
            <b-spinner
                v-if="!previewsLoaded"
                type="grow"
                label="Loading..."
                variant="secondary"
            ></b-spinner>
            <b-img
                v-if="fileIsImage(selectedFile.label)"
                center
                :src="fileURLs[selectedFile.path]"
                style="width: 68rem"
                v-show="previewsLoaded"
            >
            </b-img>
            <b-embed
                v-else-if="fileIsText(selectedFile.label)"
                type="iframe"
                :src="fileURLs[selectedFile.path]"
            ></b-embed>
        </b-modal>
    </b-list-group>
</template>
<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import { guid } from '@/utils';

export default {
    name: 'data-tree',
    props: {
        node: {
            required: true,
            type: Object
        },
        select: {
            required: false,
            type: String
        },
        create: {
            required: false,
            type: Boolean
        },
        upload: {
            required: false,
            type: Boolean
        },
        download: {
            required: false,
            type: Boolean
        },
        agents: {
            required: false,
            type: Array
        },
        sprout: {
            required: false,
            type: String
        }
    },
    data: function() {
        return {
            internalNode: null,
            internalLoading: false,
            internalLoaded: false,
            isOpen: false,
            filesToUpload: [],
            filesToDownload: [],
            uploading: false,
            deleting: false,
            creatingDirectory: false,
            deletingDirectory: false,
            newDirectoryName: '',
            uploadingIntervalId: '',
            creatingDirectoryIntervalId: '',
            deletingIntervalId: '',
            downloading: false,
            sharedUsers: [],
            sharedAlertMessage: '',
            showSharedAlert: false,
            // selected file view
            selectedFileLoading: true,
            selectedFileTitle: '',
            selectedFile: null,
            fileURLs: [],
            previewsLoaded: false,
            selectedProject: null,
            selectedStudy: null,
            showingProjectSelection: false,
            bindingProject: false,
            unbindingProject: false,
            projectToUnbind: null,
            studyToUnbind: null,
            // file paging
            filePage: 1,
            filePageSize: 10
        };
    },
    mounted: {},
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        ...mapGetters('projects', [
            'personalProjects',
            'projectsLoading',
            'othersProjects'
        ]),
        ...mapGetters('datasets', [
            'sharingDatasets',
            'sharingDatasetsLoading'
        ]),
        numFiles() {
            return (this.internalLoaded
                ? this.internalNode.files
                : this.node.files
            ).length;
        },
        filteredFiles() {
            return (this.internalLoaded
                ? this.internalNode.files
                : this.node.files
            ).slice(
                (this.filePage - 1) * this.filePageSize,
                this.filePage * this.filePageSize
            );
        },
        matchingSharingDatasets() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            return this.sharingDatasets.filter(d => d.path === path);
        },
        associatedStudies() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            if (this.projectsLoading) return [];
            let projects = this.personalProjects
                .concat(this.othersProjects)
                .filter(p =>
                    p.studies.some(s => s.dataset_paths.includes(path))
                );
            return projects
                .flatMap(p => p.studies)
                .filter(s => s.dataset_paths.includes(path))
                .map(s => {
                    return {
                        title: s.title,
                        project_title: s.project_title,
                        project_owner: s.project_owner
                    };
                });
        },
        internalLoadedFolders() {
            return this.internalNode !== null ? this.internalNode.folders : [];
        },
        sharedBy: function() {
            if (this.isShared) {
                let path = this.internalLoaded
                    ? this.internalNode.path
                    : this.node.path;
                let split = path.split('/');
                return split[3];
            } else return null;
        },
        isShared: function() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            let split = path.split('/');
            let user = split[3];
            return (
                user !== this.profile.djangoProfile.username &&
                user !== 'shared'
            );
        },
        isDir: function() {
            return !('file-size' in this);
        },
        isPersonalDirectory() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            let isPersonal = path.startsWith(
                `/iplant/home/${this.profile.djangoProfile.username}`
            );
            return isPersonal;
        },
        isRoot() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            let isRootPath =
                path ===
                    `/iplant/home/${this.profile.djangoProfile.username}` ||
                path === `/iplant/home/${this.profile.djangoProfile.username}/`;
            return isRootPath;
        },
        sharingUsers() {
            let username = this.profile.djangoProfile.username;
            return (
                this.allUsers
                    // .map(function(user) {
                    //     return {
                    //         value: user.username,
                    //         text: user.username
                    //         // avatar: user.github_profile.avatar_url
                    //     };
                    // })
                    .filter(function(item) {
                        return item.username !== username;
                    })
            );
        },
        subDirCount: function() {
            return this.internalLoaded
                ? this.internalNode.folders
                    ? this.internalNode.folders.length
                    : 0
                : this.node.folders
                ? this.node.folders.length
                : 0;
        },
        fileCount: function() {
            return this.internalLoaded
                ? this.internalNode.files
                    ? this.internalNode.files.length
                    : 0
                : this.node.files
                ? this.node.files.length
                : 0;
        }
    },
    watch: {
        internalLoadedFolders() {
            //
        },
        filePage() {
            this.loadFileURLs();
        }
    },
    methods: {
        getFileURL(file) {
            // let url = await this.fileURL(file);
            // return url['url'];
            if (file.path in this.fileURLs) return this.fileURLs[file.path];
            return null;
        },
        async loadFileURLs() {
            this.previewsLoaded = false;
            if (
                this.internalLoaded &&
                this.internalNode !== null &&
                this.internalNode.files !== undefined &&
                this.internalNode.files !== null
            ) {
                await Promise.all(
                    (this.internalLoaded
                        ? this.internalNode.files
                        : this.node.files
                    )
                        .slice(
                            (this.filePage - 1) * this.filePageSize,
                            this.filePage * this.filePageSize
                        )
                        .map(f => this.fileURL(f))
                ).then(urls => {
                    for (const url of urls)
                        this.fileURLs[url['path']] = url['url'];
                });
            }
            this.previewsLoaded = true;
        },
        async fileURL(file) {
            var result = null;
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/fileio/download?path=${file.path}`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.profile.djangoProfile.cyverse_token
                        },
                        responseType: 'blob'
                    }
                )
                .then(response => {
                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    result = {
                        path: file.path,
                        url: url
                    };
                });

            return result;
        },
        async refreshUsers() {
            await this.$store.dispatch('users/loadAll');
        },
        projectFor(study) {
            return this.personalProjects.find(
                p =>
                    p.owner === study.project_owner &&
                    p.title === study.project_title
            );
        },
        async unbindProject() {
            this.unbindingProject = true;
            this.hideUnbindProjectModal();
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            var data = {
                path: path
            };
            if (this.projectToUnbind !== null)
                data['project'] = this.projectToUnbind;
            if (this.studyToUnbind !== null) data['study'] = this.studyToUnbind;
            await axios
                .post(`/apis/v1/datasets/unbind/`, data)
                .then(async response => {
                    if (
                        response.status === 200 &&
                        response.data.project !== undefined
                    ) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data.project
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unbound project ${this.projectToUnbind.title} study ${this.studyToUnbind.title} from path ${path}`,
                            guid: guid().toString()
                        });
                        this.projectToUnbind = null;
                        this.studyToUnbind = null;
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    this.unbindingProject = false;
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unbind project ${this.projectToUnbind.title} study ${this.studyToUnbind.title} from path ${path}`,
                        guid: guid().toString()
                    });
                    throw error;
                });
        },
        showUnbindProjectModal() {
            this.$bvModal.show(
                'unbindProject' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        hideUnbindProjectModal() {
            this.$bvModal.hide(
                'unbindProject' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        preUnbindProject(project, study) {
            this.projectToUnbind = project;
            this.studyToUnbind = study;
            this.showUnbindProjectModal();
        },
        async bindProject(path) {
            this.bindingProject = true;
            this.hideBindProjectModal();
            var data = {
                path: path
            };
            if (this.selectedProject !== null)
                data['project'] = this.selectedProject;
            if (this.selectedStudy !== null) data['study'] = this.selectedStudy;
            await axios
                .post(`/apis/v1/datasets/bind/`, data)
                .then(async response => {
                    if (
                        response.status === 200 &&
                        response.data.project !== undefined
                    ) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data.project
                        );
                        await this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Bound project ${this.selectedProject.title} study ${this.selectedStudy.title} to path ${path}`,
                            guid: guid().toString()
                        });
                    }
                })
                .catch(async error => {
                    Sentry.captureException(error);
                    this.bindingProject = false;
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to bind project ${this.selectedProject.title} study ${this.selectedStudy.title} to path ${path}`,
                        guid: guid().toString()
                    });
                    throw error;
                });
        },
        showBindProjectModal() {
            this.$bvModal.show(
                'bindProject' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        hideBindProjectModal() {
            this.$bvModal.hide(
                'bindProject' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        preBindProject() {
            this.showBindProjectModal();
        },
        // https://stackoverflow.com/a/23625419
        formatBytes(bytes) {
            var marker = 1024; // Change to 1000 if required
            var decimal = 3; // Change as required
            var kiloBytes = marker; // One Kilobyte is 1024 bytes
            var megaBytes = marker * marker; // One MB is 1024 KB
            var gigaBytes = marker * marker * marker; // One GB is 1024 MB

            // return bytes if less than a KB
            if (bytes < kiloBytes) return bytes + ' Bytes';
            // return KB if less than a MB
            else if (bytes < megaBytes)
                return (bytes / kiloBytes).toFixed(decimal) + ' KB';
            // return MB if less than a GB
            else if (bytes < gigaBytes)
                return (bytes / megaBytes).toFixed(decimal) + ' MB';
            // return GB if less than a TB
            else return (bytes / gigaBytes).toFixed(decimal) + ' GB';
        },
        showProjectSelection() {
            this.showingProjectSelection = true;
        },
        hideProjectSelection() {
            this.showingProjectSelection = false;
        },
        openDataset(agent) {
            this.$store.dispatch('datasets/open', {
                agent: agent,
                path: this.internalLoaded
                    ? this.internalNode.path
                    : this.node.path
            });
        },
        fileIsImage(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'png' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpg' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'jpeg'
            );
        },
        fileIsText(file) {
            return (
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'txt' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'csv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'tsv' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'yaml' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'log' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'out' ||
                file
                    .toLowerCase()
                    .split('.')
                    .pop() === 'err'
            );
        },
        viewFile(file) {
            this.selectedFile = file;
            this.selectedFileTitle = file.label;
            this.$bvModal.show('selectedFile' + this.internalNode.path);
        },
        onSelectedFileClosed() {
            this.selectedFile = null;
            this.selectedFileTitle = '';
        },
        showCreateDirectoryModal() {
            this.$bvModal.show(
                'createDirectoryModal' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        hideCreateDirectoryModal() {
            this.$bvModal.hide(
                'createDirectoryModal' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        async shareDataset() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            await axios({
                method: 'post',
                url: `/apis/v1/datasets/share/`,
                data: {
                    // sharing
                    sharing: this.sharedUsers.map(function(user) {
                        return {
                            user: user,
                            paths: [
                                {
                                    path: path,
                                    permission: 'read'
                                }
                            ]
                        };
                    })
                },
                headers: { 'Content-Type': 'application/json' }
            })
                .then(async response => {
                    await this.$store.dispatch(
                        'datasets/setSharing',
                        response.data.datasets
                    );
                    await this.$store.dispatch('alerts/add', {
                        variant: 'success',
                        message: `Shared directory ${
                            this.internalLoaded
                                ? this.internalNode.path
                                : this.node.path
                        } with ${this.sharedUsers.length} user(s)`,
                        guid: guid().toString()
                    });

                    this.$parent.$parent.$parent.$parent.$parent.$emit(
                        'loadSharedDirectory'
                    );
                    this.$parent.$parent.$parent.$parent.$emit(
                        'loadSharedDirectory'
                    );
                    this.$parent.$parent.$parent.$emit('loadSharedDirectory');
                    this.$parent.$parent.$emit('loadSharedDirectory');
                    this.$parent.$emit('loadSharedDirectory');
                    this.$emit('loadSharedDirectory');
                })
                .catch(error => {
                    Sentry.captureException(error);

                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to share directory ${
                            this.internalLoaded
                                ? this.internalNode.path
                                : this.node.path
                        } with ${this.sharedUsers.length} user(s)`,
                        guid: guid().toString()
                    });

                    throw error;
                });
        },
        showShareDirectoryModal() {
            this.$bvModal.show(
                'shareDirectoryModal' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        hideShareDirectoryModal() {
            this.$bvModal.hide(
                'shareDirectoryModal' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        toggle: function() {
            if (this.internalLoaded) this.isOpen = !this.isOpen;
            else this.loadDirectory();
        },
        waitForCreation(path) {
            this.waitFor(() => {
                this.refresh();
                let created =
                    this.internalNode.folders.filter(f => f.path === path)
                        .length !== 0;
                if (created) {
                    this.creatingDirectory = false;
                    this.$store.dispatch('alerts/add', {
                        variant: 'success',
                        message: `Created directory ${path}`,
                        guid: guid().toString()
                    });
                }
                return created;
            });
        },
        waitForDeletion(path) {
            this.waitFor(
                () => {
                    this.refresh();
                    let deleted =
                        this.internalNode.folders.filter(f => f.path === path)
                            .length === 0;
                    if (deleted) {
                        this.deletingDirectory = false;
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Deleted directory ${path}`,
                            guid: guid().toString()
                        });
                    }
                    return deleted;
                },
                () => this.internalNode.folders.map(f => f)
            );
        },
        waitFor(condition, callback) {
            if (!condition()) {
                window.setTimeout(
                    this.waitFor.bind(null, condition, callback),
                    5000
                ); /* this checks the flag every 100 milliseconds*/
            } else {
                callback();
            }
        },
        async refresh() {
            await this.loadDirectory(
                this.internalLoaded ? this.internalNode.path : this.node.path,
                this.profile.djangoProfile.cyverse_token
            );
        },
        async downloadFile(path, token) {
            this.downloading = true;
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/fileio/download?path=${path}`,
                    {
                        headers: {
                            Authorization: 'Bearer ' + token
                        },
                        responseType: 'blob'
                    }
                )
                .then(response => {
                    let url = window.URL.createObjectURL(
                        new Blob([response.data])
                    );
                    let link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', path);
                    link.click();
                    window.URL.revokeObjectURL(url);
                    this.downloading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to download ${path}`,
                        guid: guid().toString()
                    });
                    throw error;
                });
        },
        refreshAfterDeletion() {
            this.$parent.$emit('deleted', this.internalNode);
            this.$emit('deleted', this.internalNode);
        },
        async deletePath(path, token) {
            await this.$bvModal
                .msgBoxConfirm(`Are you sure you want to delete '${path}'?`, {
                    size: 'sm',
                    bodyBgVariant: this.profile.darkMode ? 'dark' : 'white',
                    footerBgVariant: this.profile.darkMode ? 'dark' : 'white',
                    footerBorderVariant: this.profile.darkMode
                        ? 'dark'
                        : 'white',
                    footerTextVariant: this.profile.darkMode ? 'white' : 'dark',
                    bodyTextVariant: this.profile.darkMode ? 'white' : 'dark',
                    bodyBorderVariant: this.profile.darkMode ? 'dark' : 'white',
                    okVariant: 'outline-danger',
                    cancelVariant: 'secondary',
                    okTitle: 'Yes',
                    cancelTitle: 'No',
                    centered: true
                })
                .then(async value => {
                    if (value) {
                        this.deleting = true;
                        await axios
                            .post(
                                `https://de.cyverse.org/terrain/secured/filesystem/delete`,
                                { paths: [path] },
                                {
                                    headers: {
                                        Authorization: 'Bearer ' + token
                                    }
                                }
                            )
                            .then(() =>
                                setTimeout(this.refreshAfterDeletion, 5000)
                            )
                            .catch(error => {
                                Sentry.captureException(error);
                                this.deleting = false;
                                this.$store.dispatch('alerts/add', {
                                    variant: 'success',
                                    message: `Failed to delete ${path}`,
                                    guid: guid().toString()
                                });
                                throw error;
                            });
                    }
                })
                .catch(err => {
                    throw err;
                });
        },
        until(conditionFunction) {
            const poll = resolve => {
                if (conditionFunction()) resolve();
                else setTimeout(() => poll(resolve), 5000);
            };

            return new Promise(poll);
        },
        // old version, invokes Terrain API directly
        // async createDirectory(path, token) {
        //     this.creatingDirectory = true;
        //     this.$bvModal.hide('createDirectoryModal');
        //     await axios
        //         .post(
        //             `https://de.cyverse.org/terrain/secured/filesystem/directory/create`,
        //             {
        //                 path: path
        //             },
        //             {
        //                 headers: {
        //                     Authorization: 'Bearer ' + token
        //                 }
        //             }
        //         )
        //         .then(async response => {
        //             if (
        //                 response.status === 200 &&
        //                 response.data.project !== undefined
        //             ) {
        //                 await this.$store.dispatch(
        //                     'projects/addOrUpdate',
        //                     response.data.project
        //                 );
        //             }
        //             setTimeout(() => this.waitForCreation(path), 3000);
        //         })
        //         .catch(error => {
        //             Sentry.captureException(error);
        //             this.creatingDirectory = false;
        //             alert(`Failed to create directory '${path}''`);
        //             throw error;
        //         });
        // },
        // new version proxies via PlantIT to link project/study info
        async createDirectory(path, token) {
            this.creatingDirectory = true;
            this.$bvModal.hide('createDirectoryModal');
            var data = {
                path: path
            };
            if (this.selectedProject !== null)
                data['project'] = this.selectedProject;
            if (this.selectedStudy !== null) data['study'] = this.selectedStudy;
            await axios
                .post(`/apis/v1/datasets/create/`, data, {
                    headers: {
                        Authorization: 'Bearer ' + token
                    }
                })
                .then(async response => {
                    if (
                        response.status === 200 &&
                        response.data.project !== undefined
                    ) {
                        await this.$store.dispatch(
                            'projects/addOrUpdate',
                            response.data.project
                        );
                    }
                    setTimeout(() => this.waitForCreation(path), 3000);
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.creatingDirectory = false;
                    this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to create directory ${path}`,
                        guid: guid().toString()
                    });
                    throw error;
                });
        },
        async uploadFiles(files, to_path, token) {
            this.uploading = true;
            for (let file of files) {
                let data = new FormData();
                data.append('file', file, file.name);
                await axios
                    .post(
                        `https://de.cyverse.org/terrain/secured/fileio/upload?dest=${to_path}`,
                        data,
                        {
                            headers: {
                                Authorization: 'Bearer ' + token,
                                'Content-Type': 'multipart/form-data'
                            }
                        }
                    )
                    .then(response => {
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `File '${response.data.file.label}' uploaded to '${response.data.file.path}'`,
                            guid: guid().toString()
                        });
                        this.uploading = false;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        this.uploading = false;
                        this.$store.dispatch('alerts/add', {
                            variant: 'danger',
                            message: `Failed to upload '${file.name}' to '${to_path}'`,
                            guid: guid().toString()
                        });
                        throw error;
                    });
            }
            await this.loadDirectory(
                to_path,
                this.profile.djangoProfile.cyverse_token
            );
            this.filesToUpload = [];
            this.uploading = false;
        },
        async loadDirectory(path, token) {
            this.internalLoading = true;
            await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(async response => {
                    this.internalNode = response.data;
                    this.internalLoading = false;
                    this.internalLoaded = true;
                    this.deleting = false;
                    if (!this.isOpen) this.isOpen = true;
                    await this.loadFileURLs();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.internalLoading = false;
                    this.deleting = false;
                    throw error;
                });
        },
        selectNode: function(node, kind) {
            node['kind'] = kind;

            // 15 layers should be deep enough for any conceivable use case, right?
            // ..right?
            if (this.$parent !== undefined) {
                this.$parent.$emit('selectNode', node);
                if (this.$parent.$parent !== undefined) {
                    this.$parent.$parent.$emit('selectNode', node);
                    if (this.$parent.$parent.$parent !== undefined) {
                        this.$parent.$parent.$parent.$emit('selectNode', node);
                        if (
                            this.$parent.$parent.$parent.$parent !== undefined
                        ) {
                            this.$parent.$parent.$parent.$parent.$emit(
                                'selectNode',
                                node
                            );
                            if (
                                this.$parent.$parent.$parent.$parent.$parent !==
                                undefined
                            ) {
                                this.$parent.$parent.$parent.$parent.$parent.$emit(
                                    'selectNode',
                                    node
                                );
                                if (
                                    this.$parent.$parent.$parent.$parent.$parent
                                        .$parent !== undefined
                                ) {
                                    this.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                        'selectNode',
                                        node
                                    );
                                    if (
                                        this.$parent.$parent.$parent.$parent
                                            .$parent.$parent.$parent !==
                                        undefined
                                    ) {
                                        this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                            'selectNode',
                                            node
                                        );
                                        if (
                                            this.$parent.$parent.$parent.$parent
                                                .$parent.$parent.$parent
                                                .$parent !== undefined
                                        ) {
                                            this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                'selectNode',
                                                node
                                            );
                                            if (
                                                this.$parent.$parent.$parent
                                                    .$parent.$parent.$parent
                                                    .$parent.$parent.$parent !==
                                                undefined
                                            ) {
                                                this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                    'selectNode',
                                                    node
                                                );
                                                if (
                                                    this.$parent.$parent.$parent
                                                        .$parent.$parent.$parent
                                                        .$parent.$parent.$parent
                                                        .$parent !== undefined
                                                ) {
                                                    this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                        'selectNode',
                                                        node
                                                    );
                                                    if (
                                                        this.$parent.$parent
                                                            .$parent.$parent
                                                            .$parent.$parent
                                                            .$parent.$parent
                                                            .$parent.$parent
                                                            .$parent !==
                                                        undefined
                                                    ) {
                                                        this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                            'selectNode',
                                                            node
                                                        );
                                                        if (
                                                            this.$parent.$parent
                                                                .$parent.$parent
                                                                .$parent.$parent
                                                                .$parent.$parent
                                                                .$parent.$parent
                                                                .$parent
                                                                .$parent !==
                                                            undefined
                                                        ) {
                                                            this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                                'selectNode',
                                                                node
                                                            );
                                                            if (
                                                                this.$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent
                                                                    .$parent !==
                                                                undefined
                                                            ) {
                                                                this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                                    'selectNode',
                                                                    node
                                                                );
                                                                if (
                                                                    this.$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent
                                                                        .$parent !==
                                                                    undefined
                                                                ) {
                                                                    this.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$parent.$emit(
                                                                        'selectNode',
                                                                        node
                                                                    );
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            this.$emit('selectNode', node);

            this.$parent.toggle();
        }
    }
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"
.custom-file-input:lang(en) ~ .custom-file-label::after
  content: 'Upload'
</style>
