<template>
    <div class="mb-4">
        <b-container>
            <div>
                <b-row align-content="center">
                    <b-col>
                        <h5 class="text-center">
                            Logging out of PlantIT...
                        </h5>
                    </b-col>
                </b-row>
            </div>
        </b-container>
    </div>
</template>

<script>
import Auth from '@/services/apiV1/Auth';

export default {
    name: 'Logout',
    data() {
        return {
            seconds: 3
        };
    },
    methods: {
        logout: function() {
            Auth.logout();
            this.$router.push({ path: '/' })
        }
    },
    mounted() {
        setTimeout(this.logout, this.seconds * 1000);
    }
};
</script>

<style scoped></style>
