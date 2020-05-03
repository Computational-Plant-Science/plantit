<template>
    <div class="mb-4">
        <b-container>
            <div>
                <b-row>
                    <b-col>
                        <b-tabs
                            justified
                            active-nav-item-class="bg-success"
                            pills
                            vertical
                            v-model="state"
                        >
                            <b-tab title="Collections" active>
                                <template v-slot:title class="m-0 p-0">
                                    <b
                                        class="dark"
                                        v-on:click="onListCollections"
                                        ><i
                                            class="fas fa-layer-group dark mr-1"
                                        ></i
                                        >Collections</b
                                    >
                                </template>
                                <SelectCollection
                                    filterable="true"
                                    v-on:selected="onViewCollection"
                                    v-on:new="onNewCollection"
                                    v-if="
                                        collection_state ===
                                            CollectionState.List
                                    "
                                ></SelectCollection>
                                <Collection
                                    v-if="
                                        collection_state ===
                                            CollectionState.View
                                    "
                                    :pk="collection_pk"
                                ></Collection>
                                <NewCollection
                                    v-if="
                                        collection_state ===
                                            CollectionState.New
                                    "
                                    v-on:back="onListCollections"
                                    v-on:view="onViewCollection"
                                >
                                </NewCollection>
                            </b-tab>
                            <b-tab title="Workflows">
                                <template v-slot:title class="m-0 p-0">
                                    <b class="dark" v-on:click="onListWorkflows"
                                        ><i class="fas fa-stream dark mr-1"></i
                                        >Workflows</b
                                    >
                                </template>
                                <SelectWorkflow
                                    v-if="workflow_state === WorkflowState.List"
                                    filterable="true"
                                    v-on:workflowSelected="onConfigureWorkflow"
                                ></SelectWorkflow>
                                <SubmitWorkflow
                                    v-if="
                                        workflow_state === WorkflowState.Submit
                                    "
                                    :workflow_name="workflow_name"
                                    v-on:workflowSubmitted="onViewJob"
                                ></SubmitWorkflow>
                            </b-tab>
                            <b-tab title="Jobs">
                                <template v-slot:title class="m-0 p-0">
                                    <b class="dark" v-on:click="onListJobs"
                                        ><i
                                            class="fas fa-terminal dark mr-1"
                                        ></i
                                        >Jobs</b
                                    >
                                </template>
                                <SelectJob
                                    filterable="true"
                                    v-if="job_state === JobState.List"
                                    v-on:workflowSelected="onConfigureWorkflow"
                                    v-on:jobSelected="onViewJob"
                                ></SelectJob>
                                <Job
                                    v-if="job_state === JobState.View"
                                    :pk="job_pk"
                                ></Job>
                            </b-tab>
                        </b-tabs>
                    </b-col>
                </b-row>
            </div>
        </b-container>
    </div>
</template>
<script>
import Collection from '@/views/Collection.vue';
import SubmitWorkflow from '@/views/SubmitWorkflow.vue';
import Job from '@/views/Job.vue';
import SelectCollection from '@/components/collections/SelectCollection.vue';
import SelectWorkflow from '@/components/collections/SelectWorkflow.vue';
import SelectJob from '@/components/SelectJob.vue';
import NewCollection from "./NewCollection";

const State = Object.freeze({ Collections: 1, Workflows: 2, Jobs: 3 });
const CollectionState = Object.freeze({ List: 1, View: 2, New: 3 });
const WorkflowState = Object.freeze({ List: 1, Submit: 2 });
const JobState = Object.freeze({ List: 1, View: 2 });

export default {
    name: 'Dashboard',
    components: {
        NewCollection,
        Collection,
        SubmitWorkflow,
        Job,
        SelectCollection,
        SelectWorkflow,
        SelectJob
    },
    data() {
        return {
            State: State,
            CollectionState: CollectionState,
            WorkflowState: WorkflowState,
            JobState: JobState,
            state: State.Collections,
            collection_state: CollectionState.List,
            workflow_state: WorkflowState.List,
            job_state: JobState.List,
            collection_pk: null,
            workflow_name: null,
            job_pk: null
        };
    },
    methods: {
        onListCollections() {
            this.collection_state = CollectionState.List;
            this.collection_pk = null;
        },
        onViewCollection(collection) {
            this.collection_pk = collection.pk;
            this.collection_state = CollectionState.View;
        },
        onNewCollection() {
            this.collection_state = CollectionState.New;
        },
        onListWorkflows() {
            this.workflow_state = WorkflowState.List;
        },
        onConfigureWorkflow(workflow) {
            this.workflow_name = workflow.app_name;
            this.workflow_state = WorkflowState.Submit;
        },
        onListJobs() {
            this.job_state = JobState.List;
        },
        onViewJob(pk) {
            this.job_pk = pk;
            this.state = State.Jobs;
            this.job_state = JobState.View;
        },
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
