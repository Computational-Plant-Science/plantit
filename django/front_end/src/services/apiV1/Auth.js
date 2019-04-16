import axios from 'axios'

export default {
   login(username, password) {
    /**
     * Login the current session.
     *
     * Args:
     *    username (str): username
     *    password (str): password
     *
     * Returns:
     *    Axios promise containing the server response
     **/
    return axios.post("/apis/v1/auth/login/", {
      username: username,
      password: password
    })
    .then((response) => {return response})
    .catch(function (error) {
      console.log("Error: " + error);
    })
  },

  logout() {
    /**
     * Logout the current session.
     *
     * Returns:
     *    Axios promise containing the server response 
     **/
    return axios.get("/apis/v1/auth/logout/")
    .then((response) => { return response })
    .catch(function (error) {
      console.log(error);
    })
  }
}
