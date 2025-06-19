import { K8sResourceKind, ListBase, ResourceMap } from './models'
import { State } from './state'
import { fromMarkdown, Navigation, Router, DefaultLayout } from 'mkdocs-ts'
import { iconsFactory, navBase } from './utils.view'
import { map, Observable } from 'rxjs'
import { AnyVirtualDOM } from 'rx-vdom'
import { ServiceView } from './k8s-resources/service.view'
import { SecretView } from './k8s-resources/secret.view'
import { ServiceAccountView } from './k8s-resources/service-account.view'
import { IngressView } from './k8s-resources/ingress.view'
import { PodView } from './k8s-resources/pod.view'
import { K8sResourceView } from './k8s-resources/k8s-resource.view'
import { setup } from '../auto-generated'
import { ConfigMapView } from './k8s-resources/config-map.view'

const url = (restOfPath: string) =>
    `/api/assets-gateway/webpm/resources/${setup.assetId}/${setup.version}/assets/${restOfPath}`

function fromMd(file: string) {
    return fromMarkdown({
        url: url(file),
        placeholders: {},
    })
}

export function createDynamicNav({
    kind,
    state,
}: {
    kind: K8sResourceKind
    state: State
}): Navigation<DefaultLayout.NavLayout, DefaultLayout.NavHeader> {
    const nav = navBase[kind]
    const name = nav.charAt(0).toUpperCase() + nav.slice(1)
    const icon = iconsFactory[kind]
    return {
        name,
        header: {
            icon: {
                tag: 'div',
                class: `fas ${icon} me-2`,
            },
        },
        layout: { content: fromMd(`namespace.${nav}.md`) },
        routes: state.selectedNamespace$.pipe(
            map((namespace) => ({ path, router }) => {
                return implicitNav({
                    kind,
                    state,
                    namespace,
                    path,
                    router,
                })
            }),
        ),
    }
}

type F<K extends K8sResourceKind> = {
    resource$: (name: string) => Observable<ResourceMap[K]>
    items$: Observable<ListBase<{ name: string }>>
    page: (p: {
        resource: ResourceMap[K]
        state: State
        namespace: string
        router: Router
    }) => AnyVirtualDOM
}
type Factory = {
    [K in K8sResourceKind]: F<K>
}

function factory({
    state,
    namespace,
}: {
    state: State
    namespace: string
}): Factory {
    return {
        Service: {
            resource$: (name: string) =>
                state.service$({
                    namespace,
                    service: name,
                }),
            items$: state.services$({ namespace }),
            page: ({ state, router, resource }) =>
                new ServiceView({
                    state,
                    service: resource,
                    router,
                }),
        },
        Secret: {
            resource$: (name: string) =>
                state.secret$({
                    namespace,
                    secret: name,
                }),
            items$: state.secrets$({ namespace }),
            page: ({ state, namespace, router, resource }) =>
                new SecretView({
                    state,
                    namespace,
                    secret: resource,
                    router,
                }),
        },
        ServiceAccount: {
            resource$: (name: string) =>
                state.serviceAccount$({
                    namespace,
                    serviceAccount: name,
                }),
            items$: state.serviceAccounts$({ namespace }),
            page: ({ state, router, resource }) =>
                new ServiceAccountView({
                    state,
                    serviceAccount: resource,
                    router,
                }),
        },
        Ingress: {
            resource$: (name: string) =>
                state.ingress$({
                    namespace,
                    ingress: name,
                }),
            items$: state.ingresses$({ namespace }),
            page: ({ state, router, resource }) =>
                new IngressView({ state, router, ingress: resource }),
        },
        Pod: {
            resource$: (name: string) =>
                state.pod$({
                    namespace,
                    pod: name,
                }),
            items$: state.pods$({ namespace }),
            page: ({ resource, state, namespace }) =>
                new PodView({ pod: resource, state, namespace }),
        },
        ConfigMap: {
            resource$: (name: string) =>
                state.configMap$({
                    namespace,
                    configMap: name,
                }),
            items$: state.configMaps$({ namespace }),
            page: ({ resource, state, router, namespace }) =>
                new ConfigMapView({
                    configMap: resource,
                    router,
                    state,
                    namespace,
                }),
        },
    }
}
function implicitNav({
    kind,
    state,
    namespace,
    path,
    router,
}: {
    kind: K8sResourceKind
    state: State
    namespace: string
    path: string
    router: Router
}) {
    const navTarget: F<typeof kind> = factory({ state, namespace })[kind]
    const parts = path.split('/').filter((d) => d != '')
    const view = ({ resource }: { resource: ResourceMap[typeof kind] }) => {
        return navTarget.page({
            namespace,
            router,
            state,
            resource,
        })
    }
    const formatChild = (name: string) => {
        return {
            id: window.btoa(name),
            name,
            leaf: true,
            header: {
                wrapperClass: `${DefaultLayout.NavHeaderView.DefaultWrapperClass}`,
            },
            layout: {
                content: () => {
                    return new K8sResourceView({
                        state,
                        namespace,
                        name,
                        router,
                        resource$: navTarget.resource$(name),
                        content: view,
                    })
                },
            },
        }
    }
    if (parts.length !== 0) {
        return undefined
    }
    return navTarget.items$.pipe(
        map(({ items }) => {
            const children = items.map((item) => {
                return formatChild(item.name)
            })
            return children.reduce(
                (acc, e) => ({ ...acc, [`/${e.id}`]: e }),
                {},
            )
        }),
    )
}
