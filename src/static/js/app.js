import initMobileNav from "./components/initMobileNav.js";
import initOpenClose from "./components/initOpenClose.js";
import initFixedHeader from "./components/initFixedHeader";
import initPopups from "./components/initPopups";
import initTooltip from "./components/initTooltip";
import * as Sentry from "@sentry/browser";

Sentry.init({
	dsn: "https://c2be26cb81341d42992ae0ad9b338f9b@o4506381004701696.ingest.sentry.io/4506381006667776",

	integrations: [
		// new Sentry.BrowserTracing(),
		Sentry.browserTracingIntegration(),
		Sentry.replayIntegration(),
		Sentry.feedbackIntegration({
			colorScheme: "light",
		}),
	],

	// Set tracesSampleRate to 1.0 to capture 100%
	// of transactions for performance monitoring.
	// We recommend adjusting this value in production
	tracesSampleRate: 0.5,

	// Capture Replay for 10% of all sessions,
	// plus for 100% of sessions with an error
	replaysSessionSampleRate: 0.1,
	replaysOnErrorSampleRate: 1.0,
});

document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.classList.add("is-loaded");
  initMobileNav();
  initOpenClose();
  initFixedHeader();
  initPopups();
  initTooltip();
});