const mongoose = require('mongoose');
const plm = require("passport-local-mongoose");

mongoose.connect("mongodb://127.0.0.1:27017/vcethack");

const userSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        lowercase: true
    },
    email: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        lowercase: true
    },
    password: {
        type: String,
    },
    userDetails: { type: mongoose.Schema.Types.ObjectId, ref: 'UserDetails' }, // Reference to UserDetails
    userCollab: { type: mongoose.Schema.Types.ObjectId, ref: 'UserCollab' } // Reference to UserDetails
});

userSchema.plugin(plm);

module.exports = mongoose.model('User', userSchema);
