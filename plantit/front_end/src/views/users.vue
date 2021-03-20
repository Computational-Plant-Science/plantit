<template>
    <div
        class="w-100 h-100 pl-3 pt-3"
        :style="
            profile.darkMode
                ? 'background-color: #d6df5D'
                : 'background-color: white' + '; min-height: 100%'
        "
    >
        <br />
        <br />
        <b-container class="pl-3 pt-3">
            <b-row align-v="center" align-h="center" v-if="usersLoading">
                <b-col align-self="end" class="text-center">
                    <b-spinner
                        type="grow"
                        label="Loading..."
                        variant="secondary"
                    ></b-spinner>
                </b-col>
            </b-row>
            <b-row v-else align-v="center" align-h="center">
                <b-col>
                    <b-row
                        ><b-col
                            ><h3
                                :class="
                                    profile.darkMode
                                        ? 'text-light'
                                        : 'text-dark'
                                "
                            >
                                User Registry
                            </h3> </b-col
                        ><!--<b-col md="auto"
                            ><b-dropdown
                                dropleft
                                :variant="
                                    profile.darkMode ? 'outline-white' : 'white'
                                "
                                ><template #button-content>Actions</template
                                ><b-dropdown-item></b-dropdown-item></b-dropdown></b-col>--></b-row
                    ><b-row
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
                    <b-card-group
                        deck
                        columns
                        class="justify-content-center mt-3"
                    >
                        <b-card
                            v-for="user in users"
                            :key="user.username"
                            :bg-variant="profile.darkMode ? 'dark' : 'white'"
                            :header-bg-variant="
                                profile.darkMode ? 'dark' : 'white'
                            "
                            border-variant="default"
                            :header-border-variant="
                                profile.darkMode ? 'secondary' : 'default'
                            "
                            :text-variant="profile.darkMode ? 'white' : 'dark'"
                            style="min-width: 30rem; max-width: 40rem;"
                            class="overflow-hidden mb-4"
                        >
                            <b-row align-v="center">
                                <b-col
                                    style="color: white; cursor: pointer"
                                    @click="userSelected(user)"
                                >
                                    <h5
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                    >
                                        {{ user.first_name }}
                                        {{ user.last_name }}
                                        <small
                                            :class="
                                                profile.darkMode
                                                    ? 'text-warning'
                                                    : 'text-dark'
                                            "
                                            >({{ user.username }})</small
                                        >
                                    </h5>
                                </b-col>
                            </b-row>
                            <b-row align-v="center">
                                <b-col
                                    :class="
                                        profile.darkMode
                                            ? 'text-white'
                                            : 'text-dark'
                                    "
                                >
                                    {{
                                        user.github_profile
                                            ? user.github_profile.bio
                                            : ''
                                    }}
                                </b-col>
                            </b-row>
                            <br />
                            <b-row align-v="center">
                                <b-col v-if="user.github_username">
                                    <b-link
                                        :class="
                                            profile.darkMode
                                                ? 'text-white'
                                                : 'text-dark'
                                        "
                                        :href="
                                            'https://github.com/' +
                                                user.github_username
                                        "
                                    >
                                        <i
                                            class="fab fa-github fa-fw fa-1x mr-2 ml-1 pl-1"
                                        ></i>
                                        <small>{{
                                            user.github_username
                                        }}</small>
                                    </b-link>
                                </b-col>
                                <b-col class="ml-0 mr-0" align-self="left">
                                    <b-img
                                        v-if="user.github_profile !== undefined"
                                        right
                                        rounded
                                        class="avatar card-img-right"
                                        style="max-height: 4rem; max-width: 4rem; opacity: 0.9; position: absolute; right: -15px; top: -25px; z-index:1;"
                                        :src="user.github_profile.avatar_url"
                                    ></b-img>
                                    <span
                                        v-else
                                        style="max-height: 4rem; max-width: 4rem; opacity: 0.9; position: absolute; right: -15px; top: 15px; z-index:1;"
                                    >
                                        <i class="far fa-user fa-fw fa-3x"></i>
                                    </span>
                                </b-col>
                            </b-row>
                        </b-card>
                    </b-card-group>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import { mapGetters } from 'vuex';
import router from '@/router';

export default {
    name: 'Users',
    async mounted() {
        await this.$store.dispatch('loadUsers');
    },
    computed: mapGetters(['profile', 'users', 'usersLoading']),
    data: function() {
        return {
            searchText: ''
        };
    },
    methods: {
        goToFlows() {
            router.push({ name: 'workflows' });
        },
        userSelected(user) {
            router.push({
                name: 'user',
                params: {
                    username:
                        user.username === 'Computational-Plant-Science' ||
                        user.username === 'van-der-knaap-lab'
                            ? user.github_username
                            : user.username
                }
            });
        }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"
@import "../scss/main.sass"

.hvr:hover
  text-decoration: underline
  text-underline-color: $dark
  cursor: pointer
</style>
