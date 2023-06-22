import useSWR from 'swr';
import { components } from './spotify';

type User = components['schemas']['PrivateUserObject'] & {
    can_send_tune: boolean;
};

export type ResponseError = {
    status_code: number;
    data?: object;
    text?: string;
};

export const useProfile = () => useSWR<User, ResponseError>('api/profile');

export const useRecent = () =>
    useSWR<components['schemas']['TrackObject'], ResponseError>(
        '/api/profile/recent',
    );

export interface Tune {
    name: string;
    album: string;
    primary_artist: string;
    user: string;
    created_at: number;
}

export const useTunes = () => useSWR<Tune[], ResponseError>('/api/tunes');
