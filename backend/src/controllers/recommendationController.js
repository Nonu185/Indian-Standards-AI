const { getRecommendations } = require('../services/ai/fastapiService');

const recommend = async (req, res) => {
  try {
    const { text } = req.body;

    if (!text || text.trim() === '') {
      return res.status(400).json({ error: 'Requirement text is required.' });
    }

    // Forward natural language requirement to FastAPI AI service
    const aiResponse = await getRecommendations(text.trim());

    // Send the recommendation payload directly to the client
    res.status(200).json(aiResponse);
  } catch (error) {
    console.error('Recommendation Controller Error:', error.message);
    // Graceful degradation without exposing Python/Ollama specifics
    res.status(503).json({ 
      error: 'The AI Recommendation Service is currently unavailable. Please try again later.' 
    });
  }
};

module.exports = { recommend };
