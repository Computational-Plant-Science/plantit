<template>
    <div>
        <b-button @click="login">
            Login
        </b-button>
        <b-button @click="logout">
            Logout
        </b-button>
    </div>
</template>

<script>
import Auth from '@/services/Auth';

export default {
    name: 'Login',
    components: {},
    methods: {
        login: function() {
            Auth.login('admin', 'admin');
        },
        logout: function() {
            Auth.logout();
        }
    }
};
</script>
