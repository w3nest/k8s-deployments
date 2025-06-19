import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { parseMd, Router } from 'mkdocs-ts'
import { K8sLinkView, PendingK8sView } from '../utils.view'
import { State } from '../state'
import { LabelsView } from './labels.view'
import { switchMap } from 'rxjs'
import { Namespace, K8sResourceKind } from '../models'

export class NamespaceView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State
    public readonly router: Router
    public readonly namespace: string

    constructor(params: { state: State; router: Router }) {
        Object.assign(this, params)
        this.children = [
            {
                source$: this.state.selectedNamespace$.pipe(
                    switchMap((namespace) =>
                        this.state.namespace$({
                            namespace: namespace,
                        }),
                    ),
                ),
                untilFirst: new PendingK8sView(),
                vdomMap: (resp: Namespace) => {
                    const listView = (
                        kind: K8sResourceKind,
                        resources: { name: string }[],
                    ) => {
                        return {
                            tag: 'div' as const,
                            children: resources.map((r) => {
                                return {
                                    tag: 'h3' as const,
                                    children: [
                                        new K8sLinkView({
                                            kind,
                                            name: r.name,
                                            namespace: resp.namespace,
                                            state: this.state,
                                            router: this.router,
                                        }),
                                    ],
                                }
                            }),
                        }
                    }
                    return parseMd({
                        src: `
# Namespace \`${resp.name}\`

<note level="info" title="Labels & Annotations" expandable="true">
**Labels**:
<labels></labels>

**Annotations**:
<annotations></annotations>
</note>

## Pods

*  **Total pods**: ${resp.podsStats.totalPods}
*  **Running pods**: ${resp.podsStats.runningPods}
*  **Pending pods**: ${resp.podsStats.pendingPods}
*  **Succeeded pods**: ${resp.podsStats.succeededPods}
*  **Failed pods**: ${resp.podsStats.failedPods}
*  **Crash-loop pods**: ${resp.podsStats.crashLoopPods}

<pods></pods>

## Ingresses

<ingresses></ingresses>

## Services

<services></services>

## Secrets

<secrets></secrets>

## Service Accounts

<serviceAccounts></serviceAccounts>
`,
                        router: this.state.router,
                        views: {
                            labels: () => {
                                return new LabelsView({
                                    labels: resp.labels,
                                })
                            },
                            annotations: () => {
                                return new LabelsView({
                                    labels: resp.annotations,
                                })
                            },
                            pods: () => {
                                return listView('Pod', resp.pods)
                            },
                            ingresses: () => {
                                return listView('Ingress', resp.ingresses || [])
                            },
                            services: () => {
                                return listView('Service', resp.ingresses || [])
                            },
                            serviceAccounts: () => {
                                return listView(
                                    'ServiceAccount',
                                    resp.serviceAccounts || [],
                                )
                            },
                            secrets: () => {
                                return listView('Secret', resp.secrets || [])
                            },
                        },
                    })
                },
            },
        ]
    }
}
