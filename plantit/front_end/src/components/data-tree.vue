<template>
    <b-list-group flush class="m-0">
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
                    {{
                        internalLoaded ? internalNode.label : node.label
                    }}</b-button
                >
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
                >
            </b-col>
            <b-col md="auto">
                <b-input-group size="sm">
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
                        v-else-if="internalLoaded && internalLoading"
                        :variant="darkMode ? 'warning' : 'dark'"
                        type="grow"
                        label="Loading"
                    ></b-spinner>
                    <b-form-file
                        v-if="upload"
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
                        v-if="upload"
                        class="ml-1"
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
                        ><i class="fas fa-upload fa-fw"></i> Upload</b-button
                    >
                    <b-button
                        class="ml-1"
                        size="sm"
                        v-b-modal.createDirectoryModal
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        ><i class="fas fa-plus fa-fw"></i> Directory</b-button
                    >
                    <b-modal
                        id="createDirectoryModal"
                        title="Create Directory"
                        close
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
                        v-if="
                            internalLoaded &&
                                internalNode.path.split('/').length > 4
                        "
                        class="ml-1"
                        size="sm"
                        @click="
                            deletePath(
                                internalLoaded ? internalNode.path : node.path,
                                profile.djangoProfile.profile.cyverse_token
                            )
                        "
                        variant="outline-danger"
                        ><i class="fas fa-trash fa-fw"></i> Delete</b-button
                    >
                    <b-button
                        class="ml-1"
                        title="Expand Directory"
                        v-if="!isOpen"
                        size="sm"
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        @click="toggle"
                    >
                        <i class="fas fa-caret-up fa-fw"></i> </b-button
                    ><b-button
                        class="ml-1"
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
            <b-col v-if="node.path.split('/').length > 4" md="auto"
                ><b-button
                    class="ml-1"
                    size="sm"
                    @click="
                        deletePath(
                            internalLoaded ? internalNode.path : node.path,
                            profile.djangoProfile.profile.cyverse_token
                        )
                    "
                    variant="outline-danger"
                    ><i class="fas fa-trash fa-fw"></i> Delete</b-button
                ></b-col
            >
            <b-col :class="darkMode ? 'theme-dark' : 'theme-light'" md="auto">
                <b-button
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
                <b-col md="auto"
                    ><b-button
                        class="ml-1 mt-1 mb-1"
                        size="sm"
                        @click="
                            downloadFile(
                                child.path,
                                profile.djangoProfile.profile.cyverse_token
                            )
                        "
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        ><i class="fas fa-download fa-fw"></i>
                        Download</b-button
                    ></b-col
                >
                <b-col md="auto"
                    ><b-button
                        class="ml-1 mt-1 mb-1"
                        size="sm"
                        @click="
                            deletePath(
                                child.path,
                                profile.djangoProfile.profile.cyverse_token
                            )
                        "
                        variant="outline-danger"
                        ><i class="fas fa-trash fa-fw"></i> Delete</b-button
                    ></b-col
                >
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
            downloading: false
        };
    },
    computed: {
        ...mapGetters([
            'profile.djangoProfile',
            'profile.githubProfile',
            'profile.cyverseProfile',
            'loggedIn',
            'darkMode'
        ]),
        isDir: function() {
            return !('file-size' in this);
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
                    let url = window.URL.createObjectURL(new Blob([response.data]));
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
