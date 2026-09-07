const express = require('express');
const passport = require('passport');
const { getMe, logout, googleCallback } = require('../controllers/authController');
const { requireAuth } = require('../middleware/auth');

const router = express.Router();

// Initiate Google OAuth login
// GET /api/auth/google
router.get(
  '/google',
  passport.authenticate('google', { scope: ['profile', 'email'], session: false })
);

// Google OAuth callback
// GET /api/auth/google/callback
router.get(
  '/google/callback',
  passport.authenticate('google', {
    failureRedirect: `${process.env.CLIENT_URL}/login?error=auth_failed`,
    session: false,
  }),
  googleCallback
);

// Get current authenticated user
// GET /api/auth/me
router.get('/me', requireAuth, getMe);

// Logout
// POST /api/auth/logout
router.post('/logout', requireAuth, logout);

module.exports = router;
