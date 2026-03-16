/**
 * version-redirect.js
 *
 * On the root index page only, fetches versions.json and redirects to the
 * URL of the first entry with a 3-digit Mechanical revision (e.g. "261").
 * This is the stable/latest version listed at the top of versions.json.
 *
 * Falls back to FALLBACK_VERSION if the fetch fails or no match is found.
 */
(function () {
  // Only run on the root index page
  if (DOCUMENTATION_OPTIONS.pagename !== "index") {
    return;
  }

  var FALLBACK_VERSION = "261";

  // theme_switcher_json_url is injected by ansys-sphinx-theme after page load,
  // so derive the versions.json URL from the current host as a reliable fallback.
  var switcherUrl =
    DOCUMENTATION_OPTIONS.theme_switcher_json_url ||
    window.location.origin + "/versions.json";

  function redirectToVersion(version) {
    window.location.replace("api/ansys/mechanical/stubs/v" + version + "/index.html");
  }

  fetch(switcherUrl)
    .then(function (response) { return response.json(); })
    .then(function (data) {
      // Pick the first entry whose version is a 3-digit Mechanical revision
      var stable = data.find(function (entry) {
        return /^\d{3}$/.test(entry.version);
      });
      redirectToVersion(stable ? stable.version : FALLBACK_VERSION);
    })
    .catch(function () {
      redirectToVersion(FALLBACK_VERSION);
    });
})();
