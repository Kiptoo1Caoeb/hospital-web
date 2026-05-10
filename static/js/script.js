
function toggleDarkMode(){
document.body.classList.toggle('dark-mode');
}

function openChat(){
const chat=document.getElementById('chat');
chat.style.display=chat.style.display==='block'?'none':'block';
}

function speakWelcome(){
const speech = new SpeechSynthesisUtterance('Welcome to the smart HCI hospital management system');
window.speechSynthesis.speak(speech);
}

function startRecognition(){
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.onresult = function(event){
alert('Voice Command: ' + event.results[0][0].transcript);
}

recognition.start();
}
