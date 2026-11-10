// Cal.com's official embed bootstrap, scoped to this booking page.
(function (C, A, L) {
  const push = function (api, args) { api.q.push(args); };
  const document = C.document;
  C.Cal = C.Cal || function () {
    const cal = C.Cal;
    const args = arguments;
    if (!cal.loaded) {
      cal.ns = {};
      cal.q = cal.q || [];
      document.head.appendChild(document.createElement("script")).src = A;
      cal.loaded = true;
    }
    if (args[0] === L) {
      const api = function () { push(api, arguments); };
      const namespace = args[1];
      api.q = api.q || [];
      if (typeof namespace === "string") {
        cal.ns[namespace] = cal.ns[namespace] || api;
        push(cal.ns[namespace], args);
        push(cal, ["initNamespace", namespace]);
      } else {
        push(cal, args);
      }
      return;
    }
    push(cal, args);
  };
})(window, "https://app.cal.com/embed/embed.js", "init");

Cal("init", "podcast", { origin: "https://app.cal.com" });
Cal.ns.podcast("inline", {
  elementOrSelector: "#podcast-booking",
  config: { layout: "month_view" },
  calLink: "cloaked/podcast"
});
Cal.ns.podcast("ui", {
  cssVarsPerTheme: {
    light: { "cal-brand": "#242522", "cal-bg": "#faf9f6" },
    dark: { "cal-brand": "#e4e4de", "cal-bg": "#1b1c1a" }
  },
  hideEventTypeDetails: true,
  layout: "month_view"
});

// Keep a way to book if the external calendar is blocked or unavailable.
const bookingFallback = document.getElementById("booking-fallback");
const fallbackTimer = window.setTimeout(() => {
  bookingFallback.hidden = false;
}, 12000);

Cal.ns.podcast("on", {
  action: "linkReady",
  callback: () => {
    window.clearTimeout(fallbackTimer);
    bookingFallback.hidden = true;
  }
});
