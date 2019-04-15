<template>
    <div style="text-align:center">
        <PageNavigation>
            <template v-slot:page-nav>
                <b-nav-item to="/user/collections">Collections</b-nav-item>
                <b-nav-item to="/user/dashboard">Dashboard</b-nav-item>
                <b-nav-item to="/user/jobs">Jobs</b-nav-item>
            </template>
            <template v-slot:buttons>
            </template>
        </PageNavigation>

        <h1> Choose a Workflow </h1>

        <b-form-group label-cols-sm="2" label="Filter" style="width: 400px">
            <b-input-group>
                <b-form-input
                    v-model="filter_query"
                    placeholder="Type to Filter"
                ></b-form-input>
                <b-input-group-append>
                    <b-button
                        :disabled="!filter_query"
                        @click="filter_query = ''"
                        >Clear</b-button
                    >
                </b-input-group-append>
            </b-input-group>
        </b-form-group>

         <div class="d-flex flex-wrap justify-content-center align-items-stretch row-eq-height">
            <div
              v-for="workflow in filtered"
              class="p-3 m-3 workflow"
            >
              <div class="workflow-icon">
                <b-img :src="workflow.icon_url"></b-img>
              </div>
              <div class="workflow-text">
                <b-link :to="{name: 'submit_workflow', query: { job_pk: pk, workflow_pk: workflow.pk }}"> {{workflow.name}} </b-link>
                <hr>
                {{workflow.description}}
              </div>
            </div>
          </div>
    </div>
</template>

<script>
import PageNavigation from '@/components/PageNavigation.vue';

export default {
    name: 'Analyze',
    components: {
      PageNavigation
    },
    props:{
      pk:{
        // the pk of the collection to analyze
        required: true
      },
    },
    data: function () {
      return{
        // The text to filter the shown workflow by.
        filter_query: "",

        //Available workflows.
        workflows:[
          {
            name: "DIRT2D",
            description: "A cool description",
            icon_url: require('../assets/logo.png'),
            pk: 1
          },
          {
            name: "Workflow 2",
            description: "A cool description",
            icon_url: require('../assets/logo.png'),
            pk: 2
          },
          {
            name: "Workflow 3",
            description: "A cool and very long description that tests how well the text wwraps",
            icon_url: require('../assets/logo.png'),
            pk: 3
          },
          {
            name: "Workflow 4",
            description: "A cool, but different, description",
            icon_url: require('../assets/logo.png'),
            pk: 4
          }
        ]
      }
    },
    computed:{
      filter_text: function(){
        /*
          returns (str): filter_query converted to all lower case
        */
        return this.filter_query.toLowerCase()
      },
      filtered: function(){
        /*
          returns: An array of workflow objects that include the f
            ilter_query text in their name or description
        */
        if(this.filter_text == ""){
          return this.workflows
        }else{
          return this.workflows.filter((w) => {
             return w.name.toLowerCase().includes(this.filter_text) ||
                      w.description.toLowerCase().includes(this.filter_text)
          })
        }
      }
    }
};
</script>

<style scoped lang="sass">
@import "../scss/_colors.sass"

.workflow
  width: 300px

.workflow-icon
  width: 200px
  height: 200px
  margin: 0 auto
  margin-bottom: -10px
  background-color: $color-disabled
  border-radius: 50%
  padding: 10px

  img
    max-width: 100px
    max-height: 190px

.workflow-text
  background-color: $color-box-background
  padding: 10px

</style>
