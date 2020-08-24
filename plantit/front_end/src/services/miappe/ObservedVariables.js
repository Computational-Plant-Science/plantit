import API from '@/utils';

class ObservedVariablesAPI extends API {
    constructor() {
        super();
        this.url = '/apis/v1/miappe/observed_variables';
    }
}

const api = new ObservedVariablesAPI();

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
