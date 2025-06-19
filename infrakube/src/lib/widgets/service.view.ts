import { ChildrenLike, VirtualDOM, AnyVirtualDOM } from 'rx-vdom'
import { Router } from 'mkdocs-ts'
import { K8sLinkView, PendingK8sView } from '../utils.view'
import { State } from '../state'
import { Service } from '../models'
import { InlinedResourceView } from './common'

export class ServiceView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'w-100'

    public readonly children: ChildrenLike

    public readonly name: string
    public readonly namespace: string
    public readonly state: State
    public readonly router: Router

    constructor(params: {
        name: string
        namespace: string
        state: State
        router: Router
    }) {
        Object.assign(this, params)

        this.children = [
            {
                source$: this.state.service$({
                    namespace: this.namespace,
                    service: this.name,
                }),
                untilFirst: new PendingK8sView(),
                vdomMap: (resp: Service) => {
                    const content = (): AnyVirtualDOM => {
                        return {
                            tag: 'div',
                            children: resp.pods.map(
                                (pod) =>
                                    new K8sLinkView({
                                        kind: 'Pod',
                                        name: pod.name,
                                        namespace: pod.namespace,
                                        state: this.state,
                                        router: this.router,
                                    }),
                            ),
                        }
                    }

                    return new InlinedResourceView({
                        kind: 'Service',
                        name: this.name,
                        content,
                        state: this.state,
                        router: this.router,
                        namespace: this.namespace,
                        extraHeader: {
                            tag: 'strong',
                            innerText: resp.type,
                        },
                    })
                },
            },
        ]
    }

    static fromHtmlElement({
        elem,
        state,
        router,
    }: {
        elem: HTMLElement
        state: State
        router: Router
    }) {
        return new ServiceView({
            name: elem.getAttribute('target'),
            namespace: elem.getAttribute('namespace'),
            state,
            router,
        })
    }
}
