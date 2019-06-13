<template>
    <p>
        {{ label }}
        <span @click="editing = true" v-show="!editing">
            {{ valueInteral }}
        </span>
        <span v-show="editing">
            <input
                v-model="valueInteral"
                @keydown.enter="editing = false"
                @blur="editing = false"
                type="text"
                ref="input"
            />
        </span>
    </p>
</template>

<script>
export default {
    props: ['label', 'value'],
    data() {
        return {
            editing: false,
            valueInteral: this.value
        };
    },
    watch: {
        editing: function(val) {
            if (val) {
                this.$nextTick(() => this.$refs.input.focus());
            }
            {
                this.$emit('input', this.valueInteral);
            }
        }
    }
};
</script>

<style scoped></style>
