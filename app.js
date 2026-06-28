const express = require('express');
const path = require('path');
const mysql = require('mysql2/promise');

const app = express();
const PORT = process.env.PORT || 3000;

// Create a MySQL Connection Pool using environment variables (DevOps Best Practice)
const pool = mysql.createPool({
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'your_password',
    database: process.env.DB_NAME || 'cozy_bean_db',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

// Middleware
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Root Route redirect
app.get('/', (req, res) => {
    res.redirect('/home.html');
});

// API endpoint for Table Bookings
app.post('/api/booking', async (req, res) => {
    const { name, email, dateTime, guests } = req.body;
    
    const query = 'INSERT INTO bookings (name, email, booking_time, guests) VALUES (?, ?, ?, ?)';
    const values = [name, email, dateTime, parseInt(guests, 10)];

    try {
        await pool.execute(query, values);
        res.send(`
            <body style="background:#fffbeb;font-family:sans-serif;text-align:center;padding-top:50px;">
                <h2 style="color:#78350f;">🎉 Booking Confirmed!</h2>
                <p>Thank you, ${name}. We look forward to seeing you at the café.</p>
                <a href="/home.html" style="color:#b45309;">Go Back Home</a>
            </body>
        `);
    } catch (err) {
        console.error("MySQL Insertion Error (Bookings): ", err);
        res.status(500).send("Database Insertion Failure.");
    }
});

// API endpoint for Contact Submissions
app.post('/api/contact', async (req, res) => {
    const { name, message } = req.body;

    const query = 'INSERT INTO messages (name, message) VALUES (?, ?)';
    const values = [name, message];

    try {
        await pool.execute(query, values);
        res.send(`
            <body style="background:#fffbeb;font-family:sans-serif;text-align:center;padding-top:50px;">
                <h2 style="color:#78350f;">✉️ Message Sent!</h2>
                <p>Thanks for reaching out, ${name}. We'll get back to you shortly.</p>
                <a href="/home.html" style="color:#b45309;">Go Back Home</a>
            </body>
        `);
    } catch (err) {
        console.error("MySQL Insertion Error (Messages): ", err);
        res.status(500).send("Database Insertion Failure.");
    }
});

app.listen(PORT, () => {
    console.log(`Café MySQL backend live and running on port ${PORT}`);
});