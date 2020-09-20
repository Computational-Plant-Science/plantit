<template>
    <b-list-group flush>
        <b-row v-if="isDir && internalLoaded">
            <b-col
                :style="{
                    'font-weight': isDir ? '500' : '300'
                }"
            >
                <i class="fas fa-folder fa-fw"></i>
                {{ internalLoaded ? internalNode.label : node.label }}
            </b-col>
            <b-col md="auto" class="mt-1">
                {{
                    isDir
                        ? `${subDirCount} ${
                              subDirCount === 1
                                  ? 'subdirectory'
                                  : 'subdirectories'
                          }, ${fileCount} ${fileCount === 1 ? 'file' : 'files'}`
                        : ''
                }}
            </b-col>
            <b-col class="ml-0 mr-0" md="auto">
                <b-button
                    v-if="internalLoaded && !internalLoading"
                    class="ml-0 mr-0"
                    title="Refresh Directory"
                    size="sm"
                    variant="outline-dark"
                    @click="refresh"
                >
                    <i class="fas fa-sync-alt fa-fw"></i>
                </b-button>
                <b-spinner
                    small
                    v-else-if="internalLoaded && internalLoading"
                    variant="dark"
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
                    variant="outline-dark"
                    @click="toggle"
                >
                    <i class="fas fa-caret-up fa-fw"></i> </b-button
                ><b-button
                    class="ml-0 mr-0"
                    title="Collapse Directory"
                    v-else
                    size="sm"
                    variant="outline-dark"
                    @click="toggle"
                >
                    <i class="fas fa-caret-down fa-fw"></i>
                </b-button>
            </b-col>
            <b-col class="ml-0 mr-0" md="auto">
                <b-button
                    class="ml-0 mr-0"
                    title="Select"
                    size="sm"
                    variant="outline-white"
                    @click="
                        selectPath(
                            internalLoaded ? internalNode.path : node.path
                        )
                    "
                >
                    Select
                </b-button>
            </b-col>
        </b-row>
        <b-row v-if="isDir && !internalLoaded">
            <b-col>
                <i class="fas fa-folder fa-fw"></i>
                {{ internalLoaded ? internalNode.label : node.label }}
            </b-col>
            <b-col md="auto">
                <b-button
                    size="sm"
                    variant="outline-dark"
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
                        variant="dark"
                        type="grow"
                        label="Loading"
                    ></b-spinner
                ></b-button>
            </b-col>
            <b-col class="ml-0 mr-0" md="auto">
                <b-button
                    class="ml-0 mr-0"
                    title="Select"
                    size="sm"
                    variant="outline-white"
                    @click="
                        selectPath(
                            internalLoaded ? internalNode.path : node.path
                        )
                    "
                >
                    Select
                </b-button>
            </b-col>
        </b-row>
        <b-list-group-item
            v-for="(child, index) in internalLoaded
                ? internalNode.folders
                : node.folders"
            v-bind:key="index"
            v-show="isOpen"
            variant="white"
        >
            <data-tree :key="index" :node="child"></data-tree>
        </b-list-group-item>
        <b-list-group-item
            v-show="isOpen"
            v-if="isDir && internalLoaded"
            variant="light"
        >
            <b-row
                v-for="(child, index) in internalLoaded
                    ? internalNode.files
                    : node.files"
                :key="index"
            >
                <b-col>
                    <i class="fas fa-file fa-fw"></i> {{ child.label }}
                </b-col>
                <b-col class="ml-0 mr-0" md="auto">
                    <b-button
                        class="ml-0 mr-0"
                        title="Select"
                        size="sm"
                        variant="outline-white"
                        @click="selectPath(child.path)"
                    >
                        Select
                    </b-button>
                </b-col>
            </b-row>
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
        selectable: {
            required: false,
            type: Boolean
        }
    },
    data: function() {
        return {
            internalNode: null,
            internalLoading: false,
            internalLoaded: false,
            isOpen: false
        };
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
            'loggedIn'
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
        selectPath: function(path) {
            this.$parent.$emit('selectPath', path);
            this.$emit('selectPath', path);
        }
    }
};
</script>

<style scoped></style>
