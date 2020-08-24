import API from '@/utils';

class BiologicalMaterialsAPI extends API {
    constructor() {
        super();
        this.url = '/apis/v1/miappe/biological_materials'
    }
}

const api = new BiologicalMaterialsAPI();

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