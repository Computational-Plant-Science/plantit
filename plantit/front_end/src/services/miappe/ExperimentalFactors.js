import API from '@/utils';

class ExperimentalFactorsAPI extends API {
    constructor() {
        super();
        this.url = '/apis/v1/miappe/experimental_factors';
    }
}

const api = new ExperimentalFactorsAPI();

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
