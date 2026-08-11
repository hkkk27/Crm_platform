const POPUP_SUCCESS_AUTO_CLOSE_MS = 10000;
const POPUP_INFO_AUTO_CLOSE_MS = 10000;
const POPUP_ERROR_AUTO_CLOSE_MS = 0;
const POPUP_MIN_LOADING_MS = 5000;

let appPopupLoadingStartedAt = 0;

function getPopupType(message) {
    const text = String(message).toLowerCase();

    if (
        text.includes("invalid") ||
        text.includes("not found") ||
        text.includes("unable") ||
        text.includes("failed") ||
        text.includes("error") ||
        text.includes("do not match") ||
        text.includes("inactive") ||
        text.includes("denied") ||
        text.includes("issue")
    ) {
        return "error";
    }

    if (
        text.includes("success") ||
        text.includes("sent") ||
        text.includes("updated") ||
        text.includes("verified") ||
        text.includes("redirecting")
    ) {
        return "success";
    }

    return "info";
}

function getPopupTitle(type) {
    if (type === "error") return "Attention";
    if (type === "success") return "Success";
    if (type === "warning") return "Warning";
    return "Message";
}

function getPopupIcon(type) {
    if (type === "error") return "!";
    if (type === "success") return "✓";
    if (type === "warning") return "!";
    return "i";
}

function getAutoCloseTime(type, options) {
    if (typeof options.autoCloseMs === "number") {
        return options.autoCloseMs;
    }

    if (type === "error") return POPUP_ERROR_AUTO_CLOSE_MS;
    if (type === "success") return POPUP_SUCCESS_AUTO_CLOSE_MS;

    return POPUP_INFO_AUTO_CLOSE_MS;
}

function escapePopupHTML(value) {
    return String(value || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getRadialLoaderHTML() {
    return `
        <div class="app-radial-loader" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
}

function getLoaderDotsHTML() {
    return `
        <div class="app-loader-dots" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
}

function getPopupLayoutHTML() {
    return `
        <div class="app-popup-box" role="dialog" aria-modal="true">
            <div class="app-popup-header">
                <div class="app-popup-title-wrap">
                    <span class="app-popup-icon">i</span>
                    <span class="app-popup-title">Message</span>
                </div>
                <button type="button" class="app-popup-close" aria-label="Close popup">×</button>
            </div>

            <div class="app-popup-body"></div>

            <div class="app-popup-footer">
                <button type="button" class="app-popup-ok">OK</button>
            </div>
        </div>
    `;
}

function ensurePopupRoot() {
    let root = document.getElementById("appPopupRoot");

    if (root) {
        if (!root.querySelector(".app-popup-box")) {
            root.innerHTML = getPopupLayoutHTML();
        }

        return root;
    }

    root = document.createElement("div");
    root.id = "appPopupRoot";
    root.className = "app-popup-overlay";
    root.innerHTML = getPopupLayoutHTML();

    document.body.appendChild(root);

    return root;
}

function showAppPopup(message, options = {}) {
    return new Promise(function (resolve) {
        const root = ensurePopupRoot();

        const box = root.querySelector(".app-popup-box");
        const icon = root.querySelector(".app-popup-icon");
        const title = root.querySelector(".app-popup-title");
        const body = root.querySelector(".app-popup-body");
        const closeBtn = root.querySelector(".app-popup-close");
        const okBtn = root.querySelector(".app-popup-ok");
        const header = root.querySelector(".app-popup-header");
        const footer = root.querySelector(".app-popup-footer");

        const type = options.type || getPopupType(message);
        const autoCloseMs = getAutoCloseTime(type, options);

        if (header) header.style.display = "flex";
        if (footer) footer.style.display = "flex";

        box.className = "app-popup-box";
        box.classList.add(`app-popup-${type}`);

        icon.textContent = getPopupIcon(type);
        title.textContent = options.title || getPopupTitle(type);

        body.innerHTML = `
            <div class="app-popup-content-stack">
                ${getRadialLoaderHTML()}
                <div class="app-popup-message-text">${escapePopupHTML(message)}</div>
                ${getLoaderDotsHTML()}
            </div>
        `;

        let autoCloseTimer = null;

        function closePopup() {
            if (autoCloseTimer) {
                clearTimeout(autoCloseTimer);
            }

            root.classList.remove("active");
            resolve();
        }

        closeBtn.onclick = closePopup;
        okBtn.onclick = closePopup;

        root.classList.add("active");
        okBtn.focus();

        /*
            Error popups do not auto-close.
            Invalid email/password requires user to click OK.
        */
        if (autoCloseMs > 0) {
            autoCloseTimer = setTimeout(function () {
                closePopup();
            }, autoCloseMs);
        }
    });
}

function showLoadingPopup(message = "Loading...") {
    const root = ensurePopupRoot();

    const box = root.querySelector(".app-popup-box");
    const body = root.querySelector(".app-popup-body");
    const header = root.querySelector(".app-popup-header");
    const footer = root.querySelector(".app-popup-footer");

    appPopupLoadingStartedAt = Date.now();

    if (header) header.style.display = "none";
    if (footer) footer.style.display = "none";

    box.className = "app-popup-box app-popup-loading app-popup-info";

    body.innerHTML = `
        <div class="app-popup-content-stack">
            ${getRadialLoaderHTML()}
            <div class="app-popup-message-text">${escapePopupHTML(message)}</div>
            ${getLoaderDotsHTML()}
        </div>
    `;

    root.classList.add("active");
}

function hideLoadingPopup() {
    const root = document.getElementById("appPopupRoot");

    if (!root) return;

    const elapsedTime = Date.now() - appPopupLoadingStartedAt;
    const remainingTime = Math.max(0, POPUP_MIN_LOADING_MS - elapsedTime);

    setTimeout(function () {
        root.classList.remove("active");
    }, remainingTime);
}

/* Make popup functions available everywhere */
window.showAppPopup = showAppPopup;
window.showLoadingPopup = showLoadingPopup;
window.hideLoadingPopup = hideLoadingPopup;

/* Global alert override */
window.nativeAlert = window.alert;

window.alert = function (message) {
    window.showAppPopup(message);
};