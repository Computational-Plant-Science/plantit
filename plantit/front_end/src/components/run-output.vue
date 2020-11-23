<template>
    <div>
        <b-row
            ><b-col
                >Select a directory in the CyVerse Data Store to push output
                files to.</b-col
            ></b-row
        >
        <br />
        <datatree
            :select="true"
            @selectPath="selectPath"
            :node="data"
        ></datatree>
        <br />
        Selected:
        <b
            >{{ path ? path : 'None' }}
            <i v-if="path" class="fas fa-check text-success"></i>
            <i v-else class="fas fa-exclamation text-danger"></i>
        </b>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import datatree from '@/components/data-tree.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'run-output',
    components: {
        datatree
    },
    data() {
        return {
            data: null,
            path: null
        };
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
            'flowConfigs',
            'loggedIn'
        ]),
        flowKey: function() {
            return `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`;
        }
    },
    async mounted() {
        await this.loadDirectory(
            `/iplant/home/${this.currentUserDjangoProfile.username}/`,
            this.currentUserDjangoProfile.profile.cyverse_token
        );
        if (this.flowKey in this.flowConfigs) {
            let flowConfig = this.flowConfigs[this.flowKey];
            if (
                flowConfig.output !== undefined &&
                flowConfig.output.to !== undefined
            ) {
                this.path = flowConfig.output.to;
            }
        }
    },
    methods: {
        loadDirectory(path, token) {
            axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=${path}`,
                    { headers: { Authorization: 'Bearer ' + token } }
                )
                .then(response => {
                    this.data = response.data;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    throw error;
                });
        },
        selectPath(path) {
            this.path = path;
            this.$emit('outputSelected', path);
        }
    }
};
</script>

<style scoped></style>
