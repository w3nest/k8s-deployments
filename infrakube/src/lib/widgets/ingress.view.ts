import { AnyVirtualDOM, ChildrenLike, VirtualDOM } from 'rx-vdom'
import { Router } from 'mkdocs-ts'
import { Ingress, IngressRule } from '../models'
import { State } from '../state'
import { InlinedResourceView } from './common'
import { ServiceView } from './service.view'
import { K8sLinkView, PendingK8sView } from '../utils.view'

export class IngressRuleView implements VirtualDOM<'li'> {
    public readonly tag = 'li'
    public readonly class = 'border-left rounded'
    public readonly children: ChildrenLike
    public readonly rule: IngressRule

    constructor(params: {
        rule: IngressRule
        namespace: string
        state: State
        router: Router
    }) {
        const url = `${params.rule.host}${params.rule.path}`

        this.children = [
            {
                tag: 'a',
                innerText: url,
                href: `https://${url}`,
                target: '_blank',
            },
            new ServiceView({
                name: params.rule.service.name,
                namespace: params.namespace,
                state: params.state,
                router: params.router,
            }),
        ]
    }
}

export class IngressView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly state: State
    public readonly router: Router
    public readonly ingress: Ingress

    constructor(params: { ingress: Ingress; state: State; router: Router }) {
        Object.assign(this, params)

        const content = (): AnyVirtualDOM => {
            return {
                tag: 'div',

                children: [
                    {
                        tag: 'ul' as const,
                        innerText: 'Rules',
                        children: this.ingress.rules.map((rule) => {
                            return new IngressRuleView({
                                rule,
                                namespace: this.ingress.namespace,
                                state: this.state,
                                router: this.router,
                            })
                        }),
                    },
                    {
                        tag: 'ul' as const,
                        innerText: 'TLS',
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
                    },
                ],
            }
        }
        const firstUrl = `${this.ingress.rules[0].urlBase}`.split('(')[0]
        this.children = [
            new InlinedResourceView({
                kind: 'Ingress',
                name: this.ingress.name,
                content: content,
                extraHeader: {
                    tag: 'a',
                    target: '_blank',
                    href: firstUrl,
                    innerText: firstUrl,
                },
                state: this.state,
                router: this.router,
                namespace: this.ingress.namespace,
            }),
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
    }): VirtualDOM<'div'> {
        const ingress = elem.getAttribute('target')
        const namespace = elem.getAttribute('namespace')
        return {
            tag: 'div',
            children: [
                {
                    source$: state.ingress$({ ingress, namespace }),
                    untilFirst: new PendingK8sView(),
                    vdomMap: (ingressInfo: Ingress) => {
                        return new IngressView({
                            ingress: ingressInfo,
                            state,
                            router,
                        })
                    },
                },
            ],
        }
    }
}
