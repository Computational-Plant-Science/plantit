import API from '@/utils';

class ObservationUnitsAPI extends API {
    constructor() {
        super();
        this.url = '/apis/v1/miappe/observation_units';
    }
}

const api = new ObservationUnitsAPI();

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
