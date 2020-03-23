<template>
    <div class="w-100 p-2">
                    <b-container>
        <b-card
                :img-src="require('../assets/icons/default-user-small.png')"
                img-alt="Image"
                img-top
                tag="profile"
                style="max-width: 20rem;">
                <b-row>
                    <b-col>
                        <h4>{{ this.info['username'] }}</h4>
                    </b-col>
                    <b-col md="auto">
                        <b-button
                                id="edit-btn"
                                @click="$bvModal.show('editUserInfo')"
                                class="plantit-btn"
                                v-b-tooltip.hover
                                title="Edit collection name, description, and metadata.">
                            <i class="far fa-edit"></i>
                        </b-button>
                    </b-col>
                </b-row>
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
                                    </b-container>

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
        mounted: function () {
            UserApi.getCurrentUser().then(info => (this.info = info));
        }
    }
</script>

