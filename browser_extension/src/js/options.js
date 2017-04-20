import {DEFAULT_SETTINGS} from './config'

// Полифил чтобы работал Firefox
// global.browser = global.chrome;

// Saves options to chrome.storage
function save_options() {
    let highlight = document.getElementById('highlight').checked;
    let volumePanelDisplay;
    let volumeRadios = document.getElementsByName('volumePanelDisplay');
    for (let i = 0; i < volumeRadios.length; i++) {
        if (volumeRadios[i].checked) {
            volumePanelDisplay = volumeRadios[i].value;
            break;
        }
    }

    browser.storage.local.set({
        alwaysHighlight: highlight, volumePanelDisplay: volumePanelDisplay
    }).then(() => {
        // Update status to let user know options were saved.
        let status = document.getElementById('status');
        status.textContent = 'Настройки сохранены.';
        setTimeout(()=> {
            status.textContent = '';
        }, 750);
    });
}

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options() {
    // Use default value color = 'red' and likesColor = true.
    browser.storage.local.get(DEFAULT_SETTINGS).then((items) => {
        // console.log(items);
        document.getElementById('highlight').checked = items.alwaysHighlight;
        document.querySelector("input[name='volumePanelDisplay'][value='" + items.volumePanelDisplay + "']").checked = true;
    });
}

function reset_stats() {
    browser.storage.local.clear().then(() => {
        let status = document.getElementById('status');
        status.textContent = 'Статистика сброшена.';
        setTimeout(() => {
            status.textContent = '';
        }, 750);
    });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
    save_options);
document.getElementById('reset').addEventListener('click',
    reset_stats);