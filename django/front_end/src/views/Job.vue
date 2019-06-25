<template>
    <div>
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
            </template>
        </PageNavigation>
        <b-container>
            <b-row>
                <b-col>
                    <h1>Job ID: {{ this.$route.query.pk }}</h1>
                    <h3>Collection: {{ this.job.collection }}</h3>
                </b-col>
                <b-col cols="5">
                    <b>Current Status:</b> {{ job.current_status }}<br />
                    <b>Submission ID:</b> {{ job.submission_id }}<br />
                    <b>Work DIR:</b> {{ job.work_dir }}<br />
                    <b>Created:</b> {{ job.date_created | format_date }}<br />
                </b-col>
            </b-row>
            <b-row>
                <b-col class="content-box text-center p-5">
                    <b-img
                        v-if="job.remote_results_path == null"
                        :src="require('../assets/PlantITLoading.gif')"
                        width="250%"
                        alt="Plant IT"
                    ></b-img>
                    <b-link v-else :href="job | resultsLink">
                        <b-img
                            :src="require('../assets/icons/download.png')"
                            width="250%"
                            alt="Download"
                        ></b-img>
                    </b-link>
                    <DiscreteProgress
                        style="padding: 20px 15% 10px 15%;"
                        :tasks="job.task_set"
                    ></DiscreteProgress>

                    <b-table
                      id="error-log"
                      striped
                      borderless
                      responsive="lg"
                      :items="job.status_set"
                      :fields="status_table.fields"
                      :per-page="status_table.perPage"
                      :sort-by.sync="status_table.sortBy"
                      :sort-desc.sync="status_table.sortDesc"
                      >
                      <span
                        slot="description"
                        slot-scope="data"
                        v-html="data.value"
                        class="align-left"></span>
                    </b-table>
                    <div id="error-count" >
                      <span v-if="error_count > 0">
                        There are {{ error_count }} warning(s) / error(s):
                      </span>
                      <b-button @click="status_table.perPage = status_table.perPage ? null : 1">
                         {{ status_table.perPage ? 'Show' : 'Hide'}} Log
                      </b-button>
                    </div>
                </b-col>
            </b-row>
        </b-container>
    </div>
</template>

<script>
import PageNavigation from '@/components/PageNavigation.vue';
import DiscreteProgress from '@/components/DiscreteProgress.vue';
import JobApi from '@/services/apiV1/JobManager.js';
import moment from 'moment';

export default {
    name: 'Job',
    components: {
        PageNavigation,
        DiscreteProgress
    },
    data() {
        return {
            job: {
                pk: this.$route.query.pk,
                collection: 'NULL',
                current_status: 'NULL',
                submission_id: 'NULL',
                work_dir: 'NULL',
                auth_token: 'NULL',
                remote_results_path: null,
                task_set: [],
                status_set: []
            },
            status_table: {
              sortBy: 'date',
              sortDesc: true,
              perPage: 1,
              fields: [
                {
                  key: 'date',
                  label: 'Time',
                  sortable: true,
                  formatter: value => {
                    return moment(value).format('MM/DD/YY HH:mm')
                  }
                },
                {
                  key: 'state',
                  label: 'State',
                  formatter: value => {
                    switch(value){
                      case 1:
                        return "Completed"
                        break;
                      case 2:
                        return "Failed"
                        break;
                      case 3:
                        return "OK"
                        break;
                      case 4:
                        return "Warning"
                        break;
                      case 5:
                        return "Created"
                        break;
                    }
                  }
                },
                {
                  key: 'description',
                  formatter: value => {
                    return value.replace(/(?:\r\n|\r|\n)/g, '<br>')
                  },
                  tdClass: 'table-td'
                }

              ]
            }
        };
    },
    mounted: function() {
        JobApi.getJob(this.job.pk).then(data => {
            this.job = data;
        });
    },
    computed: {
        current_status() {
            if (this.job.status_set.length > 0) {
                return this.job.status_set[0].description;
            } else {
                return '';
            }
        },
        error_count(){
          return this.job.status_set.filter(status =>{
            return status.state == 2 | status.state == 4
          }).length
        }
    },
    filters: {
        format_date(value) {
            return moment(value).format('MM/DD/YY HH:mm');
        },
        resultsLink(job) {
            return JobApi.resultsLink(job.pk);
        }
    }
};
</script scoped>

<style>
.table-td {
  text-align: left;
}

#error-log > thead {
    display:none !important;
}

#error-count {
  padding-top: 10 px;
  float: right;
}
</style>
