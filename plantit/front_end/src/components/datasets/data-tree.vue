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
                    {{ internalLoaded ? internalNode.label : node.label }}
                </b-button>
            </b-col>
            <b-col class="mt-1" md="auto">
                <small
                    :variant="
                        profile.darkMode ? 'outline-light' : 'outline-dark'
                    "
                >
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
                            title="Delete Subdirectory"
                            @click="showDeleteDirectoryModal"
                            :variant="
                                profile.darkMode
                                    ? 'outline-light'
                                    : 'outline-dark'
                            "
                            ><i
                                class="fas fa-trash text-danger fa-fw"
                            ></i
                        ></b-button>
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
                                <b-form-input
                                    size="sm"
                                    v-model="newDirectoryName"
                                    :placeholder="'Enter a directory name'"
                                ></b-form-input>
                            </b-form-group>
                        </b-modal>
                        <!--<b-modal
                            v-if="!isShared"
                            :title-class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            :title="`Delete directory ${(internalLoaded
                                        ? internalNode.label
                                        : node.label)}?`"
                            :id="
                                'deleteDirectoryModal' +
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
                            @close="hideDeleteDirectoryModal"
                            ok-variant="danger"
                            @ok="
                                deletePath(
                                    (internalLoaded
                                        ? internalNode.path
                                        : node.path) +
                                        '/' +
                                        newDirectoryName,
                                    profile.djangoProfile.cyverse_token
                                )
                            "
                        ><p :class="profile.darkMode ? 'text-light' : 'text-dark'">This directory and its contents will be permanently deleted.</p>
                        </b-modal>-->
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
                                ></b-row
                            >
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
                                                    >{{ user.username }}
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
            <b-row
                align-v="middle"
                class="mt-1 mb-1 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5);"
                v-for="(child, index) in internalLoaded
                    ? internalNode.files
                    : node.files"
                :key="index"
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-col>
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
                <b-col md="auto">
                    <!--<b-button
                        id="popover-reactive-1"
                        :disabled="
                            !fileIsImage(child.label) &&
                                !fileIsText(child.label)
                        "
                        :variant="profile.darkMode ? 'outline-light' : 'white'"
                        class="m-1"
                        size="sm"
                        v-b-tooltip.hover
                        :title="'View ' + child.label"
                        @click="viewFile(child)"
                    >
                        <i class="fas fa-eye fa-fw"></i>
                    </b-button-->
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
                ? internalNode.folders
                : node.folders"
            v-bind:key="index"
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
                title="Upload file(s)"
                @selectPath="selectNode(child, 'directory')"
                @deleted="
                    loadDirectory(
                        node.path,
                        this.profile.djangoProfile.cyverse_token
                    )
                "
                :key="index"
                :node="child"
            ></data-tree>
        </b-list-group-item>
        <b-modal
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
            :title="thumbnailTitle"
            id="thumbnail"
            class="overflow-hidden"
            @close="onThumbnailHidden"
        >
            <b-spinner
                v-if="loadingThumbnail"
                type="grow"
                label="Loading..."
                variant="secondary"
            ></b-spinner>
            <b-img
                v-if="fileIsImage(thumbnailName)"
                center
                :src="thumbnailUrl"
                style="width: 68rem"
                @load="thumbnailLoaded"
                v-show="thumbnailDoneLoading"
            >
            </b-img>
            <b-embed
                @load="thumbnailLoaded"
                v-else-if="fileIsText(thumbnailName)"
                type="iframe"
                :src="thumbnailUrl"
            ></b-embed>
        </b-modal>
    </b-list-group>
</template>
<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
import router from '@/router';
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
            // thumbnail view
            loadingThumbnail: true,
            thumbnailName: '',
            thumbnailUrl: '',
            thumbnailTitle: '',
            thumbnailDoneLoading: false
        };
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
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
        isRoot() {
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            let isRootPath = (path === `/iplant/home/${this.profile.djangoProfile.username}` || path === `/iplant/home/${this.profile.djangoProfile.username}/`);
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
    methods: {
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
            router.push({
                name: 'artifact',
                params: {
                    path: file.path
                }
            });
        },
        onThumbnailHidden() {
            this.thumbnailUrl = '';
            this.thumbnailTitle = '';
            this.thumbnailDoneLoading = false;
            this.loadingThumbnail = true;
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
        showDeleteDirectoryModal() {
            this.$bvModal.show(
                'deleteDirectoryModal' +
                    (this.internalLoaded
                        ? this.internalNode.label
                        : this.node.label)
            );
        },
        hideDeleteDirectoryModal() {
            this.$bvModal.hide(
                'deleteDirectoryModal' +
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
                .then(() => {
                    this.sharedAlertMessage = `Shared directory ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.showSharedAlert = true;

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
                    this.sharedAlertMessage = `Failed to share directory ${
                        this.internalLoaded
                            ? this.internalNode.path
                            : this.node.path
                    } with ${this.sharedUsers.length} user(s)`;
                    this.showSharedAlert = true;
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
        refresh: function() {
            this.loadDirectory(
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
                    alert(`Failed to download '${path}''`);
                    throw error;
                });
        },
        refreshAfterDeletion() {
            this.$parent.$emit('deleted');
            // this.deleting = false;
            // this.checkDirectoryCreation(path, response);
        },
        checkDeletion(path, response) {
            if (
                !this.internalNode.folders.some(folder => folder.path === path)
            ) {
                clearInterval(this.deletingIntervalId);
                this.deleting = false;
                alert(`Path '${response.data.paths}' deleted`);
            }
        },
        async deletePath(path, token) {
            await this.$bvModal
                .msgBoxConfirm(`Are you sure you want to delete '${path}'?`, {
                    title: `Delete ${path}?`,
                    size: 'sm',
                    okVariant: 'outline-danger',
                    cancelVariant: 'white',
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
                                alert(`Failed to delete '${path}'`);
                                throw error;
                            });
                    }
                })
                .catch(err => {
                    throw err;
                });
        },
        refreshAfterDirectoryCreation() {
            this.loadDirectory(
                this.internalNode.path,
                this.profile.djangoProfile.cyverse_token
            );
            this.creatingDirectory = false;
            // this.checkDirectoryCreation(path, response);
        },
        refreshAfterDirectoryDeletion() {
            this.loadDirectory(
                this.internalNode.path,
                this.profile.djangoProfile.cyverse_token
            );
            this.creatingDirectory = false;
            // this.checkDirectoryCreation(path, response);
        },
        checkDirectoryCreation(path, response) {
            if (
                this.internalNode.folders.some(
                    folder => folder.path === response.data.path
                )
            ) {
                clearInterval(this.creatingDirectoryIntervalId);
                this.creatingDirectory = false;
                alert(`Path '${response.data.path}' created`);
            }
        },
        async createDirectory(path, token) {
            this.creatingDirectory = true;
            this.$bvModal.hide('createDirectoryModal');
            await axios
                .post(
                    `https://de.cyverse.org/terrain/secured/filesystem/directory/create`,
                    {
                        path: path
                    },
                    {
                        headers: {
                            Authorization: 'Bearer ' + token
                        }
                    }
                )
                .then(() =>
                    setTimeout(this.refreshAfterDirectoryCreation, 5000)
                )
                .catch(error => {
                    Sentry.captureException(error);
                    this.creatingDirectory = false;
                    alert(`Failed to create directory '${path}''`);
                    throw error;
                });
        },
        async deleteDirectory(path, token) {
            this.deletingDirectory = true;
            this.$bvModal.hide('deleteDirectoryModal');
            await axios
                .post(
                    `https://de.cyverse.org/terrain/secured/filesystem/delete`,
                    {
                        paths: [path]
                    },
                    {
                        headers: {
                            Authorization: 'Bearer ' + token
                        }
                    }
                )
                .then(() =>
                    setTimeout(this.refreshAfterDirectoryDeletion, 5000)
                )
                .catch(error => {
                    Sentry.captureException(error);
                    this.deletingDirectory = false;
                    alert(`Failed to delete directory '${path}''`);
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
                        alert(
                            `File '${response.data.file.label}' uploaded to '${response.data.file.path}'`
                        );
                        this.uploading = false;
                    })
                    .catch(error => {
                        Sentry.captureException(error);
                        this.uploading = false;
                        alert(
                            `Failed to upload '${file.name}' to '${to_path}'`
                        );
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
        loadDirectory(path, token) {
            this.internalLoading = true;
            axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    this.internalNode = response.data;
                    this.internalLoading = false;
                    this.internalLoaded = true;
                    this.deleting = false;
                    if (!this.isOpen) this.isOpen = true;
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
