<template>
        <b-container class="m-0 p-0" fluid>
            <b-row>
                <b-col class="pl-10">

        <b-card
            class="rounded-0"
            bg-variant="dark"
            border-variant="dark"
            text-variant="white"
            header-bg-variant="dark"
            header-border-variant="dark"
        >
            <template slot="header" style="border: none">
                <h2>Researchers</h2>
                <p>PlantIT takes care of infrastructure details so you can focus on your data.</p>
            </template>
            <b-img
                    style="border: none"
                center
                fluid
                :src="require('@/assets/frontpage/icons/hex1.png')"
                alt="Plant IT"
            ></b-img>
        </b-card>
                </b-col>
                    </b-row>
            </b-container>
</template>

<script>
export default {
    name: 'HomeResearchers'
};
</script>

<style scoped></style>
