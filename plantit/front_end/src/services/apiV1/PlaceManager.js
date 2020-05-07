import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    searchInstitution(name) {
        /**
         * Search for an institution by name.
         *
         * Requirements:
         *   User must be logged in
         *
         * Returns:
         *    Axios promise containing the search results
         **/
        return axios
            .get(
                encodeURI(
                    `https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=${name}&inputtype=textquery&fields=name&key=AIzaSyChHaZfwFcVigXg_T8DfDI5tqUP8QQJE88`
                )
            )
            .then(response => {
                return response.candidates;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
