import {DEFAULT_SETTINGS} from './config'

// Полифил чтобы работал Firefox
global.browser = global.chrome;

// Saves options to chrome.storage
function load_stats() {
    chrome.storage.local.get({
        views: 0,
        likes: 0,
        dislikes: 0
    }, function (data) {
        let viewsEl = document.getElementById('views');
        let likesEl = document.getElementById('likes');
        let dislikesEl = document.getElementById('dislikes');
        viewsEl.textContent = data.views;
        likesEl.textContent = data.likes;
        dislikesEl.textContent = data.dislikes;

    });
}
document.addEventListener('DOMContentLoaded', load_stats);