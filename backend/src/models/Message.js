const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema(
  {
    chatId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Chat',
      required: true,
    },
    userId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    role: {
      type: String,
      enum: ['user', 'assistant'],
      required: true,
    },
    content: {
      type: String,
      required: true,
    },
    // Optional: populated on assistant messages that carry AI recommendation results.
    // Mixed type preserves any shape from FastAPI without a rigid sub-schema.
    // Absent on plain text messages — backward compatible.
    recommendations: {
      type: [mongoose.Schema.Types.Mixed],
      default: undefined,
    },
    extractedRequirements: {
      type: mongoose.Schema.Types.Mixed,
      default: undefined,
    },
  },
  {
    timestamps: { createdAt: 'createdAt', updatedAt: false },
  }
);

module.exports = mongoose.model('Message', messageSchema);
