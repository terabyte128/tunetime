import useSWR from 'swr';
import { components } from './spotify';

type User = components['schemas']['PrivateUserObject'] & {
    can_send_tune: boolean;
};

export const useProfile = () => useSWR<User>('api/profile');

export const useRecent = () =>
    useSWR<components['schemas']['TrackObject']>('/api/profile/recent');

export interface Tune {
    name: string;
    album: string;
    primary_artist: string;
    user: string;
    created_at: number;
}

export const useTunes = () => useSWR<Tune[]>('/api/tunes');
