const API_BASE_URL = window.API_BASE_URL || "http://127.0.0.1:8000";

let forgotPasswordEmail = "";
let forgotPasswordResetCode = "";

async function postJson(endpoint, body) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });

    const result = await response.json().catch(function () {
        return { detail: "Invalid server response" };
    });

    if (!response.ok) {
        throw new Error(result.detail || result.message || "Request failed");
    }

    return result;
}

function setButtonLoading(button, isLoading, loadingText, normalText) {
    if (!button) return;
    button.disabled = isLoading;
    button.textContent = isLoading ? loadingText : normalText;
}

function showScreen(currentScreen, nextScreen) {
    currentScreen.classList.add("hidden");
    nextScreen.classList.remove("hidden");
}

/* Popup loading helper - frontend only, no backend logic change */
function showPageLoading(message) {
    if (typeof window.showLoadingPopup === "function") {
        window.showLoadingPopup(message);
    }
}

function hidePageLoading() {
    if (typeof window.hideLoadingPopup === "function") {
        window.hideLoadingPopup();
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const emailScreen = document.getElementById("emailScreen");
    const otpScreen = document.getElementById("otpScreen");
    const passwordScreen = document.getElementById("passwordScreen");
    const successScreen = document.getElementById("successScreen");

    const sendCodeBtn = document.getElementById("sendCodeBtn");
    const verifyOtpBtn = document.getElementById("verifyOtpBtn");
    const updatePasswordBtn = document.getElementById("updatePasswordBtn");

    sendCodeBtn.addEventListener("click", async function () {
        const email = document.getElementById("registeredEmail").value.trim().toLowerCase();

        if (!email) {
            alert("Enter your registered email.");
            return;
        }

        try {
            setButtonLoading(sendCodeBtn, true, "Sending...", "Send Reset Code");
            showPageLoading("Sending reset code...");

            await postJson("/auth/forgot-password/request", {
                email: email
            });

            hidePageLoading();

            forgotPasswordEmail = email;
            alert("A reset code has been sent.");
            showScreen(emailScreen, otpScreen);
        } catch (error) {
            hidePageLoading();
            alert(error.message || "Unable to send reset code.");
        } finally {
            setButtonLoading(sendCodeBtn, false, "Sending...", "Send Reset Code");
        }
    });

    verifyOtpBtn.addEventListener("click", function () {
        const otp = document.getElementById("otpCode").value.trim();

        if (!otp) {
            alert("Please enter OTP.");
            return;
        }

        forgotPasswordResetCode = otp;
        showScreen(otpScreen, passwordScreen);
    });

    updatePasswordBtn.addEventListener("click", async function () {
        const newPassword = document.getElementById("newPassword").value.trim();
        const confirmPassword = document.getElementById("confirmPassword").value.trim();

        if (!forgotPasswordEmail) {
            alert("Please request a reset code again.");
            showScreen(passwordScreen, emailScreen);
            return;
        }

        if (!forgotPasswordResetCode) {
            alert("Please enter the reset code again.");
            showScreen(passwordScreen, otpScreen);
            return;
        }

        if (!newPassword) {
            alert("Please enter new password.");
            return;
        }

        if (!confirmPassword) {
            alert("Please confirm your password.");
            return;
        }

        if (newPassword.length < 8) {
            alert("Password must be at least 8 characters long.");
            return;
        }

        if (newPassword !== confirmPassword) {
            alert("Passwords do not match.");
            return;
        }

        try {
            setButtonLoading(updatePasswordBtn, true, "Updating...", "Update Password");
            showPageLoading("Updating password...");

            await postJson("/auth/forgot-password/reset", {
                email: forgotPasswordEmail,
                reset_code: forgotPasswordResetCode,
                new_password: newPassword
            });

            hidePageLoading();

            showScreen(passwordScreen, successScreen);

            setTimeout(function () {
                window.location.href = "login.html";
            }, 2000);
        } catch (error) {
            hidePageLoading();
            alert(error.message || "Unable to update password.");
        } finally {
            setButtonLoading(updatePasswordBtn, false, "Updating...", "Update Password");
        }
    });
});