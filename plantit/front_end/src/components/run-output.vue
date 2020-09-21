<template>
    <div>
        <b-card
            border-variant="white"
            footer-bg-variant="white"
            sub-title="Select an output file or directory."
        >
            <br />
            <datatree
                select="Directory"
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
    name: 'run-output',
    components: {
        datatree
    },
    props: {
        kind: {
            required: true,
            type: String
        }
    },
    data() {
        return {
            data: null,
            path: null
        };
    },
    computed: mapGetters([
        'currentUserDjangoProfile',
        'currentUserGitHubProfile',
        'currentUserCyVerseProfile',
        'loggedIn'
    ]),
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
            this.$emit('outputSelected', path);
        }
    }
};
</script>

<style scoped></style>
