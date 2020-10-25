<template>
    <div id="app" class="m-0 p-0" style="width: 100vw; min-height: 100vh;">
        <b-container
            fluid
            class="m-0 p-0"
            style="width: 100vw; min-height: 100vh;"
        >
            <Navigation v-if="$route.path !== '/'"></Navigation>
            <!--{{ keycloak.idToken }}
            <br />
            {{ keycloak.clientId }}
            <br />
            {{ keycloak.authServerUrl }}-->

            <router-view
                :class="darkMode ? 'theme-dark' : 'theme-light'"
                style="width: 100vw; min-height: 100vh;"
            ></router-view>
        </b-container>
    </div>
</template>

<script>
import Navigation from '@/components/navigation';
import { mapGetters } from 'vuex';

export default {
    name: 'App',
    components: {
        Navigation
    },
    computed: mapGetters([
        'darkMode',
        'currentUserDjangoProfile',
        'currentUserCyVerseProfile',
        'currentUserGitHubProfile',
        'loggedIn'
    ]),
    data() {
        return {};
    }
};
</script>

<style scoped lang="sass">
@import 'scss/main.sass'
@import 'scss/_colors.sass'
.dark
    background-color: $dark
.light
    background-color: white
</style>
