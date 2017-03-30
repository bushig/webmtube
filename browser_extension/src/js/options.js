// Saves options to chrome.storage
function save_options() {
    let highlight = document.getElementById('highlight').checked;
    chrome.storage.sync.set({
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
    chrome.storage.sync.get({
        alwaysHighlight: false
    }, function (items) {
        console.log(items);
        document.getElementById('highlight').checked = items.alwaysHighlight;
    });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
    save_options);