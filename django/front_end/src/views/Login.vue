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
import Auth from '@/services/apiV1/Auth'

export default {
    name: 'Login',
    components: {
    },
    methods:{
      login: function() {
        console.log(Auth.login("admin","admin"))
      },
      logout: function() {
        console.log(Auth.logout())
      }
    }
};
</script>
