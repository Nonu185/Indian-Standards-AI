const { Mistral } = require('@mistralai/mistralai');

const apiKey = process.env.MISTRAL_API_KEY;
// Initialize the client if the API key is present
const client = apiKey ? new Mistral({ apiKey }) : null;

/**
 * Generates a concise title for a chat based on the user's first message.
 * @param {string} message - The first user message in the chat
 * @returns {Promise<string|null>} - The generated title or null if an error occurred
 */
const generateChatTitle = async (message) => {
  if (!client) {
    console.warn('MISTRAL_API_KEY is not configured. Skipping title generation.');
    return null;
  }

  try {
    const prompt = `Generate a concise 3-6 word title for a conversation that starts with the following message.
Rules:
- Do not use quotation marks.
- Do not use unnecessary punctuation.
- Do not include prefixes like "Chat about", "Conversation about".
- Only return the title itself.

Message: "${message}"`;

    const chatResponse = await client.chat.complete({
      model: 'mistral-small-latest',
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3,
    });

    let title = chatResponse.choices[0].message.content.trim();
    // Clean up any surrounding quotes or newlines Mistral might have included
    title = title.replace(/^["']|["']$/g, '').trim();

    return title;
  } catch (error) {
    console.error('Mistral Title Generation Error:', error.message || error);
    return null;
  }
};

module.exports = { generateChatTitle };
