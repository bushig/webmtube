var nodes = document.querySelectorAll("figure.image");

// Function to get absolute url from relative
function qualifyURL(url) {
    var a = document.createElement('a');
    a.href = url;
    return a.href;
}

nodes.forEach(function (val) {
    var div = val.querySelector('div');
    var a = div.querySelector('a');
    if (a.getAttribute('href').slice(-5) == ".webm") {
        val.addEventListener("mouseenter", function (event) {
            //val.removeEventListener('mouseover');
            var md5 = div.id.split('-').pop();
            var url = encodeURIComponent(qualifyURL(a.getAttribute('href')));
            var request = new Request(`https://devshaft.ru/check?md5=${md5}&url=${url}`, {
                method: 'GET',
                mode: 'cors'
            });
            fetch(request).then(function (response) {
                    console.log(response);
                    if (response.status == 200) {
                        return response.json();
                    } else if (response.status == 203) {
                        div.style.background = 'blue';
                    } else {
                        throw new Error(`Request error to Scream checker. Status code: ${response.status}`);
                    }
                }
            ).then(function (json) {
                var screamChance = json.scream_chance;
                if (screamChance == null) {
                    div.style.background = '#C0C0C0';
                } else if (screamChance == 0) {
                    div.style.background = 'green';
                } else if (screamChance == 0.5) {
                    div.style.background = 'yellow';
                } else if (screamChance == 0.8) {
                    div.style.background = 'orange';
                } else if (screamChance == 1.0) {
                    div.style.background = 'red';
                }
            })
        })
    }
});