import axios from 'axios'

export default {
   getStorageTypes() {
    /**
     * Get Available stroage types.
     *
     * Returns:
     *    Axios promise containing returning an array of storage types
     **/
    return axios.post("/apis/v1/files/")
    .then((response) => {return response.data.storage_types})
    .catch(function (error) {
      console.log("Error: " + error);
    })
  },
}
