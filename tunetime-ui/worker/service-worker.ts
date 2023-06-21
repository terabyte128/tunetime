/// <reference lib="webworker" />

declare const self: ServiceWorkerGlobalScope;

self.addEventListener('push', (event: PushEvent) => {
    if (event.data) {
        self.registration.showNotification(event.data.text());
    }
});

export default null;
