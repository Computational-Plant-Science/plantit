<template>
    <div>
        <b-card
            border-variant="white"
            footer-bg-variant="white"
            footer-border-variant="white"
            :sub-title="
                `Select a ${
                    kind.toLowerCase() === 'file' ? 'file' : 'directory'
                } in the CyVerse Data Store${kind.toLowerCase() === 'file' ? ' to use as input' : ' to pull input files from'}.`
            "
        >
          <br/>
            <datatree
                :select="kind"
                @selectPath="selectPath"
                :node="data"
            ></datatree>
            <template v-slot:footer
                >Selected:
                <b
                    >{{ path ? path : 'None' }}
                    <i v-if="path" class="fas fa-check text-success"></i>
                    <i v-else class="fas fa-exclamation text-warning"></i> </b
            ></template>
        </b-card>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import datatree from '@/components/data-tree.vue';
import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    name: 'run-input',
    components: {
        datatree
    },
    props: {
        kind: {
            required: true,
            type: String
        },
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
            'loggedIn'
        ]),
    },
    async mounted() {
        await this.loadDirectory(
            `/iplant/home/${this.currentUserDjangoProfile.username}/`,
            this.currentUserDjangoProfile.profile.cyverse_token
        );
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
            this.$emit('inputSelected', path);
        }
    }
};
</script>

<style scoped></style>
