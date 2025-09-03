import { Navigation, Router, DefaultLayout } from 'mkdocs-ts'
import { install } from '@w3nest/webpm-client'
import { from, map, shareReplay } from 'rxjs'
import { HomeView } from './home.view'
import { State } from './state'
import { getDecoration, K8sCtxDropDown, NamespaceDropDown } from './utils.view'
import { NodesView } from './k8s-resources/nodes.view'
import { createDynamicNav } from './k8s-resources.nav'
import { NamespaceView } from './k8s-resources/namespace.view'
import { PersistentVolumesView } from './k8s-resources/persistent-volumes.view'
import { setup } from '../auto-generated'

import { navigation as navW3Nest } from './w3nest'
import { Backend } from './client'

export type AppNav = Navigation<
    DefaultLayout.NavLayout,
    DefaultLayout.NavHeader
>

export type AppState = {
    router: Router
}

export const metadata = () => ({
    name: setup.name,
    version: setup.version,
})

export const navigation = ({
    appState,
    basePath,
}: {
    appState: AppState
    basePath: string
}): Navigation<DefaultLayout.NavLayout, DefaultLayout.NavHeader> => {
    const backend$ = from(
        install({
            backends: {
                modules: ['w3nest_infrakube_backend#^0.1.1 as backend'],
                partition: 'Default',
            },
            css: [`${setup.name}#${setup.version}~assets/style.css`],
        }),
    ).pipe(
        map((scope) => scope as unknown as { backend: Backend }),
        map((scope) => scope.backend),
        shareReplay(1),
    )

    const state = new State({ backend$, appState, basePath })

    return {
        name: 'w3Nest K8s',
        header: {
            icon: {
                tag: 'img',
                width: 20,
                class: 'me-2',
                src: `${State.urlBase}/assets/icon.svg`,
            },
            actions: [new K8sCtxDropDown({ state })],
        },
        layout: { content: () => new HomeView({ state }) },
        routes: {
            '/w3nest': navW3Nest(state),
            '/nodes': {
                name: 'Nodes',
                header: getDecoration('fa-server'),
                layout: {
                    content: ({ router }) => new NodesView({ state, router }),
                },
            },
            '/persistent-volumes': {
                name: 'Persistent Volumes',
                header: getDecoration('fa-hdd'),
                layout: {
                    content: ({ router }) =>
                        new PersistentVolumesView({ state, router }),
                },
            },
            '/namespace': {
                name: 'Namespace',
                header: {
                    icon: { tag: 'i', class: 'fas fa-layer-group me-2' },
                    actions: [new NamespaceDropDown({ state })],
                },
                layout: {
                    content: ({ router }) =>
                        new NamespaceView({ state, router }),
                },
                routes: {
                    '/ingresses': createDynamicNav({
                        kind: 'Ingress',
                        state,
                    }),
                    '/services': createDynamicNav({
                        kind: 'Service',
                        state,
                    }),
                    '/pods': createDynamicNav({
                        kind: 'Pod',
                        state,
                    }),
                    '/secrets': createDynamicNav({
                        kind: 'Secret',
                        state,
                    }),
                    '/service-accounts': createDynamicNav({
                        kind: 'ServiceAccount',
                        state,
                    }),
                    '/config-maps': createDynamicNav({
                        kind: 'ConfigMap',
                        state,
                    }),
                },
            },
        },
    }
}
