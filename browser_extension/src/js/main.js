import threadHandler from './thread'
import threadListHandler from './threadList'
import {BOARDS} from "./config"
import runAPI from  './dollchan'

// Полифил чтобы работал Firefox
global.browser = global.chrome;

//Смотрим находимся ли мы в треде или на главной странице борды
const curr_url = window.location.pathname;
const pathArray = curr_url.split('/');
const currBoard = pathArray[1];
// Если мы не на главной странице и доска поддерживается, то включаем скрипт
console.log(currBoard);
console.log(pathArray.length);
if (document.querySelector('div#de-main')) {
    console.log('Есть кукла!');
    setTimeout(runAPI, 0);
    window.isDollchanEnabled = true;
}
if (currBoard && BOARDS.indexOf(currBoard) !== -1) {
    //Если в списке тредов
    if (pathArray.length == 3) {
        console.log("Мы в списке тредов");
        threadListHandler();
        //Если в треде
    } else {
        console.log("Мы в треде");
        threadHandler();
    }
} else {
    console.log("Отключили webmtube");
}


// inject code into "the other side" to talk back to this side;
// var script = document.createElement('script');
//
// function main() {
//     window.Stage("WEBM детектор скримеров", "webmtube", 3, function () {
//         if (!window.thread.board) return; //не запускаем на главной
//         console.log("Детектор скримеров");
//         window.postMessage({type: "FROM_PAGE", posts: [3, 2, 5]}, "*");
//         window.addEventListener("message", function (event) {
//             // We only accept messages from ourselves
//             if (event.source != window)
//                 return;
//
//             if (event.data.type && (event.data.type == "SECOND_ELEMENT")) {
//                 console.log("Второй элемент: " + event.data.posts);
//             }
//         }, false);
//     })
// }
//
// script.appendChild(document.createTextNode('(' + main + ')();'));
//
// document.body.appendChild(script);
//
//
// window.addEventListener("message", function (event) {
//     // We only accept messages from ourselves
//     if (event.source != window)
//         return;
//
//     if (event.data.type && (event.data.type == "FROM_PAGE")) {
//         console.log("Content script received: " + event.data.posts);
//         window.postMessage({type: "SECOND_ELEMENT", posts: event.data.posts[1]}, "*");
//     }
// }, false);

