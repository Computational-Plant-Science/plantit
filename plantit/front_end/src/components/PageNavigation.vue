<template>
    <b-nav>
        <b-navbar class="mx-auto">
            <slot name="page-nav"></slot>
        </b-navbar>

        <div class="button-nav">
            <slot name="buttons"></slot>
        </div>
    </b-nav>
</template>

<script>
export default {
    name: 'PageNavigation'
};
</script>
