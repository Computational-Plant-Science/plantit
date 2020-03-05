<template>
    <div>
        <PageNavigation> </PageNavigation>

        <b-container class="content-box center-container p-4">
            <h2>Create a New Collection</h2>
            <NewCollectionForm></NewCollectionForm>
        </b-container>
    </div>
</template>

<script>
import NewCollectionForm from '@/components/collections/NewCollectionForm.vue';
import PageNavigation from '@/components/PageNavigation.vue';

export default {
    name: 'NewCollection',
    components: {
        NewCollectionForm,
        PageNavigation
    }
};
</script>
