import {increaseViews} from './common'

function getDollchanAPI() {
    return new Promise((resolve, reject) => {
        const dw = document.defaultView;
        const onmessage = ({data, ports}) => {
            if (ports && ports.length === 1 && data === 'de-answer-api-message') {
                clearTimeout(to);
                dw.removeEventListener('message', onmessage);
                resolve(ports[0]);
            }
        };
        dw.addEventListener('message', onmessage);
        dw.postMessage('de-request-api-message', '*');
        const to = setTimeout(() => {
            dw.removeEventListener('message', onmessage);
            reject();
        }, 5e3);
    });
}

function runAPI() {
    getDollchanAPI().then(port => {
        port.onmessage = ({data}) => {
            switch (data.name) {
                case 'registerapi':
                    for (let key in data.data) {
                        console.log(`API ${ key } ${
                            data.data[key] ? 'зарегистрирован' : 'недоступен' }.`);
                    }
                    break;
                case 'expandmedia':
                    const src = data.data;
                    const ext = src.split('.').pop();
                    // console.log(ext + ' открыт:', src);
                    if (ext === 'webm') {
                        const aElem = document.querySelector(`a[href="${ src }"]`);
                        const md5 = aElem.getAttribute('id').split('-').pop(-1);
                        const currViewed = window.webm_data[md5].data.currViewed;
                        const id = window.webm_data[md5].data.id;
                        // console.log(md5);
                        if (currViewed !== true) {
                            // Увеличиваем счетчик только если не просмотрено в данной сессии
                            increaseViews(md5, id);
                        }
                    }
                    break;
                /* case '...': */
            }
        };
        port.postMessage({name: 'registerapi', data: ['expandmedia']});
        /* port.postMessage({ name: 'registerapi', data: ['...'] }); */
    }).catch(() => console.log('Старая версия куклы без поддержки API.'));
}

module.exports = runAPI;