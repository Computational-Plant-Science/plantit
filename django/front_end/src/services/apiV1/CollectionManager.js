import axios from 'axios'

export default {
   newCollection(name,desc,storageType,basePath) {
    /**
     * Create a new collection
     *
     * Args:
     *    name (str): name of the collection
     *    description (str): Collection description
     *    storageType (str): Storage system that the
     *         collection samples are save on
     *    basePath (str): The base folder in which the samples are
     *         saved on storageType
     *
     * Returns:
     *    Axios promise containing the server response
     **/
    return axios.post("/apis/v1/collections/",{
      storage_type: storageType,
      base_file_path: basePath,
      name: name,
      description: desc,
    })
    .then((response) => {return response })
    .catch(function (error) {
      console.log("Error: " + error);
    })
  },

  getCollectionList(){
    /**
     * Get a list of collections for the current user.
     *
     * Requirements:
     *   User must be logged in
     *
     * Returns:
     *    Axios promise containing the user's collections in an array
     **/
    return axios.get("/apis/v1/collections/")
    .then((response) => { return response.data })
  }
}
