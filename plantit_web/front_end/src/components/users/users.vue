<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent">
        <div>
            <div v-if="isRootPath">
                <b-row
                    ><b-col
                        ><h4
                            :class="
                                profile.darkMode ? 'text-light' : 'text-dark'
                            "
                        >
                            <i class="fas fa-user-friends fa-fw"></i> Users
                        </h4></b-col
                    ></b-row
                >
                <b-row
                    ><b-col
                        ><b-input-group size="sm"
                            ><template #prepend>
                                <b-input-group-text
                                    ><i class="fas fa-search"></i
                                ></b-input-group-text> </template
                            ><b-form-input
                                :class="
                                    profile.darkMode
                                        ? 'theme-search-dark'
                                        : 'theme-search-light'
                                "
                                size="lg"
                                type="search"
                                v-model="searchText"
                            ></b-form-input> </b-input-group></b-col
                ></b-row>
                <b-row v-if="usersLoading" class="mt-2">
                    <b-col class="text-left">
                        <b-spinner
                            small
                            v-if="usersLoading"
                            label="Loading..."
                            :variant="profile.darkMode ? 'light' : 'dark'"
                            class="mr-1"
                        ></b-spinner
                        ><span
                            :class="
                                profile.darkMode ? 'text-white' : 'text-dark'
                            "
                            >Loading users...</span
                        >
                    </b-col>
                </b-row>
                <b-card-group
                    v-else
                    deck
                    columns
                    class="justify-content-center mt-3"
                >
                    <b-card
                        v-for="user in filteredUsers"
                        :key="user.username"
                        :bg-variant="profile.darkMode ? 'dark' : 'white'"
                        :header-bg-variant="profile.darkMode ? 'dark' : 'white'"
                        border-variant="default"
                        :header-border-variant="
                            profile.darkMode ? 'secondary' : 'default'
                        "
                        :text-variant="profile.darkMode ? 'white' : 'dark'"
                        style="min-width: 30rem; max-width: 40rem"
                        class="overflow-hidden mb-4"
                    >
                        <b-row align-v="center">
                            <b-col style="color: white; cursor: pointer">
                                <h5
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    <b-img
                                        v-if="user.github_profile !== undefined"
                                        class="avatar m-0 mb-1 p-0 github-hover logo"
                                        style="
                                            width: 20px;
                                            height: 20px;
                                            position: relative;
                                            border: 1px solid #e2e3b0;
                                            top: 3px;
                                        "
                                        rounded="circle"
                                        :src="user.github_profile.avatar_url"
                                    ></b-img>
                                    <span
                                        v-else
                                        style="
                                            max-height: 4rem;
                                            max-width: 4rem;
                                            opacity: 0.9;
                                            position: absolute;
                                            right: -15px;
                                            top: 15px;
                                            z-index: 1;
                                        "
                                    >
                                        <i class="far fa-user fa-fw fa-3x"></i>
                                    </span>
                                    <b-link
                                        :class="
                                            profile.darkMode
                                                ? 'text-white ml-2'
                                                : 'text-dark ml-2'
                                        "
                                        :href="
                                            'https://github.com/' +
                                            user.github_username
                                        "
                                    >
                                        <small>{{
                                            user.github_username
                                        }}</small>
                                    </b-link>
                                    <small
                                        :class="
                                            profile.darkMode
                                                ? 'text-warning'
                                                : 'text-dark'
                                        "
                                    >
                                        ({{ user.username }})</small
                                    >
                                </h5>
                            </b-col>
                            <b-col
                                md="auto"
                                class="m-0 text-left"
                                title="You"
                                v-if="
                                    user.username ===
                                    profile.djangoProfile.username
                                "
                                ><small
                                    ><i
                                        class="far fa-star text-secondary fa-fw"
                                    ></i></small
                            ></b-col>
                        </b-row>
                        <b-row align-v="center">
                            <b-col
                                :class="
                                    profile.darkMode
                                        ? 'text-white'
                                        : 'text-dark'
                                "
                            >
                                <b-row
                                    ><b-col><small>name</small></b-col
                                    ><b-col cols="10"
                                        >{{ user.first_name }}
                                        {{ user.last_name }}</b-col
                                    ></b-row
                                >
                                <b-row
                                    ><b-col><small>bio</small></b-col
                                    ><b-col cols="10">{{
                                        user.github_profile &&
                                        user.github_profile.bio
                                            ? user.github_profile.bio
                                            : '(none)'
                                    }}</b-col></b-row
                                >
                            </b-col>
                        </b-row>
                    </b-card>
                </b-card-group>
            </div>
            <router-view
                v-else
                :class="profile.darkMode ? 'theme-dark' : 'theme-light'"
            ></router-view>
        </div>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';
import moment from 'moment';

export default {
    name: 'Users',
    data: function () {
        return {
            searchText: '',
            addingCollaborator: false,
            removingCollaborator: false,
        };
    },
    async mounted() {
        await this.$store.dispatch('users/loadAll');
    },
    computed: {
        ...mapGetters('user', ['profile']),
        ...mapGetters('users', ['allUsers', 'usersLoading']),
        isRootPath() {
            return this.$route.name === 'users';
        },
        filteredUsers() {
            return this.allUsers.filter((user) =>
                user.username.includes(this.searchText)
            );
        },
    },
    methods: {
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async refreshUsers() {
            await this.$store.dispatch('users/loadAll');
        },
    },
};
</script>

<style scoped lang="sass">
@import "../../scss/_colors.sass"
@import "../../scss/main.sass"

.hvr:hover
  text-decoration: underline
  text-underline-color: $dark
  cursor: pointer
</style>
