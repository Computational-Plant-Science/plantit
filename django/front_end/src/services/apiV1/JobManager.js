import axios from 'axios'

export default {

  getJobList(){
    /**
     * Get a list of jobs for the current user.
     *
     * Requirements:
     *   User must be logged in
     *
     * Returns:
     *    Axios promise containing the user's jobs in an array
     **/
    return axios.get("/apis/v1/jobs/")
    .then((response) => { return response.data })
  },

  pin(pk,pinned){
    /**
     * Pin or unpin the job to the user profile
     *
     * Args:
     *    pk (int): job pk
     *    pinned (bool): pinned state
     *
     * Requirements:
     *    User must be logged in
     *
     * Returns:
     *    Promise returning True if the pin was sucessfully added,
     *    False otherwise
     **/
     let url = (pinned ? `/apis/v1/jobs/${pk}/pin/` : `/apis/v1/jobs/${pk}/unpin/`)
     return axios.post(url)
      .then((response) => {
        return response.status == 200
      }).catch(error => {
        console.log(error)
        return false
      })
  },

  getJob(pk){
    /**
     * Get a jobs.
     *
     * Requirements:
     *   User must be logged in
     *
     * Returns:
     *    Axios promise containing the job object
     **/
    return axios.get(`/apis/v1/jobs/${pk}/` )
    .then((response) => { return response.data })
  },

  resultsLink(pk){
    /**
     * Returns the download link for the results for the given job
     *
     * Args:
     *   pk (int): pk of job
     *
     * Requirements:
     *   User must be logged in
     *
     * Returns (str):
     *   url to download job results
     */
     return `/apis/v1/jobs/${pk}/download_results/`
  }
}
