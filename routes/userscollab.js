const mongoose = require('mongoose');

const userCollabSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User', // Reference to the User model
        unique:true,
        required: true
    },
    fullName: {
        type: String,
        required: true
    },
    relationshipToUser: {
        type: String,
        required: true
    },
    age: {
        type: Number,
        required: true
    },
    occupation: {
        type: String,
        required: false // Optional field
    },
    annualIncome: {
        type: Number,
        required: true
    },
    medicalExpenses: {
        type: Number,
        required: true
    },
    lifestyleExpenses: {
        type: Number,
        required: true
    },
    riskProfiling: {
        type: String,
        enum: ['Conservative', 'Moderate', 'Aggressive'],
        required: true
    },
    investmentGoals: {
        type: String,
        required: false // Optional field
    },
    currentInvestments: {
        type: String,
        required: false // Optional field
    }
});

// Create the UserCollab model
const UserCollab = mongoose.model('UserCollab', userCollabSchema);

module.exports = UserCollab;
