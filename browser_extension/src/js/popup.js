import {DEFAULT_SETTINGS} from './config'

// Полифил чтобы работал Firefox
global.browser = global.chrome;

// Saves options to chrome.storage
function load_stats() {
    chrome.storage.sync.get({
        views: 0,
        likes: 0,
        dislikes: 0
    }, function (data) {
        let viewsEl = document.getElementById('views');
        viewsEl.textContent = data.views;
    });
}
document.addEventListener('DOMContentLoaded', load_stats);