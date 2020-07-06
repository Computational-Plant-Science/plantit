<template>
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
            clusters: []
        };
    },
    mounted: function() {
        Clusters.getClusters().then(data => {
            this.clusters = data.clusters;
        });
    },
    methods: {
        rowSelected: function(items) {
            this.$emit('targetSelected', items[0]);
        }
    }
};
</script>

<style scoped></style>
