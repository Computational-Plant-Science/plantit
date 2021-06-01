<template>
    <div>
        <b :class="profile.darkMode ? 'text-white' : 'text-dark'">
            Select a directory in the CyVerse Data Store to upload output files
            to.
        </b>
        <b-row class="mt-2"
            ><b-col>
                <b-spinner
                    v-if="dataLoading"
                    type="grow"
                    variant="success"
                ></b-spinner>
                <datatree
                    v-else
                    select="directory"
                    :upload="false"
                    :download="false"
                    @selectNode="selectNode"
                    :node="data"
                ></datatree></b-col
        ></b-row>
        <b-alert
            class="mt-1"
            :variant="path ? 'success' : 'danger'"
            :show="true"
            >Selected: {{ path ? path : 'None' }}
            <i v-if="path" class="fas fa-check text-success"></i>
            <i v-else class="fas fa-exclamation text-danger"></i>
        </b-alert>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import datatree from '@/components/datasets/data-tree.vue';
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
        ...mapGetters('user', ['profile']),
        ...mapGetters('workflows', ['recentlyRunWorkflows']),
        flowKey: function() {
            return `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`;
        }
    },
    async mounted() {
        await this.loadDirectory(
            `/iplant/home/${this.profile.djangoProfile.username}/`,
            this.profile.djangoProfile.profile.cyverse_token
        );
        if (this.flowKey in this.recentlyRunWorkflows) {
            let flowConfig = this.recentlyRunWorkflows[this.flowKey];
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
