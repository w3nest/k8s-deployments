import {
    BehaviorSubject,
    map,
    Observable,
    ReplaySubject,
    shareReplay,
    switchMap,
    take,
    tap,
} from 'rxjs'
import { Backend, Client } from './client'
import { Router } from 'mkdocs-ts'
import {
    ConfigMap,
    ConfigMapList,
    Context,
    Namespace,
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
    NamespaceRef,
    NodeList,
    PersistentVolumeList,
    ResourceBase,
    QueryLogResponse,
} from './models'
import { setup } from '../auto-generated'

export type AppState = {
    router: Router
}

export class State {
    public static readonly urlBase = `/api/assets-gateway/webpm/resources/${setup.assetId}/${setup.version}`
    public readonly basePath: string
    public readonly backend$: Observable<Backend>
    public readonly client: Client
    public readonly appState: AppState

    public readonly router: Router

    public readonly k8sContexts$: Observable<string[]>
    public readonly k8sContext$ = new ReplaySubject<string>(1)
    public readonly namespaces$ = new BehaviorSubject<NamespaceRef[]>([
        { name: 'default' },
    ])
    public readonly selectedNamespace$ = new BehaviorSubject<string>('default')

    constructor(params: {
        backend$: Observable<Backend>
        appState: AppState
        basePath: string
    }) {
        Object.assign(this, params)
        this.router = this.appState.router
        this.client = new Client({ backend$: this.backend$ })
        this.k8sContexts$ = this.client.contexts().pipe(
            map(({ items }) => {
                return items.map((k8sCtx) => k8sCtx.name)
            }),
            tap((contexts) => {
                this.selectContext(contexts[0])
            }),
            take(1),
            shareReplay(1),
        )
        this.k8sContext$
            .pipe(
                switchMap((k8sContext) => {
                    return this.client.namespaces$({ k8sContext })
                }),
            )
            .subscribe(({ items }) => this.namespaces$.next(items))
    }

    selectContext(ctx: string) {
        this.k8sContext$.next(ctx)
        this.selectedNamespace$.next('default')
    }

    selectNamespace(namespace: string) {
        this.selectedNamespace$.next(namespace)
    }

    private wrapEndpoint<TResp>(
        obs: (arg: { k8sContext: string }) => Observable<TResp>,
    ): Observable<TResp> {
        return this.k8sContext$.pipe(
            switchMap((k8sContext: string) => {
                return obs({ k8sContext })
            }),
            shareReplay({ bufferSize: 1, refCount: true }),
        )
    }
    context$(): Observable<Context> {
        return this.wrapEndpoint((args) => this.client.context$(args))
    }

    nodes$(): Observable<NodeList> {
        return this.wrapEndpoint((args) => this.client.nodes$(args))
    }

    persistentVolumes$(): Observable<PersistentVolumeList> {
        return this.wrapEndpoint((args) => this.client.persistentVolumes$(args))
    }

    namespace$({ namespace }: { namespace: string }): Observable<Namespace> {
        return this.wrapEndpoint((args) =>
            this.client.namespace$({ ...args, namespace }),
        )
    }

    secrets$({ namespace }: { namespace: string }): Observable<SecretList> {
        return this.wrapEndpoint((args) =>
            this.client.secrets$({ ...args, namespace }),
        )
    }
    secret$({
        namespace,
        secret,
    }: {
        namespace: string
        secret: string
    }): Observable<Secret> {
        return this.wrapEndpoint((args) =>
            this.client.secret$({ ...args, namespace, secret }),
        )
    }

    serviceAccounts$({
        namespace,
    }: {
        namespace: string
    }): Observable<ServiceAccountList> {
        return this.wrapEndpoint((args) =>
            this.client.serviceAccounts$({ ...args, namespace }),
        )
    }

    serviceAccount$({
        namespace,
        serviceAccount,
    }: {
        namespace: string
        serviceAccount: string
    }): Observable<ResourceBase> {
        return this.wrapEndpoint((args) =>
            this.client.serviceAccount$({
                ...args,
                namespace,
                serviceAccount,
            }),
        )
    }

    serviceAccountToken$({
        namespace,
        serviceAccount,
    }: {
        namespace: string
        serviceAccount: string
    }): Observable<ServiceAccountToken> {
        return this.wrapEndpoint((args) =>
            this.client.serviceAccountToken$({
                ...args,
                namespace,
                serviceAccount,
            }),
        )
    }

    pods$({ namespace }: { namespace: string }): Observable<PodList> {
        return this.wrapEndpoint((args) =>
            this.client.pods$({
                ...args,
                namespace,
            }),
        )
    }

    pod$({
        namespace,
        pod,
    }: {
        namespace: string
        pod: string
    }): Observable<Pod> {
        return this.wrapEndpoint((args) =>
            this.client.pod$({
                ...args,
                pod,
                namespace,
            }),
        )
    }

    podLogs$({
        namespace,
        pod,
    }: {
        namespace: string
        pod: string
    }): Observable<Logs> {
        return this.wrapEndpoint((args) =>
            this.client.podLogs$({
                ...args,
                pod,
                namespace,
            }),
        )
    }
    logs$(): Observable<QueryLogResponse> {
        return this.wrapEndpoint((args) =>
            this.client.logs$({
                ...args,
            }),
        )
    }

    services$({ namespace }: { namespace: string }): Observable<ServiceList> {
        return this.wrapEndpoint((args) =>
            this.client.services$({
                ...args,
                namespace,
            }),
        )
    }

    service$({
        namespace,
        service,
    }: {
        namespace: string
        service: string
    }): Observable<Service> {
        return this.wrapEndpoint((args) =>
            this.client.service$({
                ...args,
                namespace,
                service,
            }),
        )
    }

    ingresses$({ namespace }: { namespace: string }): Observable<IngressList> {
        return this.wrapEndpoint((args) =>
            this.client.ingresses$({
                ...args,
                namespace,
            }),
        )
    }

    ingress$({
        namespace,
        ingress,
    }: {
        namespace: string
        ingress: string
    }): Observable<Ingress> {
        return this.wrapEndpoint((args) =>
            this.client.ingress$({
                ...args,
                namespace,
                ingress,
            }),
        )
    }

    configMaps$({
        namespace,
    }: {
        namespace: string
    }): Observable<ConfigMapList> {
        return this.wrapEndpoint((args) =>
            this.client.configMaps$({
                ...args,
                namespace,
            }),
        )
    }

    configMap$({
        namespace,
        configMap,
    }: {
        namespace: string
        configMap: string
    }): Observable<ConfigMap> {
        return this.wrapEndpoint((args) =>
            this.client.configMap$({
                ...args,
                namespace,
                configMap,
            }),
        )
    }

    portForward$({
        service,
        namespace,
        port,
    }: {
        service: string
        namespace: string
        port: number
    }) {
        return this.wrapEndpoint((args) =>
            this.client.portForward$({
                ...args,
                namespace,
                service,
                port,
            }),
        )
    }

    guestUsers$() {
        return this.wrapEndpoint((args) => this.client.guestUsers$(args))
    }
    deleteGuests$() {
        return this.wrapEndpoint((args) => this.client.deleteGuests$(args))
    }
}
