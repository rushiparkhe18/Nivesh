var express = require('express');
var router = express.Router();

const passport = require('passport');

const userModel = require('./users');
const UserDetails = require('./userdetails');
const UserCollab = require('./userscollab')


const localStrategy = require("passport-local");
passport.use(new localStrategy(userModel.authenticate()));


router.get("/", (req, res) => {
  const successMessage = req.session.successMessage;
  const errorMessage = req.session.errorMessage;

  delete req.session.successMessage;
  delete req.session.errorMessage;

  res.render("index", {
    successMessage,
    errorMessage,
    user: req.user // `req.user` contains the authenticated user object if logged in
  });
});
router.get("/test", (req, res) => {
  const successMessage = req.session.successMessage;
  const errorMessage = req.session.errorMessage;

  delete req.session.successMessage;
  delete req.session.errorMessage;

  // Pass the authenticated user (if any) to the template
  res.render("index2", {
    successMessage,
    errorMessage,
    user: req.user // `req.user` contains the authenticated user object if logged in
  });
});


router.get('/login', function (req, res, next) {
  res.render('login', { error: req.flash('error') });
});

router.get('/register', function (req, res, next) {
  res.render('register', { message: req.flash('error') });
});


// Authentication
router.post("/register", async function (req, res, next) {
  const userData = await new userModel({
    username: req.body.username,
    email: req.body.email,
    role: req.body.role,
  });
  userModel.register(userData, req.body.password)
    .then(function () {
      passport.authenticate("local")(req, res, function () {
          req.session.successMessage = 'Registered successfully!';
          res.redirect("/");
      })
    })
})

router.post("/login", function (req, res, next) {
  passport.authenticate("local", function (err, user, info) {
    if (err) {
      return next(err);
    }
    if (!user) {
      req.session.errorMessage = 'Invalid username or password.';
      return res.redirect('/');
    }
    req.logIn(user, function (err) {
      if (err) {
        return next(err);
      }
      req.session.successMessage = 'Logged in successfully!';
      return res.redirect('/');
    });
  })(req, res, next);
});


router.get("/logout", function (req, res) {
  req.logout(function (err) {
    if (err) {
      console.error("Error logging out:", err);
      req.session.errorMessage = 'Error logging out!';
    } else {
      req.session.successMessage = 'Logged out successfully!';
    }
    res.redirect('/');
  });
});

function isLoggedIn(req, res, next) {
  if (req.isAuthenticated()) {
    res.locals.user = req.user; // Make user available in views
    return next();
  }
  next(); // Continue to the next middleware or route
}
/////////////////////////////////////////////////////////////////////////

router.get('/dashboard', isLoggedIn, async function (req, res, next) {
  try {
    const userId = req.user._id; // Assuming the logged-in user ID is stored in req.user
    const userDetails = await UserDetails.findOne({ userId });

    // If user details are not found, you might want to handle that accordingly
    if (!userDetails) {
      return res.render('dashboard/dashboard', { path: '/dashboard', insights: null });
    }

    // Prepare data for insights
    const salary = userDetails.salary || 0;
    const medicalExpenses = userDetails.medicalExpenses || 0;
    const loanEMI = userDetails.loanEmi || 0;
    const lifestyleExpenses = userDetails.lifestyleExpenses || 0;
    const savings = userDetails.savings || 0;

    // Calculate total expenses and savings distribution
    const investment = savings * 0.8; // 80% for investments
    const emergency = savings * 0.2; // 20% for emergencies

    // Pass insights to the template
    res.render('dashboard/dashboard', {
      path: '/dashboard',
      userdetails: userDetails,
      insights: {
        salary,
        medicalExpenses,
        loanEMI,
        lifestyleExpenses,
        investment,
        emergency,
      },
    });
  } catch (error) {
    console.error(error);
    res.status(500).send('Server Error');
  }
});


/////////////////////////////////////////////////////////////////////////
// USER INPUT SECION 
router.get('/details', isLoggedIn, function (req, res, next) {
  res.render('details', { path: '/details' });
});

router.post('/userdetails', async (req, res) => {
  try {
      // Create a new UserDetails entry
      const userDetails = new UserDetails({
          user: req.user._id, // Reference to the logged-in user
          name: req.body.name,
          education: req.body.education,
          salary: req.body.salary,
          age: req.body.age,
          medicalEmergencies: req.body.medicalEmergencies,
          medicalAllotments: req.body.medicalAllotments,
          workSector: req.body.workSector,
          jobSecurity: req.body.jobSecurity,
          familyMembers: req.body.familyMembers,
          otherExpenses: req.body.otherExpenses,
          riskTolerance: req.body.riskTolerance,
          goal: req.body.goal,
      });
      
      // Save UserDetails
      await userDetails.save();
      
      // Link userDetails with the user (if you need to)
      await userModel.findByIdAndUpdate(req.user._id, { userDetails: userDetails._id });

      req.session.successMessage = 'Form submitted successfully!';
      res.redirect('/');
  } catch (error) {
      console.error("Error occurred while saving user details:", error); // Log the actual error
      req.session.errorMessage = 'Form submission failed! ' + error.message; // Include error message
      res.redirect('/');
  }
});

//////////////////////////////////////////////////////////////////////////////////////////////////
// Dashboard Profile
router.get('/dashboard-profile', async (req, res) => {
  try {
    const userId = req.user._id; // Get the logged-in user's ID
    const userDetails = await UserDetails.findOne({ userId });

    // Render the dashboard profile view, passing the userDetails
    res.render('dashboard/dashboard-profile', { userdetails: userDetails || null, path: '/dashboard-profile' });
  } catch (error) {
    console.error(error);
    res.status(500).send('Server Error');
  }
});


router.post('/dashboard-profile/update', async (req, res) => {
  try {
    const userId = req.user._id; // Assuming the logged-in user ID is stored in req.user

    // Destructure the fields from the request body to ensure only valid fields are updated
    const {
      name,
      education,
      salary,
      age,
      medicalAllotments,
      medicalExpenses,
      loanEmi,
      lifestyleExpenses,
      savings,
      workSector,
      riskTolerance
    } = req.body;

    // Validate the required fields (you can add more validation if needed)
    if (!name || !education || !salary || !age) {
      return res.status(400).send('Missing required fields');
    }

    // Check if user details already exist
    let userDetails = await UserDetails.findOne({ userId });

    if (userDetails) {
      // Update existing user details
      userDetails = await UserDetails.findByIdAndUpdate(
        userDetails._id,
        {
          name,
          education,
          salary,
          age,
          medicalAllotments,
          medicalExpenses,
          loanEmi,
          lifestyleExpenses,
          savings,
          workSector,
          riskTolerance
        },
        { new: true }
      );
    } else {
      // Create new user details
      userDetails = new UserDetails({
        userId,
        name,
        education,
        salary,
        age,
        medicalAllotments,
        medicalExpenses,
        loanEmi,
        lifestyleExpenses,
        savings,
        workSector,
        riskTolerance
      });
      await userDetails.save();
    }

    // Redirect to profile page after updating/creating
    res.render('dashboard/dashboard-profile', { userdetails: userDetails, path: '/dashboard-profile' });
  } catch (error) {
    // Log detailed error message and stack trace
    console.error('Error updating user details:', error.message, error.stack);

    // Send generic error message to the client
    res.status(500).send('Server Error');
  }
});


//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Dashboard BLOG
router.get('/dashboard-community', async (req, res) => {
  try {
      // Render the dashboard profile view, passing the userDetails
      res.render('dashboard/dashboard-community', { path: '/dashboard-community' });
  } catch (error) {
      console.error(error);
      res.status(500).send('Server Error');
  }
});

router.get('/dashboard-predict', function (req, res, next) {
  res.render('dashboard/dashboard-predict',{path:'dashboard/dashboard-predict'});
});
router.get('/testingb', function (req, res, next) {
  res.render('testingb');
});
router.get('/testinga', function (req, res, next) {
  res.render('testinga');
});
router.get('/pages', function (req, res, next) {
  res.render('pages');
});
router.get('/faq', function (req, res, next) {
  res.render('faq');
});
router.get('/dashboard-collab', async (req, res) => {
  try {
      // Ensure user is logged in
      if (!req.user || !req.user._id) {
          return res.redirect('/login'); // Redirect to login if not authenticated
      }
      
      const userId = req.user._id; // Get the logged-in user's ID
      const userCollab = await UserCollab.findOne({ userId });

      // Render the dashboard profile view, passing the userCollab
      res.render('dashboard/dashboard-collab', { userdetails: userCollab || null, path: '/dashboard-collab' });
  } catch (error) {
      console.error(error);
      res.status(500).send('Server Error');
  }
});

router.post('/dashboard-collab/update', async (req, res) => {
  try {
      // Ensure user is logged in
      if (!req.user || !req.user._id) {
          return res.redirect('/login'); // Redirect to login if not authenticated
      }
      
      const userId = req.user._id; // Get the logged-in user's ID
      const { fullName, relationshipToUser, age, occupation, annualIncome, medicalExpenses, lifestyleExpenses, riskProfiling, investmentGoals, currentInvestments } = req.body;

      // Check if collaboration details already exist for the user
      let userCollab = await UserCollab.findOne({ userId });

      if (userCollab) {
          // Update existing collaboration details
          userCollab.fullName = fullName;
          userCollab.relationshipToUser = relationshipToUser;
          userCollab.age = age;
          userCollab.occupation = occupation;
          userCollab.annualIncome = annualIncome;
          userCollab.medicalExpenses = medicalExpenses;
          userCollab.lifestyleExpenses = lifestyleExpenses;
          userCollab.riskProfiling = riskProfiling;
          userCollab.investmentGoals = investmentGoals;
          userCollab.currentInvestments = currentInvestments;

          await userCollab.save();
      } else {
          // Create new collaboration details
          userCollab = new UserCollab({
              userId,
              fullName,
              relationshipToUser,
              age,
              occupation,
              annualIncome,
              medicalExpenses,
              lifestyleExpenses,
              riskProfiling,
              investmentGoals,
              currentInvestments
          });

          await userCollab.save();
      }

      // Redirect or respond after successful update/create
      res.redirect('/dashboard-collab'); // Redirect back to the dashboard-collab page
  } catch (error) {
      console.error(error);
      res.status(500).send('Server Error');
  }
});



module.exports = router;