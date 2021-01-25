<template>
    <div>
        <b :class="darkMode ? 'text-white' : 'text-dark'">
            Select a cluster or server to submit this run to.
        </b>
        <br />
        <b-table
            :items="targets.filter(target => !target.disabled)"
            :fields="fields"
            responsive="sm"
            borderless
            small
            selectable
            select-mode="single"
            @row-selected="rowSelected"
            sticky-header="true"
            caption-top
            :table-variant="darkMode ? 'dark' : 'white'"
        >
            <template v-slot:cell(name)="target">
                {{ target.item.name }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.host }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.max_cores }}
            </template>
            <template v-slot:cell(host)="target">
                {{ target.item.max_processes }}
            </template>
            <template v-slot:cell(host)="target">
              <span v-if="target.item.max_mem >= flo">{{ target.item.max_mem }}</span>
            </template>
            <template v-slot:cell(gpu)="target">
                <i
                    :class="target.item.gpu ? 'text-success' : 'text-secondary'"
                    v-if="target.item.gpu"
                    class="far fa-check-circle"
                ></i>
                <i
                    :class="target.item.gpu ? 'text-success' : 'text-secondary'"
                    v-else
                    class="far fa-times-circle"
                ></i>
            </template>
        </b-table>
        <b-row align-h="center" v-if="targetsLoading">
            <b-spinner
                type="grow"
                label="Loading..."
                variant="success"
            ></b-spinner>
        </b-row>
        <b-row
            align-h="center"
            class="text-center"
            v-if="!targetsLoading && targets.length === 0"
        >
            <b-col>
                None to show.
            </b-col>
        </b-row>
    </div>
</template>
<script>
