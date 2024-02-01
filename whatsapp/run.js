const { Client } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const client = new Client({
    puppeteer: {
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        headless: true
    }
});

client.on('qr', (qr) => {
    console.log('QR Code received, scan it with your phone.');
    qrcode.generate(qr, { small: false });
});

client.on('ready', () => {
    console.log('Client is ready!');
});

client.initialize();

app.post('/send-message', async (req, res) => {
    const { number, text } = req.body;
    console.log(req.body); // the posted data

    if (!number || !text) {
        return res.status(400).json({ error: 'Missing number or text' });
    }

    try {
        await client.sendMessage(`${number}@c.us`, text, { linkPreview: false });

        console.log(`Message sent to ${number}: ${text}`);
        res.status(200).json({ success: 'Message sent' });
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).json({ error: 'Error sending message' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
