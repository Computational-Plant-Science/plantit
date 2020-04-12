<template>
    <div>
        <b-container class="justify-content-md-center">
            <b-card title="New Collection">
                <hr />
                <NewCollectionForm></NewCollectionForm>
            </b-card>
        </b-container>
    </div>
</template>

<script>
import NewCollectionForm from '@/components/collections/NewCollectionForm.vue';

export default {
    name: 'NewCollection',
    components: {
        NewCollectionForm
    }
};
</script>
