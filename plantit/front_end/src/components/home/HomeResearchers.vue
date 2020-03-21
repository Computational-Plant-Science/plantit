<template>
    <div>
        <b-card title="Explore...">
            <b-card-text>
                        ...data and reproduce analyses without wrangling infrastructure.
                        <b-img
                            center
                            fluid
                            :src="require('@/assets/frontpage/icons/hex1.png')"
                            alt="Plant IT"></b-img>
                </b-card-text>
        </b-card>
    </div>
</template>

<script>
export default {
    name: 'HomeResearchers'
};
</script>

<style scoped lang="sass">
@import '../../scss/_colors.sass'

h1
  color: $color-highlight
</style>
