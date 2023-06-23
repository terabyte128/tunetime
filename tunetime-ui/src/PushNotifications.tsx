import { useState, useEffect } from 'react';

const PUBLIC_KEY =
    'BCGgH6JSisdn-JleMsafEXwG-YzQWeWyzwgCIZO5sUc1tWPsNxaUVtrF2Y5ru9oJc5o2xQhwAHmGnu8yxtZXCEE';

const PushNotifications = () => {
    const [worker, setWorker] = useState<ServiceWorkerRegistration>();
    const [permission, setPermission] =
        useState<NotificationPermission>('default');
    const [hasPush, setHasPush] = useState(false);
    const [subscription, setSubscription] = useState<PushSubscription>();
    const [isRegistering, setIsRegistering] = useState(false);

    useEffect(() => {
        if (
            !(
                'serviceWorker' in navigator &&
                'PushManager' in window &&
                'Notification' in window
            )
        ) {
            return;
        }

        setHasPush(true);
        setPermission(Notification.permission);

        (async () => {
            const worker = await navigator.serviceWorker.register(
                '/service-worker.js',
            );
            setWorker(worker);
            const subscription = await worker.pushManager.getSubscription();
            setSubscription(subscription || undefined);
        })();
    }, []);

    if (!hasPush) return null;

    return (
        <>
            <label>
                <input
                    type="checkbox"
                    disabled={isRegistering || permission === 'denied'}
                    checked={subscription !== undefined}
                    onChange={async e => {
                        const checked = e.target.checked;
                        if (checked) {
                            const notificationPermission =
                                await Notification.requestPermission();

                            setPermission(notificationPermission);
                            if (notificationPermission === 'denied') {
                                alert(
                                    'you need to allow that if you want to be notified!!1!',
                                );
                                return;
                            }

                            if (!subscription && worker) {
                                setIsRegistering(true);

                                const localSubscription =
                                    await worker.pushManager.subscribe({
                                        applicationServerKey: PUBLIC_KEY,
                                        userVisibleOnly: true,
                                    });

                                await fetch('/api/profile/register-push', {
                                    method: 'POST',
                                    headers: {
                                        'content-type': 'application/json',
                                    },
                                    body: JSON.stringify(localSubscription),
                                });

                                setIsRegistering(false);
                                setSubscription(localSubscription);
                            }
                        } else {
                            setIsRegistering(true);
                            subscription?.unsubscribe();
                            await fetch('/api/profile/register-push', {
                                method: 'DELETE',
                                headers: {
                                    'content-type': 'application/json',
                                },
                            });
                            setSubscription(undefined);
                            setIsRegistering(false);
                        }
                    }}
                />{' '}
                i'd like to be notified when it's tunetime{' '}
                {isRegistering && '(thinking...)'}
            </label>
        </>
    );
};

export default PushNotifications;
