import {getAllWEBMData, getOneWEBMData} from './common'
window.checked_nodes = new Set(); //обработанные элементы .thread figure.image
window.webm_data = {}; //Словарь с данными о вебм

function threadHandler() {
    checkNewPosts();
    setInterval(checkNewPosts, 4000);
}


function checkNewPosts() {
    var nodes = Array.prototype.slice.call(document.querySelectorAll(".thread figure.image")); // NodeList переводим в Array
    if (nodes.length !== window.checked_nodes.length) {
        // console.log(nodes);
        var new_nodes = nodes.filter((node)=> {
            if (!window.checked_nodes.has(node)) {
                window.checked_nodes.add(node);
                return true;
            } else {
                return false
            }
        });
        if (new_nodes.length > 0) {
            console.log(new_nodes.length, " новых элементов");
            getAllWEBMData(new_nodes);
        }
    }

}


module.exports = threadHandler;