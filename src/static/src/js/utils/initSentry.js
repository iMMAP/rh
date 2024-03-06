import * as Sentry from "@sentry/browser";

Sentry.init({
    dsn: "https://f6a8ac50f4f774887a8a89c58c764e6b@o4506380666077184.ingest.us.sentry.io/4506380673679360",
    integrations: [
        new Sentry.BrowserTracing(),
        new Sentry.Replay(),
        new Sentry.Feedback({
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