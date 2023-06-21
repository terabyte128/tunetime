import { useEffect, useState } from 'react';
import { components } from './spotify';
import './App.css';
import useSWR, { SWRConfig } from 'swr';

const PUBLIC_KEY =
    'BCGgH6JSisdn-JleMsafEXwG-YzQWeWyzwgCIZO5sUc1tWPsNxaUVtrF2Y5ru9oJc5o2xQhwAHmGnu8yxtZXCEE';

function App() {
    return (
        <SWRConfig
            value={{
                fetcher: async (
                    url: string,
                    config: RequestInit | undefined,
                ) => {
                    const rsp = await fetch(url, config);
                    if (!rsp.ok) {
                        throw new Error(rsp.statusText);
                    }

                    return rsp.json();
                },
            }}
        >
            <div className="container">
                <h1>
                    <small>it's </small>tunetime!
                </h1>
                <HelloContainer />
            </div>
        </SWRConfig>
    );
}

const useProfile = () =>
    useSWR<components['schemas']['PrivateUserObject']>('/api/profile');

const useRecent = () =>
    useSWR<components['schemas']['TrackObject']>('/api/profile/recent');

const HelloContainer = () => {
    const profile = useProfile();
    const recent = useRecent();

    if (profile.error) {
        window.location.href = '/oauth2/login';
    }

    if (!profile.data || !recent.data) {
        return <>loading...</>;
    }

    return (
        <div>
            <div>
                <p>you are logged in as {profile.data.display_name}</p>
                <p>
                    and your most recently played track was{' '}
                    <b>{recent.data.name}</b> by{' '}
                    <b>{recent.data.artists?.map(a => a.name).join(', ')}</b> on
                    the album <b>{recent.data.album?.name}</b>.
                </p>
                <button
                    onClick={() => {
                        fetch('/api/profile/share-tune', {
                            method: 'POST',
                        });
                    }}
                >
                    tell your friends!
                </button>
            </div>
            <div style={{ marginTop: '24px' }}>
                <PushNotifications />
            </div>
        </div>
    );
};

const PushNotifications = () => {
    const [worker, setWorker] = useState<ServiceWorkerRegistration>();
    const [permission, setPermission] = useState(Notification.permission);
    const [hasPush, setHasPush] = useState(false);
    const [subscription, setSubscription] = useState<PushSubscription>();
    const [isRegistering, setIsRegistering] = useState(false);

    useEffect(() => {
        if (!('serviceWorker' in navigator)) {
            // Service Worker isn't supported on this browser, disable or hide UI.
            return;
        }

        if (!('PushManager' in window)) {
            // Push isn't supported on this browser, disable or hide UI.
            return;
        }

        setHasPush(true);

        (async () => {
            const worker = await navigator.serviceWorker.register(
                '/service-worker.js',
            );
            setWorker(worker);
            const subscription = await worker.pushManager.getSubscription();
            setSubscription(subscription || undefined);
        })();
    }, []);

    return (
        <>
            <label>
                <input
                    type="checkbox"
                    disabled={
                        !hasPush || isRegistering || permission === 'denied'
                    }
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

export default App;
