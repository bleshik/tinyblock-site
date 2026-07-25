(function () {
  "use strict";

  document.addEventListener("click", function (event) {
    var link = event.target.closest("[data-analytics-event]");

    if (!link || typeof window.gtag !== "function") {
      return;
    }

    var parameters = {
      link_url: link.href || undefined,
      link_text: link.textContent.trim().slice(0, 100),
      transport_type: "beacon"
    };

    if (link.dataset.analyticsStore) {
      parameters.store = link.dataset.analyticsStore;
    }

    if (link.dataset.analyticsProgram) {
      parameters.program = link.dataset.analyticsProgram;
    }

    window.gtag("event", link.dataset.analyticsEvent, parameters);
  });
}());
