function renderSettingsPage() {
  const profile = getSettingsProfile();
  const avatar = getInitials(profile.name);

  setText("settingsAvatar", avatar);
  setText("settingsName", profile.name);
  setText("settingsEmail", profile.email);
  setText("settingsRole", profile.role);
  setText("profileName", profile.name);
  setText("profileEmail", profile.email);
  setText("profileRole", profile.role);
  setText("profilePhone", profile.phone);
  setText("accountEmail", profile.email);
  setText("accountRole", profile.role);
}

function getSettingsProfile() {
  let session = null;

  try {
    session = JSON.parse(localStorage.getItem("crm_session") || "null");
  } catch (error) {
    session = null;
  }

  const email =
    session?.email ||
    localStorage.getItem("omnilink_email") ||
    localStorage.getItem("userName") ||
    "admin@omnilink.com";

  const role =
    session?.role ||
    localStorage.getItem("omnilink_role") ||
    localStorage.getItem("userRole") ||
    "Admin";

  const storedName = localStorage.getItem("userName");
  const nameFromSession = session?.name || session?.full_name || session?.user_name;
  const nameFromEmail = email.includes("@") ? email.split("@")[0].replace(/[._-]/g, " ") : "Admin User";

  return {
    name: titleCase(storedName || nameFromSession || nameFromEmail),
    email,
    role: titleCase(role),
    phone: session?.phone || localStorage.getItem("omnilink_phone") || "Not Available"
  };
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value;
}

function titleCase(value) {
  return String(value || "")
    .split(" ")
    .filter(Boolean)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ");
}

function getInitials(name) {
  return String(name || "Admin User")
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(part => part.charAt(0))
    .join("")
    .toUpperCase() || "AD";
}
