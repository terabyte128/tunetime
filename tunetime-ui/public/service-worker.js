self.addEventListener('push', event => {
    if (event.data) {
        self.registration.showNotification("it's tunetime!", {
            body: 'click to share ur tunes with ur friends!!',
        });
    }
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        (async () => {
            const allClients = await clients.matchAll({
                includeUncontrolled: true,
            });

            if (allClients.length > 0) {
                allClients[0].focus();
            } else {
                await clients.openWindow('/');
            }
        })(),
    );
});
