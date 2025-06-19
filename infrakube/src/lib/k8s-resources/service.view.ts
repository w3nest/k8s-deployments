import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { parseMd, Router } from 'mkdocs-ts'
import { State } from '../state'
import { Service } from '../models'
import { K8sLinkView } from '../utils.view'

export class ServiceView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly service: Service
    public readonly state: State
    public readonly router: Router

    constructor(params: { service: Service; state: State; router: Router }) {
        Object.assign(this, params)
        this.children = [
            parseMd({
                src: `
<note level='abstract' title="Resource info." expandable="true">
*  **Type** : ${this.service.type}
</note>

## Matching Pods

<pods></pods>
`,
                router: this.router,
                views: {
                    pods: () => ({
                        tag: 'div',
                        children: this.service.pods.map(
                            (pod) =>
                                new K8sLinkView({
                                    kind: 'Pod',
                                    name: pod.name,
                                    namespace: pod.namespace,
                                    state: this.state,
                                    router: this.router,
                                }),
                        ),
                    }),
                },
            }),
        ]
    }
}
//
// export class PodLink implements VirtualDOM<'div'> {
//     public readonly tag = 'div'
//     public readonly class = 'd-flex align-items-center border rounded p-1'
//     public readonly style = {
//         width: 'fit-content',
//     }
//     public readonly children: ChildrenLike
//
//     constructor(params: {
//         pod: { name: string; namespace: string }
//         router: Router
//         state: State
//     }) {
//         this.children = [
//             { tag: 'i', class: `fas ${iconsFactory['pod']}` },
//             { tag: 'i', class: 'mx-1' },
//             new K8sResourceAnchor({
//                 namespace: params.pod.namespace,
//                 router: params.router,
//                 state: params.state,
//                 name: params.pod.name,
//                 kind: 'pod',
//             }),
//         ]
//     }
// }
