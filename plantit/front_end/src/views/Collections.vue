<template>
    <div class="m-0 p-0">
        <b-container>
            <h3><i class="fas fa-layer-group"></i> Collections</h3>
            <hr />
            <p>
                A <i>collection</i> is a group of <i>samples</i>. A sample can
                be any data file. PlantIT workflows operate on the samples in a
                collection.
            </p>
            <p>
                To create a new collection , click the
                <i class="fas fa-plus"></i> icon below. Select an existing
                collection to edit metadata and upload samples.
            </p>
            <SelectCollection
                filterable="true"
                v-on:selected="onSelected"
            ></SelectCollection>
        </b-container>
    </div>
</template>

<script>
import SelectCollection from '@/components/collections/SelectCollection.vue';
import router from '../router';

export default {
    name: 'Collections',
    components: {
        SelectCollection
    },
    data() {
        return {
            links: [
                {
                    text: 'Dashboard',
                    to: '/user/dashboard'
                },
                {
                    text: 'Jobs',
                    to: '/user/jobs'
                }
            ]
        };
    },
    methods: {
        onSelected(collection) {
            router.push({ name: 'collection', query: { pk: collection.pk } });
        },
        createNew: function() {
            router.push({ name: 'newCollection' });
        }
    }
};
</script>
