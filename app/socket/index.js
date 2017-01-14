const express = require('express');
const app = express();
const bodyParser = require('body-parser');
const http = require('http').Server(app);
const io = require('socket.io')(http);
const YAML = require('yamljs')
const CONFIG_FILE = ('./../conf/config.yml')

app.use(express.static('./../front-app'));
app.use(bodyParser.json());

io.on('connection', function(socket){
  console.log('a user connected');
});

app.get('/init', (req, res) =>{
    res.send(YAML.load(CONFIG_FILE));
})

app.post('/video', (req, res)=> {
    io.emit('video', req.body)
    res.send()
})

app.post('/newPrices', (req, res) =>{
	io.emit('prices', req.body)
	res.send()
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
