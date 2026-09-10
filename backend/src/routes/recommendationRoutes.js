const express = require('express');
const { recommend } = require('../controllers/recommendationController');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

router.post('/', recommend);

module.exports = router;
