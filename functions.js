// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

let webRTCConnection;


// Allow users to send messages by pressing enter instead of clicking the Send button
document.addEventListener("keypress", function (event) {
    if (event.code === "Enter") {
        sendDM();
    }
});

// Renders a new chat message to the page
function addMessage(chatMessage) {
    let chat = document.getElementById('chat');
    chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
}
function sendMessage() {
    const chatBox = document.getElementById("chat-comment");
    const comment = chatBox.value;
    chatBox.value = "";
    chatBox.focus();
    if (comment !== "") {
        socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': comment}));
    }
}
// called when the page loads to get the chat_history
function get_chat_history() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessage(message);
            }
        }
    };
    request.open("GET", "/chat-history");
    request.send();
}

function dmAlert(chatMessage){
    alert(chatMessage['username']+ ": "+chatMessage["comment"])
}

function add_username(user){
    let users = document.getElementById('allUsers');
    users.innerHTML+="<b>" + user + "</b> "+ "<br/>";
}

function get_all_users_online(){
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status === 200) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                add_username(message);
            }
        }
    };
    request.open("GET", "/active-users");
    request.send();
}

function sendDM() {
    const userBox = document.getElementById("dm-user")
    const name = userBox.value;
    userBox.value = "";
    userBox.focus();
    if (name !== "") {
        const chatBox = document.getElementById("dm-mess")
        const comment = chatBox.value;
        chatBox.value = "";
        chatBox.focus();
        if (comment !== ""){
            socket.send(JSON.stringify({'messageType': 'dmMessage', 'comment': comment, 'toUser':name}));
        }
    }
}

// Called whenever data is received from the server over the WebSocket connection
socket.onmessage = function (ws_message) {
    const message = JSON.parse(ws_message.data);
    const messageType = message.messageType

    switch (messageType) {
        case 'dmMessage':
            dmAlert(message);
            break;
        case 'chatMessage':
            addMessage(message);
            break;
        case 'webRTC-offer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
            webRTCConnection.createAnswer().then(answer => {
                webRTCConnection.setLocalDescription(answer);
                socket.send(JSON.stringify({'messageType': 'webRTC-answer', 'answer': answer}));
            });
            break;
        case 'webRTC-answer':
            webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
            break;
        case 'webRTC-candidate':
            webRTCConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            break;
        default:
            console.log("received an invalid WS messageType");
    }
}

function connectWebRTC() {
    // create and send an offer
    webRTCConnection.createOffer().then(webRTCOffer => {
        socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer}));
        webRTCConnection.setLocalDescription(webRTCOffer);
    });

}

function welcome() {
    get_all_users_online()
    get_chat_history()
}

// https://www.w3schools.com/howto/howto_js_toggle_password.asp
function show_password() {
    var x = document.getElementById("password");
    if (x.type === "password") {
      x.type = "text";
    } else {
      x.type = "password";
    }
}

function register() {
    const un = document.getElementById("username");
    const pass = document.getElementById("password");
    const username = escape_html(un.value)
    const password = escape_html(pass.value)
    const request = new XMLHttpRequest();
    var valid = true
    request.onreadystatechange = function(){
        if	(this.readyState === 4 && this.status === 200){
            document.location.href = '/register'
            // newUser(username)
            un.value = ""
            pass.value = ""
            un.focus()
            valid = true
        }
        else if (this.status === 404){
            useranme_taken()
            un.value = ""
            pass.value = ""
            un.focus()             
            valid = false
        }
    };
    if (valid){
    request.open("POST", "/register");
    let data= {'username':username,'password':password}
    request.send(JSON.stringify(data));
    }
}

function newUser(user){
    let username = document.getElementById("reg_welcome")
    username.innerHTML += "Successful registration welcome!"+ user + "!"
}
function useranme_taken(){
    let username = document.getElementById("User")
    username.innerHTML = "An account with this username already exist login or try another username!"
}

function login() {
    const un = document.getElementById("username");
    const pass = document.getElementById("password");
    const username = escape_html(un.value)
    const password = escape_html(pass.value)
    const request = new XMLHttpRequest();
    var valid = true
    request.onreadystatechange = function(){
        if	(this.readyState === 4 && this.status === 200){
            document.location.href = '/'
            // signIn(username)
            // un.value = ""
            // pass.value = ""
            // valid = true
        }
        else if (this.status === 404){
            NotFound()
            un.value = ""
            pass.value = ""
            valid = false
        }        
    };
    if (valid){
        request.open("POST", "/");
        let data= {'username':username,'password':password}
        request.send(JSON.stringify(data));
        }
}

function signIn(user){
    let username = document.getElementById("welcome_back")
    username.innerHTML = "Welcome back, " + user + "!"
}
function NotFound(){
    let username = document.getElementById("User")
    username.innerHTML = "User not Found"
}

function escape_html(input){
    return input.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;')
}

function add_prof() {
    const un = document.getElementById("username");
    const fav = document.getElementById("fav_prof");
    const username = un.value
    const fav_prof = fav.value
    const request = new XMLHttpRequest();
    request.onreadystatechange = function(){
        if	(this.readyState === 4 && this.status === 200){
            document.location.href = '/'
        }
    };
    request.open("POST", "/fav_prof");
    let data= {'username':username,'fav_prof':fav_prof}
    request.send(JSON.stringify(data));
}

function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementsByClassName("main").style.marginLeft = "250px";
  }
  
  /* Set the width of the sidebar to 0 and the left margin of the page content to 0 */
  function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementsByClassName("main").style.marginLeft = "0";
  }

  let like = document.getElementById('increment');
  let dislike = document.getElementById('decrement');
  let happy = document.getElementById('1');
  let sad = document.getElementById('2');
  let dope = document.getElementById('DOPE');
  let crazy = document.getElementById('CRAZY');
  let reallyfunny = document.getElementById('really funny');
  let ok = document.getElementById('OK');
  let agree = document.getElementById('agree');
  let disagree = document.getElementById('disagree');
  let mad = document.getElementById('mad');
  let emo = document.getElementById('EMO');
  let wtf = document.getElementById('WTF');
  let dmmessage = document.getElementById('response')
  
  
  
  emo.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'eMoTiOnAl DaMaNge' + '         response to:' + dmmessage.value}))
      }
      else {
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'eMoTiOnAl DaMaNge'}))
      }
  })
  
  
  wtf.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'What did I SAW??????' + '         response to:' + dmmessage.value}))
      }
      else {
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'What did I SAW??????'}))
      }
  })
  
  like.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'I LIKE IT!' + '         response to:' + dmmessage.value}))
      }
      else {
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'I LIKE IT!'}))
      }
  })
  
  
  dislike.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'NAH, NO GOOD' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'NAH, NO GOOD'}))
      }
  })
  
  happy.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'HA~HA~HA~' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'HA~HA~HA~'}))
      }
  })
  
  sad.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'Im crying' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'Im crying'}))
      }
  })
  
  dope.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': "DAMN that's DOPEEEEEE" + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': "DAMN that's DOPEEEEEE"}))
      }
  
  })
  
  crazy.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'CrAzYyYyYyYy' + '         response to:' + dmmessage.value}))
      }
      else {
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'CrAzYyYyYyYy'}))
      }
  })
  
  reallyfunny.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'LMAO!!!' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'LMAO!!!'}))
      }
  
  })
  
  ok.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'OK' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'OK'}))
      }
  
  })
  
  agree.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'Agree' + '         response to:' + dmmessage.value}))
      }
      else {
         socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'Agree'}))
      }
  
  })
  
  disagree.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'Disagree' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'Disagree'}))
      }
  
  })
  
  dislike.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'NAH, NO GOOD' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'NAH, NO GOOD'}))
      }
  
  })
  
  mad.addEventListener('click',function(){
      if (dmmessage.value.toString() !== ""){
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'You pissing me off!' + '         response to:' + dmmessage.value}))
      }
      else{
          socket.send(JSON.stringify({'messageType': 'chatMessage', 'comment': 'You pissing me off!'}))
      }
  
  })