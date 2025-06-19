import { Observable, switchMap } from 'rxjs'
import {
    ConfigMap,
    ConfigMapList,
    Context,
    ContextList,
    Namespace,
    NamespaceList,
    PodList,
    Pod,
    Secret,
    SecretList,
    ServiceAccountList,
    ServiceAccountToken,
    Service,
    Ingress,
    IngressList,
    ServiceList,
    Logs,
    NodeList,
    PersistentVolumeList,
    ResourceBase,
    PortForwardResponse,
    QueryLogResponse,
    GuestUser,
} from './models'

export type Backend = {
    fetchJson: (
        url: string,
        options?: unknown,
    ) => Promise<{ [k: string]: unknown }>
    fromFetchJson: (
        url: string,
        options?: unknown,
    ) => Observable<{ [k: string]: unknown }>
}

export class Client {
    backend$: Observable<Backend>

    constructor(params: { backend$: Observable<Backend> }) {
        Object.assign(this, params)
    }

    contexts(): Observable<ContextList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    'contexts',
                ) as unknown as Observable<ContextList>
            }),
        )
    }

    context$({ k8sContext }: { k8sContext: string }): Observable<Context> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}`,
                ) as unknown as Observable<Context>
            }),
        )
    }

    nodes$({ k8sContext }: { k8sContext: string }): Observable<NodeList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/nodes`,
                ) as unknown as Observable<NodeList>
            }),
        )
    }

    persistentVolumes$({
        k8sContext,
    }: {
        k8sContext: string
    }): Observable<PersistentVolumeList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/persistent-volumes`,
                ) as unknown as Observable<PersistentVolumeList>
            }),
        )
    }

    namespaces$({
        k8sContext,
    }: {
        k8sContext: string
    }): Observable<NamespaceList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces`,
                ) as unknown as Observable<NamespaceList>
            }),
        )
    }

    namespace$({
        k8sContext,
        namespace,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<Namespace> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}`,
                ) as unknown as Observable<Namespace>
            }),
        )
    }

    secrets$({
        k8sContext,
        namespace,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<SecretList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/secrets`,
                ) as unknown as Observable<SecretList>
            }),
        )
    }

    secret$({
        k8sContext,
        namespace,
        secret,
    }: {
        k8sContext: string
        namespace: string
        secret: string
    }): Observable<Secret> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/secrets/${secret}`,
                ) as unknown as Observable<Secret>
            }),
        )
    }

    serviceAccounts$({
        k8sContext,
        namespace,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<ServiceAccountList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/service-accounts`,
                ) as unknown as Observable<ServiceAccountList>
            }),
        )
    }

    serviceAccount$({
        k8sContext,
        namespace,
        serviceAccount,
    }: {
        k8sContext: string
        namespace: string
        serviceAccount: string
    }): Observable<ResourceBase> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/service-accounts/${serviceAccount}`,
                ) as unknown as Observable<ResourceBase>
            }),
        )
    }

    serviceAccountToken$({
        k8sContext,
        namespace,
        serviceAccount,
    }: {
        k8sContext: string
        namespace: string
        serviceAccount: string
    }): Observable<ServiceAccountToken> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/service-accounts/${serviceAccount}/token`,
                ) as unknown as Observable<ServiceAccountToken>
            }),
        )
    }

    pods$({
        k8sContext,
        namespace,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<PodList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/pods`,
                ) as unknown as Observable<PodList>
            }),
        )
    }
    pod$({
        k8sContext,
        namespace,
        pod,
    }: {
        k8sContext: string
        namespace: string
        pod: string
    }): Observable<Pod> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/pods/${pod}`,
                ) as unknown as Observable<Pod>
            }),
        )
    }
    podLogs$({
        k8sContext,
        namespace,
        pod,
    }: {
        k8sContext: string
        namespace: string
        pod: string
    }): Observable<Logs> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/pods/${pod}/logs`,
                ) as unknown as Observable<Logs>
            }),
        )
    }

    logs$({
        k8sContext,
    }: {
        k8sContext: string
    }): Observable<QueryLogResponse> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/logs`,
                ) as unknown as Observable<QueryLogResponse>
            }),
        )
    }
    services$({
        k8sContext,
        namespace,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<ServiceList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/services`,
                ) as unknown as Observable<ServiceList>
            }),
        )
    }

    service$({
        k8sContext,
        namespace,
        service,
    }: {
        k8sContext: string
        namespace: string
        service: string
    }): Observable<Service> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/services/${service}`,
                ) as unknown as Observable<Service>
            }),
        )
    }

    ingresses$({
        k8sContext,
        namespace,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<IngressList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/ingresses`,
                ) as unknown as Observable<IngressList>
            }),
        )
    }
    ingress$({
        k8sContext,
        namespace,
        ingress,
    }: {
        k8sContext: string
        namespace: string
        ingress: string
    }): Observable<Ingress> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/ingresses/${ingress}`,
                ) as unknown as Observable<Ingress>
            }),
        )
    }

    configMaps$({
        namespace,
        k8sContext,
    }: {
        k8sContext: string
        namespace: string
    }): Observable<ConfigMapList> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/config-maps`,
                ) as unknown as Observable<ConfigMapList>
            }),
        )
    }

    configMap$({
        namespace,
        k8sContext,
        configMap,
    }: {
        k8sContext: string
        namespace: string
        configMap: string
    }): Observable<ConfigMap> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/config-maps/${configMap}`,
                ) as unknown as Observable<ConfigMap>
            }),
        )
    }

    portForward$({
        namespace,
        service,
        port,
        k8sContext,
    }: {
        namespace: string
        service: string
        port: number
        k8sContext: string
    }): Observable<PortForwardResponse> {
        const body = {
            port,
        }
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/namespaces/${namespace}/services/${service}/port-forward`,
                    {
                        method: 'post',
                        body: JSON.stringify(body),
                        headers: { 'content-type': 'application/json' },
                    },
                ) as unknown as Observable<PortForwardResponse>
            }),
        )
    }

    guestUsers$({
        k8sContext,
    }: {
        k8sContext: string
    }): Observable<GuestUser[]> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/w3nest/keycloak/guests`,
                ) as unknown as Observable<GuestUser[]>
            }),
        )
    }
    deleteGuests$({ k8sContext }: { k8sContext: string }): Observable<unknown> {
        return this.backend$.pipe(
            switchMap((backend) => {
                return backend.fromFetchJson(
                    `contexts/${k8sContext}/w3nest/keycloak/guests`,
                    {
                        method: 'DELETE',
                    },
                ) as unknown as Observable<unknown>
            }),
        )
    }
}
