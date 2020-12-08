<template>
    <div>
        <b-tabs
            active-nav-item-class="background-success text-dark"
            :active-tab-class="
                darkMode
                    ? 'background-dark text-white'
                    : 'background-white text-dark'
            "
            pills
            v-model="currentTab"
        >
            <b-tab
                :active="this.path.startsWith('/iplant/home/shared')"
                title="Community Data"
                :title-link-class="tabLinkClass(0)"
            >
                <br />
                <b-row
                    ><b-col
                        >Select a public file or dataset from the CyVerse Data
                        Commons.</b-col
                    ></b-row
                >
                <br />
                <datatree
                    :select="true"
                    @selectNode="selectNode"
                    :node="publicData"
                ></datatree>
                <br />
                Selected:
                <b
                    >{{ path ? path : 'None' }}
                    <i v-if="path" class="fas fa-check text-success"></i>
                    <i v-else class="fas fa-exclamation text-danger"></i>
                </b>
            </b-tab>
            <b-tab
                :active="!this.path.startsWith('/iplant/home/shared')"
                title="Your Data"
                :title-link-class="tabLinkClass(1)"
            >
                <br />
                <b-row
                    ><b-col
                        >Select your own file or dataset from the CyVerse Data
                        Store.</b-col
                    ></b-row
                >
                <br />
                <datatree
                    :select="true"
                    @selectNode="selectNode"
                    :node="userData"
                ></datatree>
                <br />
                Selected:
                <b
                    >{{ path ? path : 'None' }}
                    <i v-if="path" class="fas fa-check text-success"></i>
                    <i v-else class="fas fa-exclamation text-danger"></i>
                </b>
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
            publicData: null,
            userData: null,
            path: '',
            currentTab: 0
        };
    },
    computed: {
        ...mapGetters([
            'currentUserDjangoProfile',
            'currentUserGitHubProfile',
            'currentUserCyVerseProfile',
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
                `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/${this.currentUserDjangoProfile.username}/`,
                {
                    headers: {
                        Authorization:
                            'Bearer ' +
                            this.currentUserDjangoProfile.profile.cyverse_token
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
        await axios
                .get(
                    `https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path=/iplant/home/shared/`,
                    {
                        headers: {
                            Authorization:
                                'Bearer ' +
                                this.currentUserDjangoProfile.profile
                                    .cyverse_token
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
