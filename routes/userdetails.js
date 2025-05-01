const mongoose = require('mongoose');

const UserDetailsSchema = new mongoose.Schema({
    userId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        unique: true, // Ensure one detail record per user
        required: true,
    },
    name: { type: String, required: true },
    education: { type: String, required: true },
    salary: { type: Number, required: true }, // Salary in ₹
    age: { type: Number, required: true },
    medicalAllotments: { type: Number, required: true }, // Number of medical allotments
    medicalExpenses: { type: Number, required: true }, // Total medical expenses in ₹
    loanEmi: { type: Number, required: true }, // Loan EMI in ₹
    lifestyleExpenses: { type: Number, required: true }, // Lifestyle expenses in ₹
    savings: { type: Number, required: true }, // Savings in ₹
    workSector: { type: String, required: true },
    riskTolerance: { type: String, required: true } // Risk tolerance
});

const UserDetails = mongoose.model('UserDetails', UserDetailsSchema);
module.exports = UserDetails;
