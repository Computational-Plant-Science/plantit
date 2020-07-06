<template>
    <b-table
        :items="params"
        :fields="fields"
        responsive="sm"
        borderless
        small
        sticky-header="true"
        caption-top
    >
        <template v-slot:table-caption
            >Enter values for workflow parameters.</template
        >
        <template v-slot:cell(name)="param">
            {{ param.item.key }}
        </template>
        <template v-slot:cell(value)="param">
            <b-form-input
                size="sm"
                v-model="param.item.value"
                :placeholder="'Enter a value for \'' + param.item.key + '\''"
            ></b-form-input>
        </template>
    </b-table>
</template>

<script>
export default {
    name: 'EditParameters',
    props: {
        params: {
            type: Array,
            required: true
        }
    },
    data() {
        return {
            fields: [
                {
                    key: 'name',
                    label: 'Name'
                },
                {
                    key: 'value',
                    label: 'Value'
                }
            ]
        };
    }
};
</script>

<style scoped></style>
