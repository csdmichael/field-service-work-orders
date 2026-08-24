const http = require('http');
const fs = require('fs');
const path = require('path');

const port = process.env.PORT || 4200;
http.createServer((req, res) => {
  const file = path.join(__dirname, 'src', 'index.html');
  res.writeHead(200, { 'Content-Type': 'text/html' });
  fs.createReadStream(file).pipe(res);
}).listen(port, () => console.log(`ui listening on ${port}`));
