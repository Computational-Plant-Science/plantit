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

  listDir(dir,storage_type) {
    /**
     * List folder contents in the format required by
     * jsTree  (https://www.jstree.com/docs/json/)
     *
     * Requirements:
     *   User must be logged in
     *   User must have permission to access dir
     *
     * Args:
     *    dir (str): path of directory to list,
     *    storage_type (str): The storage system to access
     **/
     return axios.get(`/apis/v1/files/lsdir/`,{
       params:{
         'path': dir,
         'storage_type': storage_type
       }
     }).then((response) => {return response.data})
     .catch((error) => {console.log(error)})
  }
}
