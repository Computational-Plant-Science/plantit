<template>
    <div>
        <b-table
            :items="clusters"
            :fields="fields"
            responsive="sm"
            borderless
            small
            selectable
            @row-selected="rowSelected"
            sticky-header="true"
            caption-top
        >
            <template v-slot:table-caption
                >Select a deployment target.</template
            >
            <template v-slot:cell(name)="cluster">
                {{ cluster.item.name }}
            </template>
            <template v-slot:cell(host)="cluster">
                {{ cluster.item.host }}
            </template>
        </b-table>
        <b-row align-h="center" v-if="clustersLoading">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="dark"
            ></b-spinner>
        </b-row>
        <b-row align-h="center" class="text-center" v-if="!clustersLoading && clusters.length === 0">
            <b-col>
            None to show.
                </b-col>
        </b-row>
    </div>
</template>

<script>
import Clusters from '../services/apiV1/ClusterManager';
export default {
    name: 'SelectTarget',
    props: {
        selected: {
            type: Object,
            required: false
        }
    },
    data: function() {
        return {
            fields: [
                {
                    key: 'name',
                    label: 'Name'
                },
                {
                    key: 'host',
                    label: 'Host'
                }
            ],
            clusters: [],
            clustersLoading: false
        };
    },
    mounted: function() {
        this.reloadClusters();
    },
    methods: {
        reloadClusters: function() {
            this.clustersLoading = true;
            Clusters.getClusters().then(data => {
                this.clusters = data.clusters;
                this.clustersLoading = false;
            });
        },
        rowSelected: function(items) {
            this.$emit('targetSelected', items[0]);
        }
    }
};
</script>

<style scoped></style>
