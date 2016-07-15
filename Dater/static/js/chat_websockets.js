var url_parse = location.search.replace('?','').split('&').reduce(function(s,c){var t=c.split('=');s[t[0]]=t[1];return s;},{});
var recipient_sid = Number(url_parse.sid);

sock = new SockJS("http://127.0.0.1:" + tornado_port + "/socket");
var thread_id = [sender, recipient_sid].sort(function(a,b){return a-b;}).join("_");

sock.onopen = function() {
    //sock.send('auth:' + sender);
    var data = '{\"type\": \"auth\", \"sid\": \"' + sender + '\"}';

    sock.send(data);
    console.log('open');

 };

sock.onmessage = function(data) {
    var json_data = JSON.parse(data.data);
    if (json_data.type == 'alert') {
        console.log(json_data.body)
    } else if (json_data.type == 'message') {
        console.log("Message got: " + json_data.body + '. Datetime: ' + json_data.datetime);
         $(".chat").append('<li class="clearfix"><div class="chat-body clearfix"><span class="time">' +
            '[' + json_data.datetime_ +']</span> <strong style="color:red" class="primary-font">' + json_data.sender +
             '</strong>: <span>' + json_data.body + '</span></div></li>');
    }
 };

sock.onclose = function() {
    console.log('close');
    $(".chat").append('<li class="clearfix"><div class="chat-body clearfix">Connection closed. Please, reload page</div></li>');
};


function sendNewMessage() {
    var new_message = document.getElementById("message").value;
    data = '{\"type\": \"message\", \"recipient\": \"' + recipient_sid + '\", \"sender\": \"' + sender + '\",'+
        ' \"body\": \"' + new_message + '\"}';
    sock.send(data);
    $("#message").val("");
    console.log("Created message (successfuly)");
    return false;
}

//$("#message").on("focus", function(){
//    $(this).val("");
//});
//
//$("#btn-chat").on("click", function(event){
//    $("#message").val("");
//});















//var socket = new io.connect("http://localhost:" + tornado_port + "/");
//var recipient_sid = url_parse.sid;
//
//socket.on('connect', function() {
//    socket.json.send({"sender": sender, "recipient": recipient_sid});
//    console.log('Socket connected!');
//});
//
//socket.on('message', function(msg) {
//    console.log(msg);
//    $(".chat").append('<li class="clearfix"><div class="chat-body clearfix"><span class="time">' +
//        '[05:08:28]</span> <strong style="color:red" class="primary-font">' + msg.from + '</strong>:<span>' + msg.body +
//        '</span></div></li>')
//
//});
//
////socket.on('disconnect', function() {
////    socket.socket.reconnect();
////});
//
//
//function sendNewMessage() {
//   var new_message = document.getElementById("message"),
//       data = {"sender": sender, "recipient": recipient_sid, "body": new_message.value};
//   socket.json.send(data);
//   console.log("Created message (successfuly)");
//   return false;
//}
