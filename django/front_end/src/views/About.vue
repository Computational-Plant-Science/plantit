<template>
    <div>
        <PageNavigation></PageNavigation>
    </div>
</template>

<script>
// @ is an alias to /src
import PageNavigation from '@/components/PageNavigation.vue';

export default {
    name: 'home',
    components: {
        PageNavigation
    },
    data() {
        return {
            links: [
                {
                    text: 'home',
                    to: '/'
                }
            ]
        };
    }
};
</script>
