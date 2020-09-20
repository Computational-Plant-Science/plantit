<template>
    <b-card
        border-variant="white"
        footer-bg-variant="white"
        sub-title="Configure parameters."
    >
        <b-table
            :items="params"
            :fields="fields"
            responsive="sm"
            borderless
            small
            sticky-header="true"
            caption-top
        >
            <template v-slot:cell(name)="param">
                {{ param.item.toLowerCase() }}
            </template>
            <template v-slot:cell(value)="param">
                <b-form-input
                    size="sm"
                    v-model="param.item.value"
                    :placeholder="
                        'Enter a value for \'' + param.item.toLowerCase() + '\''
                    "
                ></b-form-input>
            </template>
        </b-table>
    </b-card>
</template>

<script>
export default {
    name: 'run-params',
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
