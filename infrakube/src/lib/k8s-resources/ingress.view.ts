import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { Ingress } from '../models'
import { parseMd, Router } from 'mkdocs-ts'
import { State } from '../state'
import { IngressRuleView } from '../widgets'
import { K8sLinkView } from '../utils.view'

export class IngressView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly ingress: Ingress
    public readonly state: State
    public readonly router: Router

    constructor(params: { ingress: Ingress; state: State; router: Router }) {
        Object.assign(this, params)
        this.children = [
            parseMd({
                src: `
## Rules

<rules></rules>

## TLS

<tls></tls>
`,
                router: this.router,
                views: {
                    rules: () => ({
                        tag: 'ul' as const,
                        children: this.ingress.rules.map((rule) => {
                            return new IngressRuleView({
                                rule,
                                namespace: this.ingress.namespace,
                                state: this.state,
                                router: this.router,
                            })
                        }),
                    }),
                    tls: () => ({
                        tag: 'ul' as const,
                        children: this.ingress.tls.map((tls) => {
                            return {
                                tag: 'li',
                                children: [
                                    new K8sLinkView({
                                        kind: 'Secret',
                                        name: tls.secretName,
                                        namespace: this.ingress.namespace,
                                        state: this.state,
                                        router: this.router,
                                    }),
                                ],
                            }
                        }),
                    }),
                },
            }),
        ]
    }
}
