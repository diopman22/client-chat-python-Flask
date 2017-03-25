var express = require('express');
var app = express();
var querystring = require('querystring');

var list_users = [];
var list_salons = [];


//verification login
function verifLogin(login) {
    var ok = true;
    for (var i = 0; i < list_users.length; i++) {
        if(list_users[i]==login){
            
            ok= false;
            break;
        }
    }
    return ok;
}

//verification salon
function verifSalon(nomSalon) {
    var ok = true;
    if(list_salons.length!=0){
        for (var i = 0; i < list_salons.length; i++) {
            if(list_salons[i].nomSalon==nomSalon){
                
                ok= false;
                break;
            }
        }
    }
    return ok;
}

//les messages du salon
function getMessagesSalon(salon,login) {
    // body...
    var i=-1,ind=0;
    list_salons.forEach(function(salonSelect){
        i++;
        if(salonSelect.nomSalon==salon){
            ind=i;
            salonSelect.list_login.forEach(function(log){
                if(log==login)
                    return salonSelect.list_messages;
            })
        }
    })
    list_salons[ind].list_login.push(login);
    return list_salons[ind].list_messages;
} 

//ajouter le message au salon
function addMessageSalon(salon,message) {
    console.log("salon choisi "+salon+" mess:"+message)
    list_salons.forEach(function(salonSelect){
        if(salonSelect.nomSalon==salon){
           salonSelect.list_messages.push(message);
           console.log("add message: "+salonSelect.nomSalon+" : "+salonSelect.list_messages);
        }
    })
} 

//les autres salons 
function getAnotherRooms(login) {
    var list_another_rooms = [];
    var ok = false;
    for (var i = 0; i < list_salons.length; i++) {
        for (var j = 0; j < list_salons[i].list_login.length; j++) {
            if(list_salons[i].list_login[j]==login){
                ok= true;
                break;
            }
            
        }
        if (ok==false) {
            list_another_rooms.push(list_salons[i].nomSalon);      
        }
        else ok=false;
        
    }
    return list_another_rooms;
}


//les salons
function getRooms() {
    var ma_liste = [];
    list_salons.forEach(function(salonSelect){        
        ma_liste.push(salonSelect.nomSalon);
    }) 
    return ma_liste;
}


//delete user from rooms
function deleteUser(login) {
    for(var i=0; i<list_users.length; i++){
        if (list_users[i] == login) {
            list_users.splice(i, 1);
            break;
        }
    }
    list_salons.forEach(function (salonSelect) {
        for(var i=0; i<salonSelect.list_login.length; i++){
            if (salonSelect.list_login[i] == login) {
                salonSelect.list_login.splice(i, 1);
                break;
            }
        }
    })
}

//subscribe
app.get('/subscribe', function (req, res) {
    var login = req.query.login;
    if (!verifLogin(login)) {
        res.send({"response":"login exist"});    
    }else{
        list_users.push(login);
        res.send({"response":login});
    }
});

//addSalon
app.post('/addSalon', function (req, res) {
    var nomSalon = req.query.nomSalon;
    var login = req.query.login;
    if (!verifSalon(nomSalon)) {
        res.json({"response":"salon exist"});    
    }else{
        
        list_salons.push({"nomSalon":nomSalon,"list_login":[login], "list_messages":[]});
        res.json({"response":nomSalon});
    }
});

//get other rooms
app.get('/getAnotherRooms', function (req, res) {
    var login = req.query.login;
    res.json(getAnotherRooms(login)); 
});

//add Message
app.post('/sendMessage', function (req, res) {
    var salon = req.query.salon;
    console.log(salon);
    var message = req.query.message;
    var login = req.query.login;
    message = login+" --> "+message;
    addMessageSalon(salon, message);
    res.json({"response":message});
});


//get messages rooms
app.get('/getMessagesSalon', function (req, res) {
    var login = req.query.login;
    var salon = req.query.salon;
    res.json(getMessagesSalon(salon,login));
     
});

//get rooms
app.get('/getRooms', function (req, res) {
    res.json(getRooms());
});

//unSubscribe
app.post('/unSubscribe', function (req, res) {
    var login = req.query.login;
    deleteUser(login);
    res.json({"response":"ok"});
});

 
app.listen(8092);
