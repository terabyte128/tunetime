/// <reference lib="webworker" />

self.addEventListener('push', (event: PushEvent) => {
    if (event.data) {
        self.registration.showNotification(event.data.text());
    }
});
