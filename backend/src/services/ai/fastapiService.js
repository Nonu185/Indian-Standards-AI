const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000';

async function getRecommendations(text) {
  try {
    const response = await fetch(`${FASTAPI_URL}/recommend`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      throw new Error(`FastAPI responded with status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error communicating with FastAPI AI service:', error.message);
    throw new Error('AI recommendation service is currently unavailable.');
  }
}

module.exports = { getRecommendations };
