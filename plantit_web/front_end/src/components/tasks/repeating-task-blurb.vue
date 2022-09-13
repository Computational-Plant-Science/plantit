<template>
    <b-card
        class="mt-2 pt-1 overflow-hidden"
        :bg-variant="profile.darkMode ? 'dark' : 'white'"
        :header-text-variant="profile.darkMode ? 'white' : 'dark'"
        border-variant="secondary"
        :text-variant="profile.darkMode ? 'white' : 'dark'"
        :body-text-variant="profile.darkMode ? 'white' : 'dark'"
        no-body
    >
        <b-card-body>
            <b-img
                v-if="
                    task.workflow_image_url !== undefined &&
                    task.workflow_image_url !== null
                "
                rounded
                class="card-img-right"
                style="
                    max-width: 5rem;
                    position: absolute;
                    right: -15px;
                    top: -20px;
                    z-index: 1;
                "
                right
                :src="task.workflow_image_url"
            ></b-img>
            <i class="fas fa-coffee fa-fw"> </i>
            DUE
            {{ prettify(task.eta) }}
            <br />
            <small v-if="task.workflow_name !== null" class="mr-1 mb-0"
                ><a
                    :class="profile.darkMode ? 'text-light' : 'text-dark'"
                    :href="`https://github.com/${task.workflow_owner}/${task.workflow_name}`"
                    ><i class="fab fa-github fa-fw"></i>
                    {{ task.workflow_owner }}/{{ task.workflow_name }}</a
                >
            </small>
        </b-card-body>
        <b-button
            size="sm"
            @click="deleteRepeating(task.name)"
            variant="outline-danger"
            class="text-right"
            ><i class="fas fa-times text-danger fa-fw"></i> Unschedule</b-button
        >
    </b-card>
</template>

<script>
import { guid } from '@/utils';
import { mapGetters } from 'vuex';
import * as Sentry from '@sentry/browser';
import moment from 'moment';
import axios from 'axios';

export default {
    name: 'repeating-task-blurb',
    props: {
        task: {
            required: true,
        },
    },
    computed: {
        ...mapGetters('user', ['profile']),
    },
    methods: {
        prettify: function (date) {
            return `${moment(date).fromNow()} (${moment(date).format(
                'MMMM Do YYYY, h:mm a'
            )})`;
        },
        async deleteRepeating(id) {
            this.unschedulingRepeating = true;
            await axios
                .get(
                    `/apis/v1/tasks/${id}/unschedule_repeating/`
                )
                .then(async (response) => {
                    await Promise.all([
                        this.$store.dispatch(
                            'tasks/setRepeating',
                            response.data.tasks
                        ),
                        this.$store.dispatch('alerts/add', {
                            variant: 'success',
                            message: `Unscheduled repeating task`,
                            guid: guid().toString(),
                        }),
                    ]);
                    this.unschedulingRepeating = false;
                })
                .catch(async (error) => {
                    Sentry.captureException(error);
                    await this.$store.dispatch('alerts/add', {
                        variant: 'danger',
                        message: `Failed to unschedule repeating task`,
                        guid: guid().toString(),
                    });
                    this.unschedulingRepeating = false;
                    throw error;
                });
        },
    },
};
</script>

<style scoped></style>
