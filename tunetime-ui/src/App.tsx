import { useEffect, useState } from 'react';
import { components } from './spotify';
import './App.css';
import useSWR, { SWRConfig } from 'swr';

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
        window.location.href = '/oauth/login';
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
                    <b>{recent.data.name}</b> from{' '}
                    <b>{recent.data.album?.name}</b>.
                </p>
                <button
                    onClick={() => {
                        fetch('/api/message', {
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
    const [sub, setSub] = useState<PushSubscription>();

    useEffect(() => {
        if (!('serviceWorker' in navigator)) {
            // Service Worker isn't supported on this browser, disable or hide UI.
            throw new Error('service worker not supported');
        }

        if (!('PushManager' in window)) {
            // Push isn't supported on this browser, disable or hide UI.
            throw new Error('push not supported');
        }

        navigator.serviceWorker
            .register('/service-worker.js')
            .then(registration => setWorker(registration));
    }, []);

    return (
        <>
            <label>
                <input
                    type="checkbox"
                    checked={permission === 'granted'}
                    onClick={async () => {
                        if (!worker) return;
                        const subscription = await worker.pushManager.subscribe(
                            {
                                applicationServerKey:
                                    'BCGgH6JSisdn-JleMsafEXwG-YzQWeWyzwgCIZO5sUc1tWPsNxaUVtrF2Y5ru9oJc5o2xQhwAHmGnu8yxtZXCEE',
                                userVisibleOnly: true,
                            },
                        );
                        setSub(subscription);
                        const result = await Notification.requestPermission();
                        setPermission(result);

                        fetch('/api/profile/register-push', {
                            method: 'POST',
                            headers: {
                                'content-type': 'application/json',
                            },
                            body: JSON.stringify(subscription),
                        });
                    }}
                />{' '}
                i'd like notifications for when it's tunetime
            </label>
        </>
    );
};

export default App;
