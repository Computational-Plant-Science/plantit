<template>
    <b-container>
        {{ this.info }}
    </b-container>
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

