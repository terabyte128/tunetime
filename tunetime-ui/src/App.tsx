import { useState } from 'react';
import { DateTime } from 'luxon';
import './App.css';
import { SWRConfig } from 'swr';
import Banner from './Banner';
import { ResponseError, useProfile, useTunes } from './remote-types';
import PushNotifications from './PushNotifications';

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
                        const error: ResponseError = {
                            status_code: rsp.status,
                        };
                        try {
                            error['data'] = await rsp.json();
                        } catch (e) {
                            error['text'] = await rsp.text();
                        }

                        throw error;
                    }

                    return rsp.json();
                },
            }}
        >
            <div className="container">
                <h1>tunetime</h1>
                <HelloContainer />
            </div>
        </SWRConfig>
    );
}

const HelloContainer = () => {
    const profile = useProfile();
    const [isEditingProfile, setIsEditingProfile] = useState(false);
    const [name, setName] = useState(profile?.data?.display_name);
    const [isShowingBanner, setIsShowingBanner] = useState(true);

    // redirect if forbidden
    if (profile.error) {
        if (profile.error.status_code === 403) {
            window.location.href = '/oauth2/login';
        } else {
            return (
                <>
                    error:{' '}
                    {profile.error.data
                        ? JSON.stringify(profile.error.data)
                        : profile.error.text}
                </>
            );
        }
    }

    if (!profile.data) {
        return <>loading...</>;
    }

    return (
        <div>
            <div>
                <PushNotifications />
                {profile.data.can_send_tune && isShowingBanner && (
                    <Banner onClose={() => setIsShowingBanner(false)} />
                )}
                <p>
                    you are logged in as {profile.data.display_name}{' '}
                    {!isEditingProfile && (
                        <button onClick={() => setIsEditingProfile(true)}>
                            edit display name
                        </button>
                    )}
                </p>
                {isEditingProfile && (
                    <div>
                        <label>
                            enter your name:{' '}
                            <input
                                type="text"
                                value={name}
                                onChange={e => setName(e.target.value)}
                            />
                        </label>
                        <button
                            onClick={async () => {
                                await fetch('/api/profile', {
                                    method: 'POST',
                                    headers: {
                                        'content-type': 'application/json',
                                    },
                                    body: JSON.stringify({
                                        display_name: name,
                                    }),
                                });
                                setIsEditingProfile(false);
                                setName('');
                                profile.mutate();
                            }}
                        >
                            ok
                        </button>
                    </div>
                )}
                {profile.data.can_send_tune && (
                    <div>
                        <button onClick={() => setIsShowingBanner(true)}>
                            share your tune!
                        </button>
                    </div>
                )}
            </div>
            <TuneCards />
        </div>
    );
};

const TuneCards = () => {
    const { data, error } = useTunes();

    if (!data || error) {
        return <>loading tunes...</>;
    }

    return (
        <>
            <h3>your friends have been listening to...</h3>
            {data.map(tune => (
                <div className="card">
                    <div className="flex-horizontal space-between">
                        <div>
                            {tune.name}
                            <br />
                            {tune.primary_artist}
                        </div>
                        <div>{tune.album}</div>
                    </div>
                    <hr />
                    <div className="flex-horizontal space-between">
                        <div>{tune.user}</div>
                        <div>
                            {DateTime.fromSeconds(
                                tune.created_at,
                            ).toLocaleString(DateTime.DATETIME_MED)}
                        </div>
                    </div>
                </div>
            ))}
        </>
    );
};

export default App;
