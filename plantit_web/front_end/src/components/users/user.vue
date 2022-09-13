<template>
    <b-container class="p-3 vl" fluid style="background-color: transparent">
        <div v-if="profileLoading">
            <br />
            <b-row>
                <b-col class="text-center">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </b-col>
            </b-row>
        </div>
        <div v-else>
            <b-row
                ><b-col
                    ><h1 :class="profile.darkMode ? 'text-light' : 'text-dark'">
                        Welcome, {{ profile.cyverseProfile.first_name }}
                    </h1></b-col
                ></b-row
            >
            <b-row align-v="center" class="mt-3"
                ><b-col>
                    <b-row
                        ><b-col
                            ><h2
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                Your Profile
                            </h2></b-col
                        ></b-row
                    >

                    <b-row align-v="start" class="mb-2">
                        <b-col md="auto">
                            <div>
                                <b-row
                                    ><b-col
                                        v-if="profile.githubProfile"
                                        md="auto"
                                        class="ml-0 mr-0"
                                        align-self="end"
                                    >
                                        <b-img
                                            class="avatar"
                                            rounded="circle"
                                            style="max-height: 5rem; max-width: 5rem; position: relative; top: 20px; box-shadow: -2px 2px 2px #adb5bd;opacity:0.9"
                                            :src="
                                                profile.githubProfile
                                                    ? profile.githubProfile
                                                          .avatar_url
                                                    : ''
                                            "
                                            v-if="profile.githubProfile"
                                        ></b-img>
                                        <i
                                            v-else
                                            class="far fa-user fa-fw fa-3x"
                                        ></i>
                                    </b-col>
                                </b-row>
                                <br />
                            </div>
                        </b-col>
                        <b-col
                            style="color: white; right: 12px"
                            align-self="end"
                            class="ml-0 mr-0"
                        >
                            <b-row
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-secondary'
                                "
                            >
                                <b-col class="ml-0 mr-0" align-self="end">
                                    <b-img
                                        rounded
                                        style="max-height: 2rem;"
                                        class="ml-1 mr-1 mb-3"
                                        :src="
                                            require('@/assets/logos/cyverse_logo.png')
                                        "
                                    ></b-img>
                                    <b
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        v-if="profile.djangoProfile !== null"
                                    >
                                        {{ profile.djangoProfile.username }}
                                    </b>
                                    <br />
                                    <a
                                        v-if="profile.githubProfile"
                                        :class="
                                            profile.darkMode
                                                ? 'text-light'
                                                : 'text-dark'
                                        "
                                        :href="
                                            'https://github.com/' +
                                                profile.githubProfile.login
                                        "
                                    >
                                        <i
                                            class="fab fa-github fa-2x fa-fw"
                                        ></i>
                                        {{
                                            'https://github.com/' +
                                                profile.githubProfile.login
                                        }}
                                    </a>
                                </b-col>
                            </b-row>
                        </b-col>
                    </b-row>
                    <b-row>
                        <b-col md="auto">
                            <p>
                                <small>Name</small>
                                <br />
                                {{
                                    profile.cyverseProfile
                                        ? `${profile.cyverseProfile.first_name} ${profile.cyverseProfile.last_name} `
                                        : profile.githubProfile
                                        ? profile.githubProfile.login
                                        : ''
                                }}
                                <br />
                            </p>
                            <p>
                                <small>Email Address</small>
                                <br />
                                {{ profile.cyverseProfile.email }}
                                (CyVerse)
                                <br />
                                {{
                                    profile.githubProfile
                                        ? profile.githubProfile.email
                                        : ''
                                }}
                                (GitHub)
                            </p>
                            <p>
                                <small>Affiliation</small>
                                <br />
                                {{
                                    profile.cyverseProfile === undefined
                                        ? ''
                                        : profile.cyverseProfile.institution
                                }}
                            </p>
                            <p>
                                <small>Bio</small>
                                <br />
                                {{
                                    profile.githubProfile
                                        ? profile.githubProfile.bio
                                        : 'None'
                                }}
                            </p>
                            <p>
                                <small>Location</small>
                                <br />
                                {{
                                    profile.githubProfile
                                        ? profile.githubProfile.location
                                        : 'None'
                                }}
                            </p>
                        </b-col>
                    </b-row>
                </b-col>
            </b-row>
        </div>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'User',
    data: function() {
        return {
            isOpen: false,
            isLoading: false,
            statsScope: 'Hour',
            alertEnabled: false,
            alertMessage: '',
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading'])
    },
    methods: {
        prettify: function(date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        prettifyShort: function(date) {
            return `${moment(date).fromNow()}`;
        },
        prettifyDuration: function(dur) {
            return moment.duration(dur, 'seconds').humanize();
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY hh:mm');
        }
    }
};
</script>

<style lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.autocomplete-result.is-active
  .autocomplete-result:hover
    background-color: #4AAE9B
    color: white

.background-dark
  background-color: $dark !important
  color: $light

.background-success
  background-color: $success !important
  color: $dark !important
</style>
