const express = require('express');
const cors = require('cors');
const fetch = (...args) => import('node-fetch').then(({default: f}) => f(...args));

const app = express();
const BOT_TOKEN = process.env.BOT_TOKEN || '8916800325:AAEPAHaUDwMJs6WhoTjwmL13W88h7KzS20Y';
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Health check
app.get('/', (req, res) => {
  res.json({ status: 'ok', service: 'CLOUDE VIP API' });
});

// Get user profile photo
app.get('/api/photo/:userId', async (req, res) => {
  try {
    const userId = req.params.userId;

    // Get user profile photos
    const photosRes = await fetch(
      `https://api.telegram.org/bot${BOT_TOKEN}/getUserProfilePhotos?user_id=${userId}&limit=1`
    );
    const photosData = await photosRes.json();

    if (!photosData.ok || photosData.result.total_count === 0) {
      return res.json({ photo: null });
    }

    // Get file_id of smallest photo
    const fileId = photosData.result.photos[0][0].file_id;

    // Get file path
    const fileRes = await fetch(
      `https://api.telegram.org/bot${BOT_TOKEN}/getFile?file_id=${fileId}`
    );
    const fileData = await fileRes.json();

    if (!fileData.ok) {
      return res.json({ photo: null });
    }

    const photoUrl = `https://api.telegram.org/file/bot${BOT_TOKEN}/${fileData.result.file_path}`;
    res.json({ photo: photoUrl });

  } catch (err) {
    console.error(err);
    res.json({ photo: null });
  }
});

app.listen(PORT, () => {
  console.log(`CLOUDE VIP API running on port ${PORT}`);
});
