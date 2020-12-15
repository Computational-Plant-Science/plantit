<template>
    <div>
        <br />
        <b-row align-v="center" align-h="center"
            ><b-col
                ><h5>
                    Select a directory in the CyVerse Data Store to push output
                    files to.
                </h5>
                <br />
                <b-spinner
                    v-if="dataLoading"
                    type="grow"
                    variant="success"
                ></b-spinner>
                <datatree
                    v-else
                    :select="true"
                    @selectNode="selectNode"
                    :node="data"
                ></datatree></b-col
        ></b-row>
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
            dataLoading: true,
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
                    this.dataLoading = false;
                })
                .catch(error => {
                    Sentry.captureException(error);
                    this.dataLoading = false;
                    throw error;
                });
        },
        selectNode(node) {
            this.path = node.path;
            this.$emit('outputSelected', node);
        }
    }
};
</script>

<style scoped></style>
