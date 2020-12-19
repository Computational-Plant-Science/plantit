<template>
    <b-list-group flush class="mt-0 mb-0">
        <!--<b-spinner
            v-if="internalLoading"
            type="grow"
            variant="success"
        ></b-spinner>-->
        <b-row v-if="isDir && internalLoaded" class="mt-1 mb-1 ml-2 mr-0 p-0">
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
                <!--<b-button
                    size="sm"
                    v-else
                    :variant="darkMode ? 'outline-light' : 'white'"
                >
                    <i class="fas fa-folder fa-fw mr-2"></i
                    >{{ internalLoaded ? internalNode.label : node.label }}
                </b-button>-->
            </b-col>
            <b-col md="auto" class="mt-1">
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
            <b-col md="auto" v-if="upload">
                <b-input-group size="sm">
                    <b-form-file
                        style="min-width: 20rem"
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
                        class="ml-1"
                        size="sm"
                        @click="
                            uploadFile(
                                filesToUpload,
                                internalLoaded ? internalNode.path : node.path,
                                currentUserDjangoProfile.profile.cyverse_token
                            )
                        "
                        :variant="darkMode ? 'outline-light' : 'outline-dark'"
                        ><i class="fas fa-plus fa-fw"></i> Upload</b-button
                    ></b-input-group
                ></b-col
            >
            <b-col class="ml-0 mr-0" md="auto">
                <b-button
                    v-if="internalLoaded && !internalLoading"
                    class="ml-0 mr-0"
                    title="Refresh Directory"
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'outline-dark'"
                    @click="refresh"
                >
                    <i class="fas fa-sync-alt fa-fw"></i>
                </b-button>
                <b-spinner
                    small
                    v-else-if="internalLoaded && internalLoading"
                    :variant="darkMode ? 'warning' : 'dark'"
                    type="grow"
                    label="Loading"
                ></b-spinner>
            </b-col>
            <b-col class="ml-0 mr-0" md="auto">
                <b-button
                    class="ml-0 mr-0"
                    title="Expand Directory"
                    v-if="!isOpen"
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'outline-dark'"
                    @click="toggle"
                >
                    <i class="fas fa-caret-up fa-fw"></i> </b-button
                ><b-button
                    class="ml-0 mr-0"
                    title="Collapse Directory"
                    v-else
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'outline-dark'"
                    @click="toggle"
                >
                    <i class="fas fa-caret-down fa-fw"></i>
                </b-button>
            </b-col>
        </b-row>
        <b-row align-h="center" align-v="center" class="text-center">
            <b-col>
                <b-spinner v-if="uploading" variant="success" small></b-spinner>
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
                <!--<b-button
                    size="sm"
                    v-else
                    :disabled="select !== 'directory' && select !== 'files'"
                    :variant="darkMode ? 'outline-light' : 'white'"
                >
                    <i class="fas fa-folder fa-fw mr-2"></i
                    >{{ internalLoaded ? internalNode.label : node.label }}
                </b-button>-->
            </b-col>
            <b-col :class="darkMode ? 'theme-dark' : 'theme-light'" md="auto">
                <b-button
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'white'"
                    @click="
                        loadDirectory(
                            internalLoaded ? internalNode.path : node.path,
                            currentUserDjangoProfile.profile.cyverse_token
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
            class="mt-1 mb-1 ml-2 mr-0 p-0"
            style="background-color: transparent;"
            v-show="isOpen"
            v-if="isDir && internalLoaded"
            :variant="darkMode ? 'outline-light' : 'outline-dark'"
        >
            <b-row
                class="mt-1 mb-1 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5);"
                v-for="(child, index) in internalLoaded
                    ? internalNode.files
                    : node.files"
                :key="index"
                :class="darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-button
                    class="ml-4"
                    :disabled="!select || select !== 'file'"
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'outline-dark'"
                    @click="selectNode(child, 'file')"
                    ><i class="fas fa-file fa-fw"></i>
                    {{ child.label }}</b-button
                >
            </b-row>
        </b-list-group-item>
        <b-list-group-item
            class="mt-1 mb-1 ml-2 mr-0 p-0"
            style="background-color: transparent;"
            v-for="(child, index) in internalLoaded
                ? internalNode.folders
                : node.folders"
            v-bind:key="index"
            v-show="isOpen"
            :variant="darkMode ? 'outline-light' : 'outline'"
        >
            <data-tree
                class="mt-0 mb-0 ml-2 mr-0 p-0"
                style="border-top: 1px solid rgba(211, 211, 211, .5); border-left: 2px solid rgba(211, 211, 211, .5)"
                :select="select"
                :upload="upload"
                @selectPath="selectNode(child, 'directory')"
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
            uploading: false
        };
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
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
                this.currentUserDjangoProfile.profile.cyverse_token
            );
        },
        async uploadFile(files, to_path, token) {
            // with open(from_path, 'rb') as file:
            // with requests.post(f"https://de.cyverse.org/terrain/secured/fileio/upload?dest={to_path}",
            //                    headers={'Authorization': f"Bearer {self.plan.cyverse_token}"},
            //                    files={'file': (basename(from_path), file, 'application/octet-stream')}) as response:
            //     response.raise_for_status()

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
            this.uploading = false;
            await this.loadDirectory(
                to_path,
                this.currentUserDjangoProfile.profile.cyverse_token
            );
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
                    if (!this.isOpen) this.isOpen = true;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.internalLoading = false;
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
