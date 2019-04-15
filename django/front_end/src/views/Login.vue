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

export default {
    name: 'Login',
    components: {
    },
    methods:{
      login: function() {
        this.$http.post("/apis/v1/auth/login/", {
          username: "admin",
          password: "admin"
        })
        .then(function (response) {
          console.log(response);
        })
        .catch(function (error) {
          console.log(error);
        })
      },
      logout: function() {
        this.$http.get("/apis/v1/auth/logout/")
        .then(function (response) {
          console.log(response);
        })
        .catch(function (error) {
          console.log(error);
        })
      }
    }
};
</script>
