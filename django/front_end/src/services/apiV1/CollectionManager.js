import axios from 'axios'

export default {
   newCollection(name,desc,storageType,metadata,basePath) {
    /**
     * Create a new collection
     *
     * Requirements:
     *   User must be logged in
     *
     * Args:
     *    name (str): name of the collection
     *    description (str): Collection description
     *    storageType (str): Storage system that the
     *         collection samples are save on
     *    metadata (Array of obects): Collection metadata
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
      metadata: metadata,
      description: desc,
    })
    .then((response) => {return response })
    .catch(function (error) {
      console.log("Error: " + error);
    })
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
     let url = (pinned ? `/apis/v1/collections/${pk}/pin/` : `/apis/v1/collections/${pk}/unpin/`)
     return axios.post(url)
      .then((response) => {
        return response.status == 200
      }).catch(error => {
        console.log(error)
        return false
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
  },

  getCollection(pk){
    /**
     * Get a collection.
     *
     * Requirements:
     *   User must be logged in
     *
     * Returns:
     *    Axios promise containing the collection object
     **/
    return axios.get(`/apis/v1/collections/${pk}/` )
    .then((response) => { return response.data })
  },

  deleteCollection(pk){
    /**
     * Delete a collection.
     *
     * Args:
     *   pk (int): collection pk
     *
     * Requirements:
     *   User must be logged in
     *
     * Returns:
     *    Axios promise containing true if the delete was sucessful,
     *    false otherwise
     **/
     return axios.delete(`/apis/v1/collections/${pk}/` )
     .then((response) => {
       return response.status == 204
     }).catch(error => {
       console.log("Error :" + error)
       return false
     })
  },

  addSample(sample, pk){
    /**
      Add sample to the collection

      Args:
        sample (json): sample info:
          {
            name: "name of sample",
            path: "path to sample"
          }
        pk (int): collection pk

      Requires:
        User is logged in and has permission for collection

      Returns:
        axios.patch promise
    **/
    return this.addSamples([sample], pk)
  },

  addSamples(samples, pk){
    /**
      Add sample to the collection

      Args:
        sample (array of json): sample info:
          [
            {
            name: "name of sample",
            path: "path to sample"
          },
          ....
        ]
        pk (int): collection pk

      Requires:
        User is logged in and has permission for collection

      Returns:
        axios.patch promise
    **/
    const data = {
      sample_set: samples
    }
    return axios.patch(`/apis/v1/collections/${pk}/`, data)
  },

  updateSample(sample){
    /**
      Update the sample list. This overwrites the collection sample list
      with the the one give here.

      Args:
        sample (array of json): sample info:
          [
            {
            name: "name of sample",
            path: "path to sample"
          },
          ....
        ]
        pk (int): collection pk

      Requires:
        User is logged in and has permission for collection

      Returns:
        axios.patch promise
    **/
    return axios.patch(`/apis/v1/samples/${sample.pk}/`, sample)
  },

  getSample(pk){
    /**
      Get a single sample

      Args:
        pk (int): sample pk

      Requires:
        User is logged in and has permission for collection

      Returns:
        axios.patch promise returning the sample object
    **/
    return axios.get(`/apis/v1/samples/${pk}/` )
    .then((response) => { return response.data })
  },

  deleteSample(pk){
    /**
      Delete a sample

      Args:
        pk (int): sample pk

      Requires:
        User is logged in and has permission for collection

      Returns:
       Axios promise returning true if the delete was sucessful,
       false otherwise
    **/
    return axios.delete(`/apis/v1/samples/${pk}/` )
    .then((response) => {
      return response.status == 204
    }).catch(error => {
      console.log("Error :" + error)
      return false
    })
  },

  updateMetadata(name,description,metadata,pk){
    /**
      Update (overwrite) the collection metadata, name, and description.
      The collection with the give pk will have its metadata, name,
      and description overwritten wtih the values passed.

      Args:
        name (string): Collection Name
        description (string): Collection Description
        metadata (array): An array of metadata fields. sample metadtata:
          [
            {
            name: "name of field",
            value: "value of field"
          },
          ....
         ]
        pk (int): collection pk

      Requires:
        User is logged in and has permission for collection

      Returns:
        axios.patch promise
    **/
    const data = {
      name: name,
      description: description,
      metadata: metadata
    }
    return axios.patch(`/apis/v1/collections/${pk}/`, data)
  }
}
