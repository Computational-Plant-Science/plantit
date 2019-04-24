import axios from 'axios'

function pathJoin(parts){
  /**
   * Joins names into a valid file path
   *
   * Args:
   *   parts (Array of strings): Names to join into a path.
   *
   * Returns:
   *   A string containing each element in parts with a single / between them.
   *   extra /s in the elements of parts are removed
   **/
   var replace   = new RegExp('/'+'{1,}', 'g');
   return parts.join('/').replace(replace, '/');
}

export default {
   getWorkflows() {
    /**
     * Get Available stroage types.
     *
     * Returns:
     *    Axios promise containing returning an array of workflow objects
     **/
    return axios.get("/apis/v1/workflows/")
    .then((response) => {return response.data.workflows})
    .catch(function (error) {
      console.log("Error: " + error);
    })
  },

  getParameters(workflow) {
   /**
    * Get workflow paramaters
    *
    * Args:
    *   workflow (str): app_name of workflow
    *
    * Returns:
    *    Axios promise containing returning the parameters
    **/
   return axios.get(`/apis/v1/workflows/${workflow}/`)
   .then((response) => {return response.data.parameters})
   .catch(function (error) {
     console.log("Error: " + error);
   })
 },

 submitJob(workflow,pk,params){
   console.log(params)
   return axios.post(`/apis/v1/workflows/${workflow}/submit/${pk}/`, params)
   .then((response) => {return response})
   .catch(function (error) {
     console.log("Error: " + error);
   })
 }

}
