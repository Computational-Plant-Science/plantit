import API from '@/utils';

class EnvironmentParametersAPI extends API {
    constructor() {
        super();
        this.url = '/apis/v1/miappe/environment_parameters';
    }
}

const api = new EnvironmentParametersAPI();

export default {
    list() {
        return api.list();
    },
    create(data) {
        return api.create(data);
    },
    update(pk, data) {
        return api.update(pk, data);
    },
    get(pk) {
        return api.get(pk);
    },
    delete(pk) {
        return api.delete(pk);
    }
};
