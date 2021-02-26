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
            v-if="isDir && internalLoaded"
            class="mt-1 mb-1 ml-2 mr-0 p-0 text-left"
        >
            <b-col
                :style="{
                    'font-weight': isDir ? '500' : '300'
                }"
                :class="darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-button
                    :title="(internalLoaded ? internalNode : node).path"
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'white'"
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
                <small :variant="darkMode ? 'outline-light' : 'outline-dark'">
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
                    <b-form-file
                        v-if="upload && !isShared"
                        style="min-width: 15rem"
                        :class="darkMode ? 'theme-dark' : 'theme-light'"
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
                                profile.djangoProfile.profile.cyverse_token
                            )
                        "
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        ><i class="fas fa-upload fa-fw"></i
                    ></b-button>
                    <b-button
                        v-if="!isShared"
                        class="ml-1 mr-1"
                        size="sm"
                        title="Create Subdirectory"
                        @click="showCreateDirectoryModal"
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        ><i class="fas fa-plus fa-fw"></i
                    ></b-button>
                    <b-modal
                        v-if="!isShared"
                        :title-class="darkMode ? 'text-white' : 'text-dark'"
                        title="Create Directory"
                        :id="
                            'createDirectoryModal' +
                                (internalLoaded
                                    ? internalNode.label
                                    : node.label)
                        "
                        centered
                        :header-text-variant="darkMode ? 'white' : 'dark'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :footer-bg-variant="darkMode ? 'dark' : 'white'"
                        :body-bg-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :footer-border-variant="darkMode ? 'dark' : 'white'"
                        close
                        @close="hideCreateDirectoryModal"
                        @ok="
                            createDirectory(
                                (internalLoaded
                                    ? internalNode.path
                                    : node.path) +
                                    '/' +
                                    newDirectoryName,
                                profile.djangoProfile.profile.cyverse_token
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
                    <b-button
                        v-if="internalLoaded && !internalLoading"
                        class="ml-1 mr-1"
                        title="Refresh Directory"
                        size="sm"
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        @click="refresh"
                    >
                        <i class="fas fa-sync-alt fa-fw"></i>
                    </b-button>
                    <b-spinner
                        v-if="internalLoaded && internalLoading"
                        :variant="darkMode ? 'warning' : 'dark'"
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
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        @click="showShareDirectoryModal"
                        class="ml-1 mr-1"
                        ><i class="fas fa-share-alt fa-fw"></i
                    ></b-button>
                    <b-modal
                        v-if="!isShared"
                        :title-class="darkMode ? 'text-white' : 'text-dark'"
                        :title="
                            'Share ' +
                                (internalLoaded ? internalNode.path : node.path)
                        "
                        centered
                        :header-text-variant="darkMode ? 'white' : 'dark'"
                        :header-bg-variant="darkMode ? 'dark' : 'white'"
                        :footer-bg-variant="darkMode ? 'dark' : 'white'"
                        :body-bg-variant="darkMode ? 'dark' : 'white'"
                        :header-border-variant="darkMode ? 'dark' : 'white'"
                        :footer-border-variant="darkMode ? 'dark' : 'white'"
                        @ok="shareDirectory"
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
                                        darkMode ? 'text-white' : 'text-dark'
                                    "
                                    ><small
                                        >Choose who to share this directory
                                        with.</small
                                    ></b-col
                                ></b-row
                            >
                            <b-row align-v="center" align-h="center">
                                <b-col>
                                    <b-form>
                                        <b-form-group
                                            v-slot="{ ariaDescribedby }"
                                        >
                                            <b-form-checkbox-group
                                                v-model="sharedUsers"
                                                :options="sharingUsers"
                                                :aria-describedby="
                                                    ariaDescribedby
                                                "
                                                stacked
                                                buttons
                                                size="lg"
                                            >
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
                                                darkMode ? 'dark' : 'white'
                                            "
                                            :header-bg-variant="
                                                darkMode ? 'dark' : 'white'
                                            "
                                            border-variant="default"
                                            :header-border-variant="
                                                darkMode
                                                    ? 'secondary'
                                                    : 'default'
                                            "
                                            :text-variant="
                                                darkMode ? 'white' : 'dark'
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
                                                            darkMode
                                                                ? 'text-white'
                                                                : 'text-dark'
                                                        "
                                                    >
                                                        {{ user.first_name }}
                                                        {{ user.last_name }}
                                                        <small
                                                            :class="
                                                                darkMode
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
                                                        darkMode
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
                                                            darkMode
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
                        </b-container></b-modal
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
                                profile.djangoProfile.profile.cyverse_token
                            )
                        "
                        variant="outline-danger"
                        ><i class="fas fa-trash fa-fw"></i
                    ></b-button>
                    <b-button
                        class="ml-1 mr-1"
                        title="Expand Directory"
                        v-if="!isOpen"
                        size="sm"
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        @click="toggle"
                    >
                        <i class="fas fa-caret-up fa-fw"></i> </b-button
                    ><b-button
                        class="ml-1 mr-1"
                        title="Collapse Directory"
                        v-else
                        size="sm"
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
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
            <b-col :class="darkMode ? 'theme-dark' : 'theme-light'">
                <b-button
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'white'"
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
            <b-col :class="darkMode ? 'theme-dark' : 'theme-light'" md="auto">
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
                            profile.djangoProfile.profile.cyverse_token
                        )
                    "
                    variant="outline-danger"
                    ><i class="fas fa-trash fa-fw"></i
                ></b-button>
                <b-button
                    title="Expand Directory"
                    class="ml-1 mr-1"
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'white'"
                    @click="
                        loadDirectory(
                            internalLoaded ? internalNode.path : node.path,
                            profile.djangoProfile.profile.cyverse_token
                        )
                    "
                    ><i
                        v-if="!internalLoaded && !internalLoading"
                        class="fas fa-caret-up fa-fw"
                    ></i>
                    <b-spinner
                        small
                        v-else-if="!internalLoaded && internalLoading"
                        :variant="darkMode ? 'warning' : 'dark'"
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
            :variant="darkMode ? 'outline-light' : 'outline-dark'"
        >
            <b-row
                align-v="middle"
                class="mt-1 mb-1 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5);"
                v-for="(child, index) in internalLoaded
                    ? internalNode.files
                    : node.files"
                :key="index"
                :class="darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-col>
                    <b-button
                        class="mt-1 mb-1 ml-4"
                        :disabled="!select || select !== 'file'"
                        size="sm"
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        @click="selectNode(child, 'file')"
                        ><i class="fas fa-file fa-fw"></i>
                        {{ child.label }}</b-button
                    >
                </b-col>
                <b-col md="auto">
                    <b-button
                        v-if="!isShared"
                        class="m-1"
                        size="sm"
                        title="Delete File"
                        @click="
                            deletePath(
                                child.path,
                                profile.djangoProfile.profile.cyverse_token
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
                                profile.djangoProfile.profile.cyverse_token
                            )
                        "
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
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
            :variant="darkMode ? 'outline-light' : 'outline'"
        >
            <data-tree
                class="pt-1 pb-1 mb-0 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5); border-left: 2px solid rgba(211, 211, 211, .5)"
                :select="select"
                :upload="upload"
                :download="download"
                title="Upload file(s)"
                @selectPath="selectNode(child, 'directory')"
                @deleted="
                    loadDirectory(
                        node.path,
                        this.profile.djangoProfile.profile.cyverse_token
                    )
                "
                :key="index"
                :node="child"
            ></data-tree>
        </b-list-group-item>
    </b-list-group>
</template>
<script>
import { mapGetters } from 'vuex';
import axios from 'axios';
import * as Sentry from '@sentry/browser';
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
        upload: {
            required: false,
            type: Boolean
        },
        download: {
            required: false,
            type: Boolean
        }
    },
    data: function() {
        return {
            users: [],
            internalNode: null,
            internalLoading: false,
            internalLoaded: false,
            isOpen: false,
            filesToUpload: [],
            filesToDownload: [],
            uploading: false,
            deleting: false,
            creatingDirectory: false,
            newDirectoryName: '',
            uploadingIntervalId: '',
            creatingDirectoryIntervalId: '',
            deletingIntervalId: '',
            downloading: false,
            sharedUsers: [],
            sharedAlertMessage: '',
            showSharedAlert: false
        };
    },
    computed: {
        ...mapGetters(['profile', 'loggedIn', 'darkMode']),
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
        sharingUsers() {
            let username = this.profile.djangoProfile.username;
            return this.users
                .map(function(user) {
                    return {
                        value: user.username,
                        text: user.username
                        // avatar: user.github_profile.avatar_url
                    };
                })
                .filter(function(item) {
                    return item.value !== username;
                });
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
        async shareDirectory() {
            /** Terrain spec
             *{
             *  "sharing": [
             *    {
             *      "user": "string",
             *      "paths: [
             *        {
             *          "path": "string",
             *          "permission": "read",
             *        }
             *      ]
             *    }
             *  ]
             *}
             */
            let path = this.internalLoaded
                ? this.internalNode.path
                : this.node.path;
            await axios({
                method: 'post',
                url: `/apis/v1/stores/share_directory/`,
                data: {
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
            this.loadUsers();
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
        loadUsers() {
            axios
                .get('/apis/v1/users/get_all/')
                .then(response => {
                    this.users = response.data.users;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    if (error.response.status === 500) throw error;
                });
        },
        toggle: function() {
            if (this.internalLoaded) this.isOpen = !this.isOpen;
            else this.loadDirectory();
        },
        refresh: function() {
            this.loadDirectory(
                this.internalLoaded ? this.internalNode.path : this.node.path,
                this.profile.djangoProfile.profile.cyverse_token
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
                    title: 'Confirm Deletion',
                    size: 'sm',
                    okVariant: 'outline-danger',
                    cancelVariant: 'outline-dark',
                    okTitle: 'Yes',
                    cancelTitle: 'Cancel',
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
                this.profile.djangoProfile.profile.cyverse_token
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
                this.profile.djangoProfile.profile.cyverse_token
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
            this.$parent.$parent.$parent.$parent.$parent.$emit(
                'selectNode',
                node
            );
            this.$parent.$parent.$parent.$parent.$emit('selectNode', node);
            this.$parent.$parent.$parent.$emit('selectNode', node);
            this.$parent.$parent.$emit('selectNode', node);
            this.$parent.$emit('selectNode', node);
            this.$emit('selectNode', node);
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"
.custom-file-input:lang(en) ~ .custom-file-label::after
  content: 'Upload'
</style>
