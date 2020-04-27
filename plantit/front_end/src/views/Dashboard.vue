<template>
    <div class="m-0 p-0">
        <b-container>
            <b-row class="justify-content-md-center mb-4">
                <b-col>
                    <b-tabs justified active-nav-item-class="bg-success" pills>
                        <br />
                        <b-tab title="Collections" active>
                            <template v-slot:title class="m-0 p-0">
                                <b class="dark"><i class="fas fa-layer-group dark mr-1"></i>Collections</b>
                            </template>
                            <p>
                                To create a new collection , click the
                                <i class="fas fa-plus"></i> icon below. Select
                                an existing collection to edit metadata and
                                upload samples.
                            </p>
                            <SelectCollection
                                filterable="true"
                                v-on:selected="onSelected"
                            ></SelectCollection>
                        </b-tab>
                        <b-tab title="Workflows">
                            <template v-slot:title class="m-0 p-0">
                                <b class="dark"><i class="fas fa-stream dark mr-1"></i>Workflows</b>
                            </template>
                            <p>
                                Select a workflow below to
                                start analyzing data.
                            </p>
                            <SelectWorkflow filterable="true"></SelectWorkflow>
                        </b-tab>
                        <b-tab title="Jobs">
                            <template v-slot:title class="m-0 p-0">
                                <b class="dark"><i class="fas fa-terminal dark mr-1"></i>Jobs</b>
                            </template>
                            <p>
                                To start a new job, go to the
                                <b-link href="/user/workflows"
                                    >workflows</b-link
                                >
                                page or click the
                                <i class="fas fa-plus"></i> icon below to select
                                a workflow. Select an existing job to view logs
                                and results.
                            </p>
                            <SelectJob filterable="true"></SelectJob>
                        </b-tab>
                    </b-tabs>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>
<script>
import router from '../router';
import SelectCollection from '@/components/collections/SelectCollection.vue';
import SelectWorkflow from '@/components/collections/SelectWorkflow.vue';
import SelectJob from '@/components/SelectJob.vue';

export default {
    name: 'Dashboard',
    components: {
        SelectCollection,
        SelectWorkflow,
        SelectJob
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

<style scoped lang="sass">
@import '../scss/_colors.sass'
@import '../scss/main.sass'
.dark
  color: $dark
.success
  color: $success
.selected
  background-color: $color-button
  color: $dark
</style>
