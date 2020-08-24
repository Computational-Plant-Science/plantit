<template>
    <div class="w-100 p-5 m-0">
        <br />
        <br />
        <b-container>
            <div class="w-100 pb-4">
                <b-card
                    bg-variant="white"
                    border-variant="white"
                    header-border-variant="white"
                    header-bg-variant="white"
                    :img-src="githubUser ? githubUser.avatar_url : ''"
                    img-alt="Image"
                    img-top
                    style="max-width: 30rem;margin: 0 auto;"
                >
                    <template
                        v-slot:header
                        style="background-color: white"
                        v-bind:info="user"
                    >
                        <b-row align-v="center">
                            <b-col
                                align-self="center"
                                class="mt-2"
                                style="color:white"
                            >
                                <h2>
                                    <b>{{ user.username }}</b>
                                </h2>
                            </b-col>
                            <b-col md="auto">
                                <b-button
                                    @click="
                                        $bvModal.show('editUserInfoModalNav')
                                    "
                                    variant="outline-dark"
                                    v-b-tooltip.hover
                                    title="Edit profile."
                                >
                                    <i class="far fa-edit fa-2x"></i>
                                </b-button>
                            </b-col>
                        </b-row>
                    </template>
                    <b-card-text>
                        <h4>Profile</h4>
                        <br />
                        <p><b>Email Address:</b> {{ user.email }}</p>
                        <p><b>First Name:</b> {{ user.first_name }}</p>
                        <p><b>Last Name:</b> {{ user.last_name }}</p>
                        <p>
                            <b>Country:</b>
                            {{
                                profile === undefined
                                    ? ''
                                    : profile.country
                            }}
                        </p>
                        <p>
                            <b>Institution:</b>
                            {{
                                profile === undefined
                                    ? ''
                                    : profile.institution
                            }}
                        </p>
                        <p>
                            <b>Field of Study:</b>
                            {{
                                profile === undefined
                                    ? ''
                                    : profile.field_of_study
                            }}
                        </p>
                        <p>
                            <b>Orcid ID:</b>
                            {{
                                profile === undefined
                                    ? ''
                                    : profile.orcid_id
                            }}
                        </p>
                        <br />
                        <h4>Github</h4>
                        <br />
                        <p>
                            <b>Username:</b>
                            {{
                                profile === undefined ||
                                profile.github_username === ''
                                    ? 'None'
                                    : this.user.profile.github_username
                            }}
                        </p>
                        <p>
                            <b>Workflows:</b>
                            {{
                                profile === undefined ||
                                profile.github_username === ''
                                    ? 'None'
                                    : this.workflows
                            }}
                        </p>
                    </b-card-text>
                </b-card>
            </div>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'Profile',
    data() {
        return {
            githubUser: null
        };
    },
    created: function() {
        this.$store.dispatch('loadUsers');
    },
    computed: mapGetters(['user', 'profile', 'loggedIn', 'profileIncomplete']),
    methods: {
        saveUserInfo(
            userName,
            firstName,
            lastName,
            orcidId,
            country,
            institution,
            fieldOfStudy
        ) {
            this.$store.dispatch('updateUser', {
                userName: userName,
                firstName: firstName,
                lastName: lastName,
                orcidId: orcidId,
                country: country,
                institution: institution,
                fieldOfStudy: fieldOfStudy
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
