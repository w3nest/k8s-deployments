export type K8sResourceKind =
    | 'Pod'
    | 'Ingress'
    | 'Service'
    | 'Secret'
    | 'ServiceAccount'
    | 'ConfigMap'

export type ResourceMap = {
    Service: Service
    Ingress: Ingress
    Pod: Pod
    Secret: Secret
    ServiceAccount: ResourceBase
    ConfigMap: ConfigMap
}

export type ResourceBase = {
    name: string
    namespace: string
    context: string
    kind: K8sResourceKind
    labels: { [k: string]: string }
    annotations: { [k: string]: string }
}

export type ListBase<TResource> = {
    items: TResource[]
}

export type Context = {
    name: string
    user: string
    cluster: string
}

export type ContextList = ListBase<Context>

export type ServiceRef = {
    name: string
    port: number
}

export type HTTPIngressPath = {
    service: ServiceRef
    path: string
}

export type IngressRule = HTTPIngressPath & {
    host: string
    urlBase: string
}

export type IngressTLS = {
    hosts: string[]
    secretName: string
}

export type Ingress = ResourceBase & {
    rules: IngressRule[]
    tls: IngressTLS[]
}

export type IngressList = ListBase<{ name: string }>

export type NamespaceRef = {
    name: string
}

export type NamespaceList = ListBase<{ name: string }>

export type PodRef = {
    name: string
    namespace: string
}

export type PodsStats = {
    totalPods: number
    runningPods: number
    pendingPods: number
    succeededPods: number
    failedPods: number
    crashLoopPods: number
    unknownPods: number
    crashLoopPodNames: string[]
}

export type PodList = ListBase<PodRef>

export type Namespace = ResourceBase & {
    pods: PodRef[]
    podsStats: PodsStats
    serviceAccounts: { name: string }[]
    services: { name: string }[]
    ingresses: { name: string }[]
    secrets: { name: string }[]
}

export type PodResourceInfo = {
    podIP: string
    phase: string
    qosClass: string
    serviceAccount: string
    imagePullSecrets: string[]
}

export type Container = {
    name: string
    image: string
    imagePullPolicy: string
    command: string[]
}

export type Pod = ResourceBase & {
    creationTimestamp: number
    memory: number
    cpu: number
    resourceInfo: PodResourceInfo
    containers: Container[]
    initContainers: Container[]
}

export type LogEntry = {
    timestamp: string
    message: string
    data: { [k: string]: unknown }
}

export type Logs = ListBase<LogEntry>

export type ServiceList = ListBase<{ name: string }>

export type Service = ResourceBase & {
    pods: {
        name: string
        namespace: string
    }[]
    type: string
}
export type SecretList = ListBase<{ name: string }>

export type Secret = ResourceBase & {
    data: { [k: string]: string }
}

export type ServiceAccountList = ListBase<{ name: string }>

export type ServiceAccountToken = ResourceBase & {
    token: string
    expiration: number
    audiences: string[]
}

export type Node = ResourceBase & {
    status: 'Ready' | 'Not Ready' | 'Unknown'
    cpuCapacity: string
    memoryCapacity: string
    internalIp: string
    externalIp: string
    hostname: string
    pods: PodRef[]
}

export type NodeList = ListBase<Node>

export type PersistentVolume = ResourceBase & {
    status: 'Bound' | 'Available'
    capacity: string
    accessModes: string[]
    storageClass: string
    reclaimPolicy: string
    volumeMode?: string
    pods: PodRef[]
}

export type PersistentVolumeList = ListBase<PersistentVolume> & {
    context: string
}

export type ConfigMapList = ListBase<{
    name: string
    namespace: string
    context: string
}>

export type ConfigMap = ResourceBase & { data: { [k: string]: string } }

export type PortForwardResponse = { url: string; pid: number }

export interface StructuredLogData {
    message: string
    spanId: string
    parentId: string
    traceId: string
    labels: string[]
    attributes?: { [k: string]: string }
    timestamp: number
    data?: { [k: string]: string }
}
export interface Log {
    data: string | StructuredLogData
    origin: {
        container: string
        instance: string
        namespace: string
        pod: string
    }
    timestamp: string
}

export interface QueryLogResponse {
    results: Log[]
}
export interface GuestUser {
    id: string
    username: string
    createdTimestamp: number
}
