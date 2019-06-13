<template>
    <div>
        <h4>{{ group.name }}</h4>
        <div v-if="group.params" class="form-group-fields">
            <FormField
                class="p-2"
                v-for="field in group.params"
                :key="field.id"
                :field="field"
                @onChange="fieldChanged"
            >
            </FormField>
        </div>

        <FormGroup
            @onChange="groupChanged"
            v-for="subgroup in group.groups"
            :key="subgroup.id"
            :group="subgroup"
        ></FormGroup>
    </div>
</template>

<script>
import FormField from '@/components/FormField';
export default {
    name: 'FormGroup',
    components: {
        FormField
    },
    props: ['group'],
    data: function() {
        return {
            values: {
                params: {},
                groups: {}
            }
        };
    },
    methods: {
        fieldChanged(field, value) {
            //Update paramater value
            this.values['params'][field] = value;
            this.$emit('onChange', this.group.id, this.values);
        },
        groupChanged(group, value) {
            //Update values of subgroup
            this.values['groups'][group] = value;
            this.$emit('onChange', this.group.id, this.values);
        }
    }
};
</script>

<style lang="sass">
.form-group-fields
  display: flex
  flex-wrap: wrap
  align-items: center
  justify-content: flex-start
</style>
