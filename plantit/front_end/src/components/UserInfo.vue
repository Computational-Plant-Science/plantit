<template>
        <div class="w-100 p-2">
          <b-card
            :title="this.info['username']"
            :img-src="require('../assets/icons/default_user.png')"
            img-alt="Image"
            img-top
            tag="profile"
            style="max-width: 15rem;">
              <hr>
            <b-card-text>
                <p><b>Email Address:</b> {{ this.info['email'] }}</p>
                <p><b>First Name:</b> {{ this.info['first_name'] }}</p>
                <p><b>Last Name:</b> {{ this.info['last_name'] }}</p>
                <p><b>City:</b> {{ this.info['city'] }}</p>
                <p><b>Country:</b> {{ this.info['country'] }}</p>
                <p><b>Affiliation:</b> {{ this.info['affiliation'] }}</p>
            </b-card-text>
          </b-card>
            </div>
</template>

<script>
import UserApi from '@/services/apiV1/UserManager.js';

export default {
    name: 'UserInfo',
    data() {
        return {
            info: {}
        };
    },
    mounted: function() {
        UserApi.getCurrentUser().then(info => (this.info = info));
    }
}
</script>

