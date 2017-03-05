var MAX_SIZE = 22000; //Max size in KB

var nodes = document.querySelectorAll("figure.image");
var active_nodes = {};
// Function to get absolute url from relative
function qualifyURL(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.href;
}

function setMessage(node, text) {
    //Sets message of webm, accepts figure.image selector and text
    var parent = node.querySelector('figcaption.file-attr');
    var message = parent.querySelector('span.message');
    if (message == null) {
        message = document.createElement('span');
        message.className = 'message';
        parent.insertBefore(message, parent.children[1]);
    }
    message.innerText = text;
    message.style.background = '#60D68C';
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
        setMessage(node, data.message);
        node.addEventListener('mouseenter', function (event) {
            event.target.removeEventListener(event.type, arguments.callee);
            setTimeout(getOneWEBMData, 5000, node);
        })
    } else {
        setMessage(node, null);
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
                setMessage(val, 'Слишком большой размер')
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

getAllWEBMData(nodes);

// nodes.forEach(function (val) {
//     var div = val.querySelector('div');
//     var a = div.querySelector('a');
//     if (a.getAttribute('href').slice(-5) == ".webm") {
//         val.addEventListener("mouseenter", function (event) {
//             event.target.removeEventListener(event.type, arguments.callee);
//             var md5 = div.id.split('-').pop();
//             var url = encodeURIComponent(qualifyURL(a.getAttribute('href')));
//             var request = new Request(`https://devshaft.ru/check?md5=${md5}&url=${url}`, {
//                 method: 'GET',
//                 mode: 'cors'
//             });
//             fetch(request).then(function (response) {
//                     console.log(response);
//                     if (response.status == 200) {
//                         return response.json();
//                     } else if (response.status == 202) {
//                         div.style.background = '#C0C0C0';
//                     } else {
//                         throw new Error(`Request error to Scream checker. Status code: ${response.status}`);
//                     }
//                 }
//             ).then(function (json) {
//                 var screamChance = json.scream_chance;
//                 if (screamChance == null) {
//                     val.style.background = 'blue';
//                 } else if (screamChance == 0) {
//                     val.style.background = 'green';
//                 } else if (screamChance == 0.5) {
//                     val.style.background = 'yellow';
//                 } else if (screamChance == 0.8) {
//                     val.style.background = 'orange';
//                 } else if (screamChance == 1.0) {
//                     val.style.background = 'red';
//                 }
//             })
//         })
//     }
// });