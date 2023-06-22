import { useState } from 'react';
import './Banner.scss';
import { LoadingBoundary } from './LoadingBoundary';
import { useProfile, useRecent, useTunes } from './remote-types';

const Banner = () => {
    const [isLoading, setIsLoading] = useState(false);

    return (
        <LoadingBoundary loader={useTunes}>
            {(_, mutateTunes) => (
                <LoadingBoundary loader={useRecent}>
                    {recent => (
                        <LoadingBoundary loader={useProfile}>
                            {(_, mutateProfile) => (
                                <div className="banner">
                                    <div className="banner-content">
                                        <h1 style={{ margin: 0 }}>
                                            <small>it's </small>tunetime!
                                        </h1>
                                        <p>
                                            and your most recently played track
                                            was <b>{recent.name}</b> by{' '}
                                            <b>
                                                {recent.artists
                                                    ?.map(a => a.name)
                                                    .join(', ')}
                                            </b>{' '}
                                            on the album{' '}
                                            <b>{recent.album?.name}</b>.
                                        </p>
                                        <button
                                            style={{
                                                width: '100%',
                                                height: '60px',
                                                fontSize: '18px',
                                            }}
                                            disabled={isLoading}
                                            onClick={async () => {
                                                setIsLoading(true);
                                                await fetch(
                                                    '/api/profile/share-tune',
                                                    {
                                                        method: 'POST',
                                                    },
                                                );
                                                setIsLoading(false);
                                                mutateTunes();
                                                mutateProfile();
                                            }}
                                        >
                                            share your song with your friends!
                                        </button>
                                    </div>
                                </div>
                            )}
                        </LoadingBoundary>
                    )}
                </LoadingBoundary>
            )}
        </LoadingBoundary>
    );
};

export default Banner;
