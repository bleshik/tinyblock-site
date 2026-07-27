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
      page_path: window.location.pathname,
      transport_type: "beacon"
    };

    parameters.cta_position = link.dataset.analyticsPosition || (
      link.closest(".hero, .creator-hero") ? "hero" :
      link.closest(".creator-callout") ? "creator_callout" :
      link.closest(".creator-contact") ? "creator_contact" :
      link.closest(".download-card") ? "download_page" :
      link.closest("footer") ? "footer" :
      "other"
    );

    if (link.dataset.analyticsStore) {
      parameters.store = link.dataset.analyticsStore;
    }

    if (link.dataset.analyticsProgram) {
      parameters.program = link.dataset.analyticsProgram;
    }

    if (link.dataset.analyticsLanguage) {
      parameters.language = link.dataset.analyticsLanguage;
    }

    window.gtag("event", link.dataset.analyticsEvent, parameters);
  });
}());
