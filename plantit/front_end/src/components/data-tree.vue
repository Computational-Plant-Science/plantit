<template>
    <b-list-group flush>
        <div v-if="isDir && internalLoad" :class="{ bold: isDir }" @click="toggle">
            {{ internalLoad ? internalNode.label : node.label }}
            <span>[{{ isOpen ? '-' : '+' }}]</span>
        </div>
        <div
            v-if="isDir && !internalLoad"
            @click="
                loadDirectory(
                    internalLoad ? internalNode.path : node.path,
                    currentUserDjangoProfile.profile.cyverse_token
                )
            "
        >
            {{ internalLoad ? internalNode.label : node.label }}
            <span>[load]</span>
        </div>
        <span v-else-if="isDir && !internalLoad">[load]</span>
        <b-list-group-item
            v-for="(child, index) in internalLoad
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
            v-if="isDir && internalLoad"
            variant="light"
        >
            <div
                v-for="(child, index) in internalLoad
                    ? internalNode.files
                    : node.files"
                :key="index"
            >
                {{ child.label }}
            </div>
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
        node: Object
    },
    data: function() {
        return {
            internalNode: null,
            internalLoad: false,
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
    },
    methods: {
        toggle: function() {
            if (this.internalLoad) this.isOpen = !this.isOpen;
            else this.loadDirectory();
        },
        loadDirectory(path, token) {
            axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    this.internalNode = response.data;
                    this.internalLoad = true;
                    this.toggle();
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        }
        // createDir: function() {
        //     if (!this.isDir) {
        //         this.$emit('addDirectory', this.node.path);
        //         this.isOpen = true;
        //     }
        // }
    }
};
</script>

<style scoped></style>
