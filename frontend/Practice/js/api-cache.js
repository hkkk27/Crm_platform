const apiMemoryCache = new Map();

function getCachedApiData(key, ttlMilliseconds) {
  const memoryItem = apiMemoryCache.get(key);

  if (
    memoryItem &&
    Date.now() - memoryItem.savedAt < ttlMilliseconds
  ) {
    return memoryItem.value;
  }

  const stored = sessionStorage.getItem(
    "omnilink_api_cache_" + key
  );

  if (!stored) {
    return null;
  }

  try {
    const parsed = JSON.parse(stored);

    if (
      Date.now() - parsed.savedAt >= ttlMilliseconds
    ) {
      sessionStorage.removeItem(
        "omnilink_api_cache_" + key
      );

      apiMemoryCache.delete(key);

      return null;
    }

    apiMemoryCache.set(key, parsed);

    return parsed.value;
  } catch (error) {
    sessionStorage.removeItem(
      "omnilink_api_cache_" + key
    );

    apiMemoryCache.delete(key);

    return null;
  }
}

function setCachedApiData(key, value) {
  const item = {
    value: value,
    savedAt: Date.now()
  };

  apiMemoryCache.set(key, item);

  sessionStorage.setItem(
    "omnilink_api_cache_" + key,
    JSON.stringify(item)
  );
}

function clearCachedApiData(key) {
  apiMemoryCache.delete(key);

  sessionStorage.removeItem(
    "omnilink_api_cache_" + key
  );
}

function clearCachedApiPrefix(prefix) {
  for (const key of apiMemoryCache.keys()) {
    if (key.startsWith(prefix)) {
      apiMemoryCache.delete(key);
    }
  }

  const keysToRemove = [];

  for (
    let index = 0;
    index < sessionStorage.length;
    index += 1
  ) {
    const storageKey = sessionStorage.key(index);

    if (
      storageKey &&
      storageKey.startsWith(
        "omnilink_api_cache_" + prefix
      )
    ) {
      keysToRemove.push(storageKey);
    }
  }

  keysToRemove.forEach(function (key) {
    sessionStorage.removeItem(key);
  });
}

function getApiBaseUrl() {
  return (
    window.API_BASE_URL ||
    localStorage.getItem("omnilink_api_base") ||
    "http://127.0.0.1:8000"
  );
}

function getApiAuthToken() {
  return localStorage.getItem("omnilink_token") || "";
}

function getApiHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: "Bearer " + getApiAuthToken()
  };
}

function formatCachedApiError(result, fallbackMessage) {
  const value =
    result &&
    (result.detail || result.message || result.error);

  if (Array.isArray(value)) {
    return value
      .map(function (item) {
        if (typeof item === "string") return item;
        if (item && item.msg) return item.msg;
        return JSON.stringify(item);
      })
      .join("\n");
  }

  if (value && typeof value === "object") {
    if (value.msg) return value.msg;
    return JSON.stringify(value);
  }

  return String(value || fallbackMessage || "API request failed");
}

async function cachedApiGet(
  cacheKey,
  endpoint,
  ttlMilliseconds = 60000
) {
  const cached = getCachedApiData(
    cacheKey,
    ttlMilliseconds
  );

  if (cached !== null) {
    return cached;
  }

  const response = await fetch(
    getApiBaseUrl() + endpoint,
    {
      method: "GET",
      headers: getApiHeaders()
    }
  );

  const result = await response.json().catch(function () {
    return {};
  });

  if (!response.ok) {
    throw new Error(
      formatCachedApiError(
        result,
        "API request failed: " + endpoint
      )
    );
  }

  setCachedApiData(cacheKey, result);

  return result;
}