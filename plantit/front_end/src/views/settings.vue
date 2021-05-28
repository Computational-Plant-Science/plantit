<template>
    <b-container fluid class="m-0 p-3" style="background-color: transparent;">
        <b-row class="m-1"
            ><b-col align-self="center" cols="3">
                <i v-if="profile.darkMode" class="fas fa-sun fa-1x fa-fw"></i>
                <i v-else class="fas fa-moon fa-1x fa-fw"></i>
                Dark Mode:
                {{ profile.darkMode ? 'enabled' : 'disabled' }} </b-col
            ><b-col align-self="center" cols="8">
                <b-button size="sm" @click="toggleDarkMode"
                    >{{ profile.darkMode ? 'Disable' : 'Enable'
                    }}<b-spinner
                        small
                        v-if="togglingDarkMode"
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="ml-2 mb-1"
                    ></b-spinner></b-button></b-col
        ></b-row>
        <b-row class="m-1">
            <b-col align-self="center" cols="3"
                ><i class="fas fa-envelope fa-1x fa-fw"></i>
                Push Notifications:
                {{ profile.pushNotifications }}
            </b-col>
            <b-col align-self="center" cols="8">
                <b-button
                    size="sm"
                    v-if="profile.pushNotifications !== 'pending'"
                    @click="togglePushNotifications"
                    >{{
                        profile.pushNotifications === 'enabled'
                            ? 'Disable'
                            : 'Enable'
                    }}<b-spinner
                        small
                        v-if="togglingPushNotifications"
                        label="Loading..."
                        :variant="profile.darkMode ? 'light' : 'dark'"
                        class="ml-2 mb-1"
                    ></b-spinner></b-button
            ></b-col>
        </b-row>
    </b-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'settings',
    data: function() {
        return {
            togglingDarkMode: false,
            togglingPushNotifications: false
        };
    },
    computed: {
        ...mapGetters('user', ['profile', 'profileLoading'])
    },
    methods: {
        async toggleDarkMode() {
            this.togglingDarkMode = true;
            await this.$store.dispatch('user/toggleDarkMode');
            this.togglingDarkMode = false;
        },
        async togglePushNotifications() {
            this.togglingPushNotifications = true;
            await this.$store.dispatch('user/togglePushNotifications');
            this.togglingPushNotifications = false;
        }
    }
};
</script>

<style scoped></style>
