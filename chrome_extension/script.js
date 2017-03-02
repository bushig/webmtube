var nodes = document.querySelectorAll("figure.image");

// Function to get absolute url from relative
function qualifyURL(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.href;
}

function getAllWEBMData(nodes) {
    var data = [];

    nodes.forEach(function (val) {
        var div = val.querySelector('div');
        var a = div.querySelector('a');
        if (a.getAttribute('href').slice(-5) == ".webm") {
            var md5 = div.id.split('-').pop();
            var url = qualifyURL(a.getAttribute('href'));
            var webm = {md5: md5, url: url};
            data.push(webm);
        }
    });
    var request = new Request('https://devshaft.ru/check', {
        method: 'POST',
        mode: 'cors',
        body: JSON.stringify(data)
    });
    fetch(request).then(function (resp) {
        //console.log(resp.json());
        return resp.json()
    }).then(function (json) {
        json.forEach(function (data) {
            if (data.message) {
                console.log(data.message);
            }
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