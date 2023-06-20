/// <reference lib="webworker" />
self.addEventListener('push', (event) => {
    if (event.data) {
        self.registration.showNotification(event.data.text());
    }
});
