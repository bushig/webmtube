import {MAX_SIZE} from './config'

var active_nodes = {};

// Function to get absolute url from relative
function qualifyURL(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.href;
}

function setMessage(node, text, color) {
    //Sets message of webm, accepts figure.image selector and text
    var parent = node.querySelector('figcaption.file-attr');
    var message = parent.querySelector('span.message');
    if (message == null) {
        message = document.createElement('span');
        message.className = 'message';
        parent.insertBefore(message, parent.children[1]);
    }
    message.innerText = text;
    message.style.background = color;
}

function setViewListener(node, md5) {
    var img = node.querySelector('img');
    img.addEventListener('click', function increaseViewsListener(event) {
        event.target.removeEventListener('click', increaseViewsListener);
        var request = new Request(`https://devshaft.ru/check/${md5}/view`, {
            method: 'GET',
            mode: 'cors'
        });
        fetch(request);
    });
}

function setScreamColor(node, screamChance) {
    if (screamChance == null) {
        node.style.background = 'blue';
    } else if (screamChance == 0) {
        node.style.background = 'green';
    } else if (screamChance == 0.5) {
        node.style.background = 'yellow';
    } else if (screamChance == 0.8) {
        node.style.background = 'orange';
    } else if (screamChance == 1.0) {
        node.style.background = 'red';
    }
}

function getOneWEBMData(node) {
    var div = node.querySelector('div');
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

function parseData(data) {
    var md5 = data.md5;
    var node = active_nodes[md5];
    if (data.message) {
        console.log(data.message);
        setMessage(node, data.message, '#60D68C');
        node.addEventListener('mouseenter', function OneWEBMListener(event) {
            event.target.removeEventListener('mouseenter', OneWEBMListener);
            setTimeout(getOneWEBMData, 5000, node);
        })
    } else {
        setMessage(node, "Просмотров: " + data.views, '#b3b3b3');
        setViewListener(node, data.md5);
        var screamChance = data.scream_chance;
        setScreamColor(node, screamChance);
    }
}

function getAllWEBMData(nodes) {
    var data = [];

    nodes.forEach(function (val) {
        var div = val.querySelector('div');
        var a = div.querySelector('a');
        if (a.getAttribute('href').slice(-5) == ".webm") {
            var size = parseInt(val.querySelector('figcaption.file-attr > span.filesize').innerText.substring(1, 30).split(',')[0]);
            var md5 = div.id.split('-').pop();
            var url = qualifyURL(a.getAttribute('href'));
            var webm = {md5: md5, url: url};
            if (size < MAX_SIZE) {
                active_nodes[md5] = val;
                data.push(webm);
            } else {
                setMessage(val, 'Слишком большой размер', 'orange')
            }
        }
    });
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

module.exports = getAllWEBMData;