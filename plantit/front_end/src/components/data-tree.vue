<template>
    <b-list-group flush :class="darkMode ? 'theme-dark' : 'theme-light'">
        <b-spinner
            v-if="internalLoading"
            type="grow"
            variant="success"
        ></b-spinner>
        <b-row
            v-if="isDir && internalLoaded"
            :class="darkMode ? 'theme-dark' : 'theme-light'"
        >
            <b-col
                :style="{
                    'font-weight': isDir ? '500' : '300'
                }"
                :class="darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-button
                    :variant="darkMode ? 'outline-light' : 'white'"
                    v-if="select"
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
                <b-button
                    v-else
                    disabled
                    :variant="darkMode ? 'outline-light' : 'white'"
                >
                    <i class="fas fa-folder fa-fw mr-2"></i
                    >{{ internalLoaded ? internalNode.label : node.label }}
                </b-button>
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
        <b-row
            v-if="isDir && !internalLoaded"
            :class="darkMode ? 'theme-dark' : 'theme-light'"
        >
            <b-col :class="darkMode ? 'theme-dark' : 'theme-light'">
                <b-button
                    :variant="darkMode ? 'outline-light' : 'white'"
                    v-if="select"
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
                <b-button
                    v-else
                    disabled
                    :variant="darkMode ? 'outline-light' : 'white'"
                >
                    <i class="fas fa-folder fa-fw mr-2"></i
                    >{{ internalLoaded ? internalNode.label : node.label }}
                </b-button>
            </b-col>
            <b-col md="auto">
                <b-button
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'outline-dark'"
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
            :class="darkMode ? 'theme-dark' : 'theme-light'"
            v-for="(child, index) in internalLoaded
                ? internalNode.folders
                : node.folders"
            v-bind:key="index"
            v-show="isOpen"
            :variant="darkMode ? 'outline-light' : 'white'"
        >
            <data-tree
                :select="true"
                @selectPath="selectNode(child, 'directory')"
                :key="index"
                :node="child"
            ></data-tree>
        </b-list-group-item>
        <b-list-group-item
            v-show="isOpen"
            v-if="isDir && internalLoaded"
            :variant="darkMode ? 'outline-light' : 'white'"
            :class="darkMode ? 'theme-dark' : 'theme-light'"
        >
            <b-row
                v-for="(child, index) in internalLoaded
                    ? internalNode.files
                    : node.files"
                :key="index"
                :class="darkMode ? 'theme-dark' : 'theme-light'"
            >
                <b-button
                    class="ml-2"
                    v-if="select"
                    size="sm"
                    :variant="darkMode ? 'outline-light' : 'outline-dark'"
                    @click="selectNode(child, 'file')"
                    ><i class="fas fa-file fa-fw"></i>
                    {{ child.label }}</b-button
                >
                <b-col v-else>
                    <i class="fas fa-file fa-fw"></i> {{ child.label }}
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
        select: {
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

<style scoped></style>
