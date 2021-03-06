import {MAX_SIZE, DEFAULT_SETTINGS} from './config'
let moment = require('moment');
moment.locale('ru');
// Полифил чтобы работал Firefox
// global.browser = global.chrome;

let settings = browser.storage.local.get(DEFAULT_SETTINGS).then((items) => {
    console.log(items);
    settings = items;
});

// Function to get absolute url from relative
function qualifyURL(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.href;
}
// При наведении должен делаться  запрос на сервер
function OneWEBMListener(event) {
    event.target.removeEventListener('mouseenter', OneWEBMListener);
    const node = event.target;
    let time = event.target.time;

    if (time === undefined) {
        event.target.time = 4;
        time = 0;
    }

    function checkTime() {
        if (time > 0) {
            setWEBMPanel({node: node, message: "Секунд до обновления: " + time});
            time--;
            // event.target.time = time;
        } else {
            clearInterval(intervID);
            event.target.time = 4;
            getOneWEBMData(node);
        }
    }

    // При первом наведении делать запрос, далее добавить таймер
    const intervID = setInterval(checkTime, 1000);
    checkTime();

}

function increaseViews(md5, id) {
    // Наъуй мозиллу и промисы
    // Проверяем просмотрен ли ролик
    let infoPromise = browser.storage.local.get(id);

    let dataPromise = browser.storage.local.get({'views': 0, 'uniqueViews': 0});
    Promise.all([infoPromise, dataPromise]).then((values) => {
        let info = values[0];
        let data = values[1];
        let viewsCount = data['views'] + 1;// Увеличиваем даже если до этого были просмотры.
        let uniqueViewsCount = data['uniqueViews']; // Уникальные просмотры
        let obj = info[id];
        // Еще нет данных или еще не просмотрен
        if (obj === undefined) {
            uniqueViewsCount++;
            obj = {};
            obj.viewed = true;
        } else if (obj.viewed !== true) {
            obj.viewed = true;
        }
        let req = {};
        req[id] = obj;
        browser.storage.local.set(req);
        browser.storage.local.set({'views': viewsCount, 'uniqueViews': uniqueViewsCount});
        return id;
    }).then((id) => {
        console.log('Удачный просмотр: ', id);
        let webmData = window.webm_data[md5].data;
        console.log(webmData);
        Object.assign(window.webm_data[md5].data, {
            views: parseInt(webmData.views) + 1,
            currViewed: true
        });
        parseData(window.webm_data[md5].data, true);
    });

    let requestHeader = new Headers();
    requestHeader.append('Content-Type', 'application/json');
    requestHeader.append('Accept', 'application/json');

    var request = new Request(`https://devshaft.ru/check/${md5}/view`, {
        headers: requestHeader,
        method: 'POST',
        mode: 'cors'
    });
    fetch(request);
}
function increaseViewsListener(event) {
    event.currentTarget.removeEventListener('click', increaseViewsListener);
    const md5 = event.currentTarget.md5;
    const id = event.currentTarget.id;
    if (md5 === undefined || id === undefined) {
        console.log('Не удалось повесить счетчик просмотров на: ', event.currentTarget);
        console.log(md5, event.currentTarget);
    }
    increaseViews(md5, id)
}

// Создаем панель если ее нет и в ней размещаем всю информацию
function setWEBMPanel({node, md5, id, screamChance, views, likes, dislikes, action, message, viewed, date} ={}) { // использовать | как сепаратор + добавить подсветку превью на ховер
    let panel = node.querySelector('figcaption > .webm-panel');
    if (panel === null) {
        panel = document.createElement('div');
        panel.className = 'webm-panel';
        const figcaption = node.querySelector('figcaption');
        figcaption.insertBefore(panel, figcaption.children[1]);
    }
    if (screamChance !== undefined) {
        setScreamColor(node, panel, screamChance, date);
    }
    if (views !== undefined) {
        setViews(panel, views, viewed);
    }
    if (likes !== undefined && dislikes !== undefined) {
        setLikesPanel(panel, md5, id, likes, dislikes, action)
    }
    if (message !== undefined) {
        setMessage(panel, message);
    }
}

function setLikesPanel(panel, md5, id, likes, dislikes, action = null) {
    let ratingPanel = panel.querySelector('span.rating');
    if (ratingPanel === null) {
        ratingPanel = document.createElement('span');
        ratingPanel.className = 'rating';
        panel.appendChild(ratingPanel);

        let likesSpan = document.createElement('span');
        createLikeIcon(likesSpan, 'like', action);
        let likeCounter = document.createTextNode(likes);
        likesSpan.appendChild(likeCounter);
        ratingPanel.appendChild(likesSpan);
        setLikesListener(likesSpan.childNodes[0], md5, id, 'like');

        let dislikesSpan = document.createElement('span');
        createLikeIcon(dislikesSpan, 'dislike', action);
        let dislikeCounter = document.createTextNode(dislikes);
        dislikesSpan.appendChild(dislikeCounter);
        ratingPanel.appendChild(dislikesSpan);
        setLikesListener(dislikesSpan.childNodes[0], md5, id, 'dislike');
    } else {
        let [likesSpan, dislikesSpan] = ratingPanel.querySelectorAll('span');

        createLikeIcon(likesSpan, 'like', action);
        likesSpan.childNodes[1].nodeValue = likes;

        createLikeIcon(dislikesSpan, 'dislike', action);
        dislikesSpan.childNodes[1].nodeValue = dislikes;
    }

}

// Отвечает за отправку запроса на сервер(лайки и дизлайки) и установку новых иконок и счетчика лайков
// TODO: Проверить убираются ли EventListeners сборщиком мусора при замене иконок
function setLikesListener(node, md5, id, action_type) {
    // Мозилла пiдоры
    node.addEventListener('click', (event) => {
        let requestHeader = new Headers();
        requestHeader.append('Content-Type', 'application/json');
        requestHeader.append('Accept', 'application/json');
        let request = new Request(`https://devshaft.ru/check/${md5}/${action_type}`, {
            headers: requestHeader,
            method: 'POST',
            mode: 'cors'
        });
        fetch(request).then((resp)=> {
            return resp.json()
        }).then((data) => {
            console.log("Likes data:", data);
            Object.assign(window.webm_data[md5].data, data); //DANGER!
            let action = data.action;
            let obj = {};
            obj[id] = {action: null}; // Стандатные значения для запроса
            // Данные из хранилища
            let storeDataPromise = browser.storage.local.get(obj);
            // Количество лайков из хранилища
            let likesDataPromise = browser.storage.local.get({likes: 0, dislikes: 0});
            Promise.all([storeDataPromise, likesDataPromise]).then((values) => {
                let storeData = values[0];
                let likesData = values[1];
                let likes = likesData.likes;
                let dislikes = likesData.dislikes;
                // console.log(storeData[md5].action, action);
                // Если одинаковый action
                if (storeData[id].action === action) {
                    // Nothing
                    // Разный action и не равен null
                } else if (storeData[id].action !== action && storeData[id].action !== null && action !== null) {
                    if (storeData[id].action === 'like') {
                        likes--;
                        dislikes++;
                    } else if (storeData[id].action === 'dislike') {
                        likes++;
                        dislikes--;
                    }
                    // Один из action равен null
                } else if (storeData[id].action === null) {
                    if (action == 'like') {
                        likes++
                    } else {
                        dislikes++
                    }
                } else if (action === null) {
                    if (storeData[id].action == 'like') {
                        likes--
                    } else {
                        dislikes--
                    }
                }
                return {md5, id, likes, dislikes, action, storeData}
            }).then((resultData)=> {
                let {md5, id, likes, dislikes, action, storeData} = resultData;
                browser.storage.local.set({likes: likes, dislikes: dislikes}).then(()=> {
                    storeData[id].action = action;
                    browser.storage.local.set(storeData).then(()=> {
                        // TODO: Тут нужно сделать сохранение новой информации в window.webm_data и использовать ее при парсе
                        parseData(window.webm_data[md5].data, true);
                    });
                })
            })

        })
    })
}

function createLikeIcon(panel, cls, action) {
    if (action === cls) {
        createIcon(panel, cls + '-active');
    } else {
        createIcon(panel, cls);
    }
}

function setViews(panel, views, viewed = false) {
    let views_elem = panel.querySelector('span.views');
    if (views_elem === null) {
        views_elem = document.createElement('span');
        views_elem.className = 'views';

        if (viewed === true) {
            createIcon(views_elem, 'eye', 'viewed');
        } else {
            createIcon(views_elem, 'eye');
        }
        let text_el = document.createElement('span');
        views_elem.appendChild(text_el);
        panel.appendChild(views_elem);
    } else {
        if (viewed === true) {
            createIcon(views_elem, 'eye', 'viewed');
        } else {
            createIcon(views_elem, 'eye');
        }
    }
    let text_el = views_elem.querySelector('span');
    text_el.innerText = views;
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
function setViewListener(node, md5, id) {
    var img = node.querySelector('img.preview');
    // console.log(img);
    img.removeEventListener('click', increaseViewsListener);
    img.md5 = md5;
    img.id = id;
    img.addEventListener('click', increaseViewsListener, false);
}

// Красит элемент в нужный цвет в зависимости от шанса скримера
function setScreamColor(node, panel, screamChance, date) {
    screamChance += "";
    var scream = panel.querySelector('span.scream.tooltip');
    if (scream === null) {
        scream = document.createElement('span');
        scream.className = 'scream tooltip';
        let dateTooltip = document.createElement('span');
        dateTooltip.className = 'tooltiptext';
        dateTooltip.innerText = moment.utc(date).fromNow();
        // console.log(moment(date));
        scream.appendChild(dateTooltip);
        panel.appendChild(scream);
    }
    const img = node.querySelector('.webm-file');
    let clsHighlight = " ";
    // настройки панельки
    let volumePanelType = settings.volumePanelDisplay; // TODO: Await settings
    let iconDisplay;
    let iconColor;
    if (volumePanelType === 'color') {
        iconDisplay = "radio-unchecked";
    } else if (volumePanelType === 'none') {
        iconDisplay = 'clock';
    } else {
        iconDisplay = "radio-unchecked";
    }
    if (volumePanelType === 'none' || volumePanelType === 'icons') {
        iconColor = 'none';
    }
    if (settings.alwaysHighlight) {
        clsHighlight = "-const ";
    }
    switch (screamChance) {
        case "null":
            img.className += ' blue-shadow' + clsHighlight;
            scream.style.background = iconColor || '#3DBFFF';
            createIcon(scream, iconDisplay || 'volume-mute');
            break;
        case "0.0":
            img.className += ' green-shadow' + clsHighlight;
            scream.style.background = iconColor || '#45D754';
            createIcon(scream, iconDisplay || 'volume-low');
            break;
        case "0.5":
            img.className += ' yellow-shadow' + clsHighlight;
            scream.style.background = iconColor || 'yellow';
            createIcon(scream, iconDisplay || 'volume-medium');
            break;
        case "0.8":
            img.className += ' orange-shadow' + clsHighlight;
            scream.style.background = iconColor || 'orange';
            createIcon(scream, iconDisplay || 'volume-high');
            break;
        case "1.0":
            img.className += ' red-shadow' + clsHighlight;
            scream.style.background = iconColor || 'red';
            createIcon(scream, iconDisplay || 'volume-scream');
            break;
    }
}
function createIcon(node, name, cls) {
    let icon = node.querySelector('img');
    if (icon === null) {
        icon = document.createElement('img');
        icon.className = 'glyphicon';
        node.appendChild(icon);
    }
    if (cls !== undefined) {
        icon.className = 'glyphicon ' + cls;
    }
    icon.setAttribute('src', browser.runtime.getURL('icons/' + name + '.svg'));
}
// В зависимости от полученных с сервера данных обрабатывает посты в треде
// data - объект с данными одной webm
function parseData(data, onlyRender = false) {
    // TODO: Сделать отдельные функции для парсинга и для рендеринга
    // Если стоит onlyRender не изменять данные в глобальном объекте
    const md5 = data.md5;
    const id = data.id; // TODO: CHECK ITS IN HERE!
    let viewed = false; // Была ли уже просмотрена ШЕБМ
    let currViewed = false; // ШЕБМ была просмотрена в текущем треде (при обновлении страницы сбрасывается)
    let action = null;
    browser.storage.local.get(id).then((info) => {
        if (info[id]) {
            if (info[id].viewed === true) {
                viewed = true;
            }
            if (info[id].action) {
                action = info[id].action;
            }
            if (data.currViewed) {
                currViewed = true;
            }
        }
        if (onlyRender === false) {
            // Значит есть информация о лайках - Обновить только ее
            // if (data.action || data.action === null) {
            //     window.webm_data[md5].data = Object.assign({}, window.webm_data[md5].data, data);
            // } else {
            window.webm_data[md5].data = data;
            // }
        }
        let nodes = window.webm_data[md5].elems;
        nodes.forEach((node)=> {
            // Обрабатываем только новые ноды
            if (data.message) {
                console.log(data.message);
                setWEBMPanel({node, message: data.message});
                node.removeEventListener('mouseenter', OneWEBMListener);
                node.addEventListener('mouseenter', OneWEBMListener);
            } else {
                var screamChance = data["screamer_chance"];
                node.removeEventListener('mouseenter', OneWEBMListener);
                setWEBMPanel({
                    node,
                    id: id,
                    md5: data.md5,
                    screamChance: screamChance,
                    views: data.views,
                    likes: data.likes,
                    dislikes: data.dislikes,
                    action: action,
                    message: null,
                    viewed: viewed,
                    date: data["time_created"]
                });
                if (currViewed === false) {
                    setViewListener(node, md5, id); // Потом сделать постоянное навешивание, но на сервере увеличивать счетчик не чаще раза в 10 минут
                }
            }
        })
    });
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

    for (let node of nodes) {
        var div = node.querySelector('div');
        var a = div.querySelector('a');
        if (a.getAttribute('href').slice(-5) == ".webm" || a.getAttribute('href').slice(-4) == ".mp4") {
            var size = parseInt(node.querySelector('figcaption.file-attr > span.filesize').innerText.substring(1, 30).split(',')[0]);
            var md5 = div.id.split('-').pop();
            var url = qualifyURL(a.getAttribute('href'));
            var webm = {md5: md5, url: url};
            if (size < MAX_SIZE) {
                if (window.webm_data[md5] === undefined) {
                    window.webm_data[md5] = {elems: [], data: {}};
                }
                window.webm_data[md5].elems.push(node);
                data.push(webm);
            } else {
                setWEBMPanel({node, message: 'Слишком большой размер'})
            }
        }
    }
    ;
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
        // console.log(resp);
        return resp.json()
    }).then(function (json) {
        json.forEach(function (data) {
            parseData(data);
        })
    })
}

module.exports = {getOneWEBMData, getAllWEBMData, increaseViews};
