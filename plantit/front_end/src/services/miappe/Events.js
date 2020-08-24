import API from '@/utils';

class EventsAPI extends API {
    constructor() {
        super();
        this.url = '/apis/v1/miappe/events';
    }
}

const api = new EventsAPI();

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
