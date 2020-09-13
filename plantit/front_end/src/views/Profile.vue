<template>
    <div class="w-100 p-5 m-0">
        <br />
        <br />
        <b-container v-if="user">
            <div class="w-100 pb-4">
                <b-card
                    bg-variant="white"
                    border-variant="white"
                    header-border-variant="white"
                    header-bg-variant="white"
                    :img-src="githubProfile ? githubProfile.avatar_url : ''"
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
                    <b-card-text v-if="cyverseProfile">
                        <h4>Profile</h4>
                        <br />
                        <p><b>Email Address:</b> {{ cyverseProfile.email }}</p>
                        <p><b>First Name:</b> {{ cyverseProfile.first_name }}</p>
                        <p><b>Last Name:</b> {{ cyverseProfile.last_name }}</p>
                        <p>
                            <b>Institution:</b>
                            {{
                                cyverseProfile === undefined
                                    ? ''
                                    : cyverseProfile.institution
                            }}
                        </p>
                        <br />
                    </b-card-text>
                  <b-card-text v-if="githubProfile">
                        <h4>Github</h4>
                        <br />
                        <p>
                            <b>Username:</b>
                            {{
                                githubProfile === undefined ||
                                githubProfile.github_username === ''
                                    ? 'None'
                                    : this.user.profile.github_username
                            }}
                        </p>
                        <p>
                            <b>Workflows:</b>
                            {{
                                githubProfile === undefined ||
                                githubProfile.github_username === ''
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
    created: function() {
        this.$store.dispatch('loadUsers');
    },
    computed: mapGetters([
        'user',
        'githubProfile',
        'cyverseProfile',
        'loggedIn'
    ])
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.green
    color: $color-button
</style>
