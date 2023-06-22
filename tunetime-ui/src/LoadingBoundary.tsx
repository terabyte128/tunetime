import { ReactNode } from 'react';
import { KeyedMutator, SWRResponse } from 'swr';

interface LoadingBoundaryType<Data, Error, Config> {
    loader: () => SWRResponse<Data, Error, Config>;
    children: (data: Data, mutate: KeyedMutator<Data>) => ReactNode;
}

export const LoadingBoundary = <Data, Error, Config>(
    props: LoadingBoundaryType<Data, Error, Config>,
) => {
    const rsp = props.loader();

    if (rsp.error) {
        return <>{rsp.error}</>;
    } else if (!rsp.data) {
        return <>loading...</>;
    }

    return props.children(rsp.data, rsp.mutate);
};
