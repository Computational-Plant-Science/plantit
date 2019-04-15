import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = '/api'

/**
 * Set the CSRF Token
 * https://docs.djangoproject.com/en/1.10/ref/csrf/#ajax
 */
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.withCredentials = true

function getCSRFToken(){
  return Cookies.get(axios.defaults.xsrfCookieName)
}

class Collection{

  static addSample(sample, pk){
    /**
      Add sample to the collection

      Args:
        sample (json): sample info:
          {
            name: "name of sample",
            path: "path to sample"
          }
      Returns:
        axios.patch promise
    **/
    return this.addSamples([sample], pk)
  }

  static addSamples(samples, pk){
    /**
      Add sample to tje collection

      Args:
        sample (array of json): sample info:
          [
            {
            name: "name of sample",
            path: "path to sample"
          },
          ....
        ]

      Returns:
        axios.patch promise
    **/
    const url = `${API_URL}/collections/${pk}/`
    const data = {
      sample_set: samples
    }
    return axios.patch(url, data)
  }

}

class Files{
  static uploadURL(storage_type){
    return `${API_URL}/files/${storage_type}/upload`
  }

  static listDir(path,storage_type){
    /**
      Get a list of files in a directory

      Args:
        path (str): path of directory
        storage_type (str): underlying storage type

      Returns (Promise): List of files in the directory
     **/
    return axios.get(`/api/files/${storage_type}`, {
      params: {
        path: path
      }
    }).then(response => {
      return response.data
    })
  }
}

export { Collection, Files, getCSRFToken }
