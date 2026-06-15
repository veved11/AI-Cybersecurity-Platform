async function login() {

    const email =
        document.getElementById("email").value;

    const password =
        document.getElementById("password").value;

    const response = await fetch(
        "http://127.0.0.1:8000/login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password
            })
        }
    );

    const result = await response.json();

    if (response.ok) {

        localStorage.setItem(
            "token",
            result.access_token
        );

        document.getElementById(
            "login-result"
        ).innerHTML = `
            <div class="alert alert-success">
                Login Successful
            </div>
        `;

        setTimeout(() => {

            window.location.href = "/";

        }, 1000);

    } else {

        document.getElementById(
            "login-result"
        ).innerHTML = `
            <div class="alert alert-danger">
                Invalid Email or Password
            </div>
        `;
    }
}