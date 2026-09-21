/* =====================================================
   HIREIQ API
===================================================== */

const API_URL = "/api";


/* =====================================================
   PAGE ELEMENTS
===================================================== */

const loginPage = document.getElementById("loginPage");
const registerPage = document.getElementById("registerPage");
const dashboardPage = document.getElementById("dashboardPage");


/* =====================================================
   SHOW LOGIN
===================================================== */

function showLogin() {
    loginPage.classList.remove("hidden");
    registerPage.classList.add("hidden");
    dashboardPage.classList.add("hidden");
}


/* =====================================================
   SHOW REGISTER
===================================================== */

function showRegister() {
    loginPage.classList.add("hidden");
    registerPage.classList.remove("hidden");
    dashboardPage.classList.add("hidden");
}


/* =====================================================
   SHOW DASHBOARD
===================================================== */

function showDashboard() {
    loginPage.classList.add("hidden");
    registerPage.classList.add("hidden");
    dashboardPage.classList.remove("hidden");
}


/* =====================================================
   SAFE API RESPONSE
===================================================== */

async function getResponseData(response) {

    const text = await response.text();

    if (!text) {
        return {};
    }

    try {
        return JSON.parse(text);
    } catch (error) {

        console.error(
            "Server returned non-JSON response:",
            text
        );

        return {
            error: text
        };
    }
}


/* =====================================================
   REGISTER USER
===================================================== */

async function registerUser() {

    const name =
        document
            .getElementById("registerName")
            .value
            .trim();

    const email =
        document
            .getElementById("registerEmail")
            .value
            .trim();

    const password =
        document
            .getElementById("registerPassword")
            .value;

    const status =
        document.getElementById("registerStatus");


    /* Check fields */

    if (!name || !email || !password) {

        status.innerText =
            "Please fill all fields.";

        return;
    }


    /* Check password */

    if (password.length < 6) {

        status.innerText =
            "Password must contain at least 6 characters.";

        return;
    }


    status.innerText =
        "Creating account...";


    try {

        const response =
            await fetch(
                `${API_URL}/register`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        name: name,
                        email: email,
                        password: password
                    })
                }
            );


        const data =
            await getResponseData(response);


        /* Backend error */

        if (!response.ok) {

            status.innerText =
                data.detail ||
                data.error ||
                `Registration failed (${response.status}).`;

            console.error(
                "REGISTER SERVER ERROR:",
                data
            );

            return;
        }


        /* Save JWT */

        localStorage.setItem(
            "hireiq_token",
            data.token
        );


        /* Go to dashboard */

        showDashboard();


        document
            .getElementById("welcomeUser")
            .innerText =
            `Welcome, ${name} 👋`;

    }


    catch (error) {

        console.error(
            "REGISTER ERROR:",
            error
        );

        status.innerText =
            "Cannot connect to HireIQ backend.";
    }
}


/* =====================================================
   LOGIN USER
===================================================== */

async function loginUser() {

    const email =
        document
            .getElementById("loginEmail")
            .value
            .trim();

    const password =
        document
            .getElementById("loginPassword")
            .value;

    const status =
        document.getElementById("loginStatus");


    /* Check fields */

    if (!email || !password) {

        status.innerText =
            "Please enter email and password.";

        return;
    }


    status.innerText =
        "Logging in...";


    try {

        const response =
            await fetch(
                `${API_URL}/login`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );


        const data =
            await getResponseData(response);


        /* Login failed */

        if (!response.ok) {

            status.innerText =
                data.detail ||
                data.error ||
                `Login failed (${response.status}).`;

            console.error(
                "LOGIN SERVER ERROR:",
                data
            );

            return;
        }


        /* Save JWT token */

        localStorage.setItem(
            "hireiq_token",
            data.token
        );


        /* Show dashboard */

        showDashboard();


        document
            .getElementById("welcomeUser")
            .innerText =
            `Welcome back, ${data.user.name} 👋`;

    }


    catch (error) {

        console.error(
            "LOGIN ERROR:",
            error
        );

        status.innerText =
            "Cannot connect to HireIQ backend.";
    }
}


/* =====================================================
   LOAD CURRENT USER
===================================================== */

async function loadUser() {

    const token =
        localStorage.getItem(
            "hireiq_token"
        );


    /* No token */

    if (!token) {

        showLogin();

        return;
    }


    try {

        const response =
            await fetch(
                `${API_URL}/me`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    }
                }
            );


        /* Token invalid */

        if (!response.ok) {

            localStorage.removeItem(
                "hireiq_token"
            );

            showLogin();

            return;
        }


        const user =
            await getResponseData(response);


        document
            .getElementById("welcomeUser")
            .innerText =
            `Welcome back, ${user.name} 👋`;


        showDashboard();

    }


    catch (error) {

        console.error(
            "USER ERROR:",
            error
        );

        localStorage.removeItem(
            "hireiq_token"
        );

        showLogin();
    }
}


/* =====================================================
   LOGOUT
===================================================== */

function logoutUser() {

    localStorage.removeItem(
        "hireiq_token"
    );


    /* Clear old results */

    const results =
        document.getElementById(
            "results"
        );


    if (results) {

        results.classList.add(
            "hidden"
        );
    }


    /* Clear fields */

    document
        .getElementById("jobRole")
        .value = "";


    document
        .getElementById("resume")
        .value = "";


    showLogin();
}


/* =====================================================
   ANALYZE RESUME
===================================================== */

async function analyzeResume() {

    /* Get login token */

    const token =
        localStorage.getItem(
            "hireiq_token"
        );


    /* User not logged in */

    if (!token) {

        showLogin();

        return;
    }


    const resume =
        document
            .getElementById("resume")
            .files[0];


    const jobRole =
        document
            .getElementById("jobRole")
            .value
            .trim();


    const status =
        document.getElementById(
            "status"
        );


    /* Check resume */

    if (!resume) {

        status.innerText =
            "Please upload a PDF resume.";

        return;
    }


    /* Check job role */

    if (!jobRole) {

        status.innerText =
            "Please enter a target job role.";

        return;
    }


    /* Check PDF */

    if (
        !resume.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        status.innerText =
            "Please upload a PDF file.";

        return;
    }


    status.innerText =
        "Analyzing resume with AI... ✨";


    /* Create form */

    const formData =
        new FormData();


    formData.append(
        "resume",
        resume
    );


    formData.append(
        "job_role",
        jobRole
    );


    try {

        const response =
            await fetch(
                `${API_URL}/analyze`,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${token}`
                    },

                    body: formData
                }
            );


        const data =
            await getResponseData(response);


        /* Authentication expired */

        if (response.status === 401) {

            localStorage.removeItem(
                "hireiq_token"
            );

            showLogin();

            return;
        }


        /* Backend error */

        if (!response.ok) {

            status.innerText =
                data.detail ||
                data.error ||
                `Something went wrong (${response.status}).`;

            console.error(
                "ANALYZE SERVER ERROR:",
                data
            );

            return;
        }


        if (data.error) {

            status.innerText =
                data.error;

            return;
        }


        /* Display results */

        displayResults(data);


        status.innerText =
            "Analysis complete! ✨";

    }


    catch (error) {

        console.error(
            "ANALYZE ERROR:",
            error
        );

        status.innerText =
            "Cannot connect to HireIQ backend.";
    }
}


/* =====================================================
   DISPLAY RESULTS
===================================================== */

function displayResults(data) {

    document
        .getElementById("results")
        .classList
        .remove("hidden");


    document
        .getElementById("score")
        .innerText =
        data.ats_score ?? 0;


    document
        .getElementById("summary")
        .innerText =
        data.summary || "";


    displaySkills(
        "matchedSkills",
        data.matched_skills || []
    );


    displaySkills(
        "missingSkills",
        data.missing_skills || []
    );


    displayList(
        "strengths",
        data.strengths || []
    );


    displayList(
        "weaknesses",
        data.weaknesses || []
    );


    displayList(
        "suggestions",
        data.suggestions || []
    );
}


/* =====================================================
   DISPLAY SKILLS
===================================================== */

function displaySkills(id, skills) {

    const container =
        document.getElementById(id);


    if (!container) {
        return;
    }


    container.innerHTML = "";


    skills.forEach(
        skill => {

            const span =
                document.createElement(
                    "span"
                );


            span.className =
                "skill";


            span.innerText =
                skill;


            container.appendChild(
                span
            );
        }
    );
}


/* =====================================================
   DISPLAY LIST
===================================================== */

function displayList(id, items) {

    const list =
        document.getElementById(id);


    if (!list) {
        return;
    }


    list.innerHTML = "";


    items.forEach(
        item => {

            const li =
                document.createElement(
                    "li"
                );


            li.innerText =
                item;


            list.appendChild(
                li
            );
        }
    );
}


/* =====================================================
   CHECK LOGIN ON PAGE LOAD
===================================================== */

window.addEventListener(
    "DOMContentLoaded",
    () => {

        const token =
            localStorage.getItem(
                "hireiq_token"
            );


        if (token) {

            loadUser();

        }

        else {

            showLogin();

        }
    }
);