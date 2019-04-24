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
  }
}
