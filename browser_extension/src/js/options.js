import {DEFAULT_SETTINGS} from './config'

// Полифил чтобы работал Firefox
global.browser = global.chrome;

// Saves options to chrome.storage
function save_options() {
    let highlight = document.getElementById('highlight').checked;
    browser.storage.sync.set({
        alwaysHighlight: highlight
    }, function () {
        // Update status to let user know options were saved.
        var status = document.getElementById('status');
        status.textContent = 'Настройки сохранены.';
        setTimeout(function () {
            status.textContent = '';
        }, 750);
    });
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
    // Use default value color = 'red' and likesColor = true.
    browser.storage.sync.get(DEFAULT_SETTINGS,
        function (items) {
        console.log(items);
        document.getElementById('highlight').checked = items.alwaysHighlight;
    });
}

function reset_stats() {
    browser.storage.local.clear(function () {
        var status = document.getElementById('status');
        status.textContent = 'Статистика сброшена.';
        setTimeout(function () {
            status.textContent = '';
        }, 750);
    });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
    save_options);
document.getElementById('reset').addEventListener('click',
    reset_stats);