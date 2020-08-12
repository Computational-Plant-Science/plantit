import axios from 'axios';
import * as Sentry from '@sentry/browser';

export default {
    getCurrentRelease() {
        return axios
            .get(
                'https://api.github.com/repos/Computational-Plant-Science/plantit/releases',
                { headers: { Accept: 'application/vnd.github.v3+json' } }
            )
            .then(response => {
                return response.data[0].tag_name;
            })
            .catch(err => {
                Sentry.captureException(err);
            });
    }
};
