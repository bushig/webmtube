import {MAX_SIZE} from './config'

// Function to get absolute url from relative
function qualifyURL(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.href;
}
// Создаем панель если ее нет и в ней размещаем всю информацию
function setWEBMPanel({node, screamChance, views, likes, dislikes, message} ={}) { // использовать | как сепаратор + добавить подсветку превью на ховер
    let panel = node.querySelector('figcaption > .webm-panel');
    if (panel === null) {
        panel = document.createElement('div');
        panel.className = 'webm-panel';
        const figcaption = node.querySelector('figcaption');
        figcaption.insertBefore(panel, figcaption.children[1]);
    }
    if (screamChance !== undefined) {
        setScreamColor(node, panel, screamChance);
    }
    if (views !== undefined) {
        setViews(panel, views);
    }
    if (likes !== undefined) {
        // setLikes(panel, likes)
    }
    if (dislikes !== undefined) {
        // setDislikes(panel, dislikes);
    }
    if (message !== undefined) {
        setMessage(panel, message);
    }

}

function setViews(panel, views) {
    let views_elem = panel.querySelector('span.views');
    if (views_elem === null) {
        views_elem = document.createElement('span');
        views_elem.className = 'views';

        createIcon(views_elem, 'eye');

        panel.appendChild(views_elem);
    }
    const text = document.createTextNode(views);
    views_elem.appendChild(text);
}
//Sets message of webm, accepts webm-panel selector and text
function setMessage(panel, text) {
    var message = panel.querySelector('span.message');
    if (message === null) {
        message = document.createElement('span');
        message.className = 'message';
        panel.appendChild(message);
    }
    message.innerText = text;
    if (text === null) {
        message.remove()
    }
}

// Отвечает за увеличение счетчика просмотров
function setViewListener(node, md5) {
    var img = node.querySelector('img.preview');
    img.addEventListener('click', function increaseViewsListener(event) {
        event.target.removeEventListener('click', increaseViewsListener);
        var request = new Request(`https://devshaft.ru/check/${md5}/view`, {
            method: 'GET',
            mode: 'cors'
        });
        fetch(request);
    });
}

// Красит элемент в нужный цвет в зависимости от шанса скримера
function setScreamColor(node, panel, screamChance) {
    var scream = panel.querySelector('span.scream');
    if (scream === null) {
        scream = document.createElement('span');
        scream.className = 'scream';
        panel.appendChild(scream);
    }
    const img = node.querySelector('.webm-file');
    if (screamChance == null) {
        img.className += 'blue-shadow ';
        scream.style.background = '#3DBFFF';
        createIcon(scream, 'volume-mute');
    } else if (screamChance == 0) {
        img.className += 'green-shadow ';
        scream.style.background = '#45D754';
        createIcon(scream, 'volume-low');
    } else if (screamChance == 0.5) {
        img.className += 'yellow-shadow ';
        scream.style.background = 'yellow';
        createIcon(scream, 'volume-medium');
    } else if (screamChance == 0.8) {
        img.className += 'orange-shadow ';
        scream.style.background = 'orange';
        createIcon(scream, 'volume-high');
    } else if (screamChance == 1.0) {
        img.className += 'red-shadow ';
        scream.style.background = 'red';
        createIcon(scream, 'volume-scream');
    }
}
function createIcon(node, name) {
    let icon = node.querySelector('img');
    if (icon === null) {
        icon = document.createElement('img');
        icon.className = 'glyphicon';
        node.appendChild(icon);
    }
    icon.setAttribute('src', chrome.runtime.getURL('icons/' + name + '.svg'));
}
// В зависимости от полученных с сервера данных обрабатывает посты в треде
// data - объект с данными одной webm
function parseData(data) {
    var md5 = data.md5;
    window.webm_data[md5].data = data;
    var nodes = window.webm_data[md5].elems;
    // if(nodes.length>1){
    //     console.log(nodes);
    // }
    nodes.forEach((node_info, index)=> {
        const node = node_info.node;
        const processed = node_info.processed;
        // Обрабатываем только новые ноды
        if (!processed) {
            window.webm_data[md5].elems[index].processed = true;
            if (data.message) {
                console.log(data.message);
                setWEBMPanel({node, message: data.message});
                node.addEventListener('mouseenter', function OneWEBMListener(event) {
                    event.target.removeEventListener('mouseenter', OneWEBMListener);
                    setTimeout(getOneWEBMData, 5000, node);
                })
            } else {
                var screamChance = data["screamer_chance"];
                setWEBMPanel({node, screamChance: screamChance, views: data.views, message: null});
                setViewListener(node, data.md5);
            }
        }
    })
}

// Получить данный об одной вебм с сервера через get запрос и затем нужные элементы
// node - figure.image селектор
function getOneWEBMData(node) {
    var div = node.querySelector('div.image-link');
    var a = div.querySelector('a');
    var md5 = div.id.split('-').pop();
    var url = encodeURIComponent(qualifyURL(a.getAttribute('href')));
    var request = new Request(`https://devshaft.ru/check?md5=${md5}&url=${url}`, {
        method: 'GET',
        mode: 'cors'
    });
    fetch(request).then(function (resp) {
        return resp.json()
    }).then(function (json) {
        parseData(json);
    })
}

// Получить данный о нескольких вебм с сервера через POST запрос и затем подсветить нужные элементы
function getAllWEBMData(nodes) {
    var data = []; // Данные которые отправляем на сервер

    nodes.forEach(function (node) {
        var div = node.querySelector('div');
        var a = div.querySelector('a');
        if (a.getAttribute('href').slice(-5) == ".webm") {
            var size = parseInt(node.querySelector('figcaption.file-attr > span.filesize').innerText.substring(1, 30).split(',')[0]);
            var md5 = div.id.split('-').pop();
            var url = qualifyURL(a.getAttribute('href'));
            var webm = {md5: md5, url: url};
            if (size < MAX_SIZE) {
                if (window.webm_data[md5] === undefined) {
                    window.webm_data[md5] = {elems: [], data: {}};
                }
                // Добавляем флаг processed чтобы по два раза не обрабатывать одни и те же ноды.
                window.webm_data[md5].elems.push({node: node, processed: false});
                data.push(webm);
            } else {
                setWEBMPanel({node, message: 'Слишком большой размер'})
            }
        }
    });
    // Если нет ничего нового, то останавливаем функцию
    if (data.length === 0) {
        return
    }
    var requestHeader = new Headers();
    requestHeader.append('Content-Type', 'application/json');
    requestHeader.append('Accept', 'application/json');
    var request = new Request('https://devshaft.ru/check', {
        method: 'POST',
        headers: requestHeader,
        mode: 'cors',
        body: JSON.stringify(data)
    });
    fetch(request).then(function (resp) {
        console.log(resp);
        return resp.json()
    }).then(function (json) {
        json.forEach(function (data) {
            parseData(data);
        })
    })
}

module.exports = {getOneWEBMData, getAllWEBMData};
