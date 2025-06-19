import { AnyVirtualDOM, ChildrenLike, VirtualDOM } from 'rx-vdom'
import { parseMd, Router } from 'mkdocs-ts'
import { PendingK8sView } from '../utils.view'
import { State } from '../state'
import { ResourceBase } from '../models'
import { Observable } from 'rxjs'
import { LabelsView } from './labels.view'

export class K8sResourceView<Resource extends ResourceBase>
    implements VirtualDOM<'div'>
{
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly name: string
    public readonly namespace: string
    public readonly state: State
    public readonly router: Router
    public readonly resource$: Observable<Resource>

    public readonly content: (p: {
        resource: Resource
        state: State
        router: Router
    }) => AnyVirtualDOM

    constructor(params: {
        name: string
        namespace: string
        state: State
        router: Router
        resource$: Observable<Resource>
        content: (p: {
            resource: Resource
            state: State
            router: Router
        }) => AnyVirtualDOM
    }) {
        Object.assign(this, params)
        this.children = [
            {
                source$: this.resource$,
                untilFirst: new PendingK8sView(),
                vdomMap: (resource: Resource) => {
                    return parseMd({
                        src: `
# **${resource.kind} \`${resource.name}\`**

<note level="info" title="Labels & Annotations" expandable="true">
**Labels**:
<labels></labels>

**Annotations**:
<annotations></annotations>
</note>

<content></content>
`,
                        router: this.router,
                        views: {
                            labels: () => {
                                return new LabelsView({
                                    labels: resource.labels,
                                })
                            },
                            annotations: () => {
                                return new LabelsView({
                                    labels: resource.annotations,
                                })
                            },
                            content: () => {
                                return this.content({
                                    resource,
                                    router: this.router,
                                    state: this.state,
                                })
                            },
                        },
                    })
                },
            },
        ]
    }
}
