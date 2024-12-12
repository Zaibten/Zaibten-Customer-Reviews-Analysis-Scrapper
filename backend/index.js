require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));

// Serve Login Page
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Admin Login</title>
      <style>
        body, html {
          margin: 0;
          padding: 0;
          width: 100%;
          height: 100%;
          background: #000;
          color: #fff;
          font-family: Arial, sans-serif;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        #particles-js {
          position: absolute;
          width: 100%;
          height: 100%;
          z-index: -1;
        }
        .login-container {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 15px;
          padding: 20px;
          text-align: center;
          width: 300px;
        }
        .logo {
          max-width: 100px;
          border-radius: 50%;
          margin-bottom: 20px;
        }
        input {
          width: 90%;
          padding: 10px;
          margin: 10px 0;
          border: none;
          border-radius: 5px;
          outline: none;
        }
        button {
          width: 95%;
          padding: 10px;
          border: none;
          border-radius: 5px;
          background-color: #007BFF;
          color: #fff;
          font-size: 16px;
          cursor: pointer;
        }
        button:hover {
          background-color: #0056b3;
        }
      </style>
      <script src="https://cdn.jsdelivr.net/npm/particles.js"></script>
    </head>
    <body>
      <div id="particles-js"></div>
      <div class="login-container">
        <img src="../assets/logo.png" alt="App Logo" class="logo">
        <form action="/login" method="POST">
          <input type="text" name="username" placeholder="Username" required>
          <input type="password" name="password" placeholder="Password" required>
          <button type="submit">Login</button>
        </form>
      </div>
      <script>
        particlesJS('particles-js', {
          "particles": {
            "number": {
              "value": 80,
              "density": {
                "enable": true,
                "value_area": 800
              }
            },
            "color": {
              "value": "#ffffff"
            },
            "shape": {
              "type": "circle",
              "stroke": {
                "width": 0,
                "color": "#000000"
              },
              "polygon": {
                "nb_sides": 5
              },
            },
            "opacity": {
              "value": 0.5,
              "random": false,
              "anim": {
                "enable": false,
              }
            },
            "size": {
              "value": 3,
              "random": true,
              "anim": {
                "enable": false,
              }
            },
            "line_linked": {
              "enable": true,
              "distance": 150,
              "color": "#ffffff",
              "opacity": 0.4,
              "width": 1
            },
            "move": {
              "enable": true,
              "speed": 6,
              "direction": "none",
              "random": false,
              "straight": false,
              "out_mode": "out",
              "bounce": false,
              "attract": {
                "enable": false,
              }
            }
          },
          "interactivity": {
            "detect_on": "canvas",
            "events": {
              "onhover": {
                "enable": true,
                "mode": "repulse"
              },
              "onclick": {
                "enable": true,
                "mode": "push"
              },
              "resize": true
            },
          },
          "retina_detect": true
        });
      </script>
    </body>
    </html>
  `);
});

// Handle Login
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  if (
    username === process.env.ADMIN_USERNAME &&
    password === process.env.ADMIN_PASSWORD
  ) {
    res.send('<h1>Welcome, Admin!</h1>');
  } else {
    res.send('<h1>Invalid Username or Password</h1>');
  }
});

// Start Server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
