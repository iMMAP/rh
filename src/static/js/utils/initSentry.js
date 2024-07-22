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
    tracesSampleRate: 1.0,

    // Capture Replay for 10% of all sessions,
    // plus for 100% of sessions with an error
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
});