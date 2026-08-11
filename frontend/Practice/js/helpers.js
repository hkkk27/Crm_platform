function badge(text, type = "") {
  return `<span class="badge ${type}">${text}</span>`;
}

function money(value) {
  return "₹" + value.toLocaleString("en-IN");
}

function getAssetPath(fileName) {
  const path = window.location.pathname.toLowerCase();

  // Pages inside /pages/ need ../ to reach root assets.
  if (path.includes("/pages/")) {
    return `../${fileName}`;
  }

  // Root pages like login.html / forgot-password.html use direct asset path.
  return fileName;
}