<template>
    <div>
        <b :class="darkMode ? 'text-white' : 'text-dark'">
            Select a public
            {{ this.kind === 'files' ? 'directory' : this.kind }} from the Data Commons or your own
            {{ this.kind === 'files' ? 'directory' : this.kind }} from the Data Store.
        </b>
        <br />
        <b-tabs
            class="mt-2"
            vertical
            pills
            nav-class="bg-transparent"
            active-nav-item-class="bg-secondary text-dark"
            v-model="currentTab"
        >
            <b-tab
                :active="!this.path.startsWith('/iplant/home/shared')"
                title="Data Store"
                :title-link-class="darkMode ? 'text-white' : 'text-dark'"
                :class="
                    darkMode
                        ? 'theme-dark m-0 p-3'
                        : 'theme-light m-0 p-3'
                "
            >
                <b-row
                    ><b-col>
                        <b-spinner
                            v-if="userDataLoading"
                            type="grow"
                            variant="success"
                        ></b-spinner>
                        <datatree
                            v-else
                            :select="kind"
                            :upload="true"
                            :download="true"
                            @selectNode="selectNode"
                            :node="userData"
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
            </b-tab>
            <b-tab
                :active="
                    this.path === '' ||
                        this.path.startsWith('/iplant/home/shared')
                "
                title="Data Commons"
                :title-link-class="darkMode ? 'text-white' : 'text-dark'"
                :class="
                    darkMode
                        ? 'theme-dark m-0 p-3'
                        : 'theme-light m-0 p-3'
                "
            >
                <b-row
                    ><b-col>
                        <b-spinner
                            v-if="publicDataLoading"
                            type="grow"
                            variant="success"
                        ></b-spinner>
                        <datatree
                            v-else
                            :select="kind"
                            :upload="true"
                            :download="true"
                            @selectNode="selectNode"
                            :node="publicData"
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
            </b-tab>
        </b-tabs>
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
        defaultPath: {
            required: false,
            type: String
        }
    },
    data() {
        return {
            publicDataLoading: true,
            userDataLoading: true,
            publicData: null,
            userData: null,
            path: '',
            currentTab: 0
        };
    },
    computed: {
        ...mapGetters([
            'profile.djangoProfile',
            'profile.githubProfile',
            'profile.cyverseProfile',
            'flowConfigs',
            'loggedIn',
            'darkMode'
        ]),
        flowKey: function() {
            return `${this.$router.currentRoute.params.username}/${this.$router.currentRoute.params.name}`;
        }
    },
    async mounted() {
        await axios
            .get(
                `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/${this.profile.djangoProfile.username}/`,
                {
                    headers: {
                        Authorization:
                            'Bearer ' +
                            this.profile.djangoProfile.profile.cyverse_token
                    }
                }
            )
            .then(response => {
                this.userData = response.data;
            })
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
        this.userDataLoading = false;
        await axios
            .get(
                `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=100&path=/iplant/home/shared/`,
                {
                    headers: {
                        Authorization:
                            'Bearer ' +
                            this.profile.djangoProfile.profile.cyverse_token
                    }
                }
            )
            .then(response => {
                this.publicData = response.data;
            })
            .catch(error => {
                Sentry.captureException(error);
                throw error;
            });
        if (this.flowKey in this.flowConfigs) {
            let flowConfig = this.flowConfigs[this.flowKey];
            if (
                flowConfig.input !== undefined &&
                flowConfig.input.from !== undefined
            ) {
                this.path = flowConfig.input.from;
            }
        }
        if (this.defaultPath !== undefined && this.defaultPath !== null) {
            this.path = this.defaultPath;
        }
        this.publicDataLoading = false;
    },
    methods: {
        selectNode(node) {
            this.path = node.path;
            this.$emit('inputSelected', node);
            this.$parent.$emit('inputSelected', node);
            this.$parent.$parent.$emit('inputSelected', node);
        },
        tabLinkClass(idx) {
            if (this.currentTab === idx) {
                // return this.darkMode
                //     ? 'background-dark text-success'
                //     : 'bg-light text-dark';
                return this.darkMode ? '' : 'text-dark';
            } else {
                return this.darkMode
                    ? 'background-dark text-light'
                    : 'text-dark';
            }
        }
    }
};
</script>

<style scoped></style>
