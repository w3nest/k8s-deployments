import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { State } from './state'
import { NamespaceRef, K8sResourceKind } from './models'
import { MdWidgets, parseMd, Router } from 'mkdocs-ts'
import { fromFetch } from 'rxjs/fetch'
import { ReplaySubject, switchMap } from 'rxjs'
import { viewsFactory } from './widgets'

export const iconsFactory: Record<K8sResourceKind, string> = {
    Ingress: 'fa-globe-africa',
    Pod: 'fa-object-group',
    Secret: 'fa-key',
    Service: 'fa-network-wired',
    ServiceAccount: 'fa-users-cog',
    ConfigMap: 'fa-wrench',
}
export const navBase: Record<K8sResourceKind, string> = {
    Ingress: 'ingresses',
    Secret: 'secrets',
    Pod: 'pods',
    Service: 'services',
    ServiceAccount: 'service-accounts',
    ConfigMap: 'config-maps',
}

export class PendingK8sView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'd-flex align-items-center'
    public readonly children: ChildrenLike

    constructor() {
        this.children = [
            {
                tag: 'img',
                width: 30,
                class: 'fas fa-spin',
                src: `${State.urlBase}/assets/icon.svg`,
            },
            { tag: 'div', class: 'mx-2' },
            {
                tag: 'div',
                innerText: 'Fetching K8s info...',
            },
        ]
    }
}

export class K8sCtxDropDown implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State

    constructor(params: { state: State }) {
        Object.assign(this, params)

        this.children = [
            {
                source$: this.state.k8sContexts$,
                untilFirst: {
                    tag: 'i',
                    class: 'fas fa-spinner fa-spin',
                },
                vdomMap: (k8sContexts: string[]) => {
                    return {
                        tag: 'select',
                        onchange: (ev: MouseEvent) => {
                            if (ev.target instanceof HTMLSelectElement) {
                                this.state.selectContext(ev.target.value)
                            }
                        },
                        children: k8sContexts.map((ctx) => {
                            return {
                                tag: 'option',
                                value: ctx,
                                selected: {
                                    source$: this.state.k8sContext$,
                                    vdomMap: (current: string) =>
                                        current === ctx,
                                },
                                innerText: ctx,
                            }
                        }),
                    }
                },
            },
        ]
    }
}

export class NamespaceDropDown implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'flex-grow-1'
    public readonly children: ChildrenLike

    public readonly state: State

    constructor(params: { state: State }) {
        Object.assign(this, params)

        this.children = [
            {
                source$: this.state.namespaces$,
                untilFirst: {
                    tag: 'i',
                    class: 'fas fa-spinner fa-spin',
                },
                vdomMap: (namespaces: NamespaceRef[]) => {
                    return {
                        tag: 'select',
                        onchange: (ev: MouseEvent) => {
                            if (ev.target instanceof HTMLSelectElement) {
                                this.state.selectNamespace(ev.target.value)
                            }
                        },
                        children: namespaces.map((namespace) => {
                            return {
                                tag: 'option',
                                value: namespace.name,
                                selected: {
                                    source$: this.state.selectedNamespace$,
                                    vdomMap: (current: string) =>
                                        current === namespace.name,
                                },
                                innerText: namespace.name,
                            }
                        }),
                    }
                },
            },
        ]
    }
}

export class K8sLinkView implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly class = 'w-100 border rounded px-1 align-items-center'
    public readonly style = {
        width: 'fit-content',
        whiteSpace: 'nowrap' as const,
        userSelect: 'none' as const,
        cursor: 'pointer' as const,
    }
    public readonly href: string
    public readonly children: ChildrenLike

    public readonly onclick: (ev: MouseEvent) => void

    public readonly name: string
    public readonly kind: string
    public readonly namespace: string
    public readonly state: State
    public readonly router: Router

    constructor(params: {
        kind: K8sResourceKind
        name: string
        namespace: string
        state: State
        router: Router
    }) {
        Object.assign(this, params)
        const path = `${this.state.basePath}/namespace/${navBase[this.kind]}/${window.btoa(this.name)}`
        this.onclick = (ev: MouseEvent) => {
            ev.preventDefault()
            this.state.selectNamespace(this.namespace)
            this.router.fireNavigateTo({
                path,
            })
        }
        this.children = [
            {
                tag: 'i',
                class: `fas ${iconsFactory[this.kind]}`,
            },
            {
                tag: 'i',
                class: 'mx-1',
            },
            {
                tag: 'i',
                innerText: `${this.name}`,
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
        return new K8sLinkView({
            name: elem.getAttribute('target'),
            namespace: elem.getAttribute('namespace'),
            kind: elem.getAttribute('kind') as K8sResourceKind,
            state,
            router,
        })
    }
}

export class PortForwardView implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly class = 'w-100 border rounded px-1 align-items-center'
    public readonly style = {
        width: 'fit-content',
        whiteSpace: 'nowrap' as const,
        userSelect: 'none' as const,
        cursor: 'pointer' as const,
    }
    public readonly href: string
    public readonly children: ChildrenLike

    public readonly onclick: (ev: MouseEvent) => void

    public readonly namespace: string
    public readonly service: string
    public readonly hostPort: number
    public readonly state: State
    public readonly router: Router

    constructor(params: {
        namespace: string
        service: string
        hostPort: number
        state: State
        router: Router
    }) {
        Object.assign(this, params)
        this.onclick = (ev: MouseEvent) => {
            ev.preventDefault()
            this.state
                .portForward$({
                    namespace: this.namespace,
                    service: this.service,
                    port: this.hostPort,
                })
                .subscribe((resp) => {
                    console.log('RESP!!', resp)
                    window.open(resp.url, '_blank').focus()
                })
        }
        this.children = [
            {
                tag: 'i',
                class: `fas ${iconsFactory.Service}`,
            },
            {
                tag: 'i',
                class: 'mx-1',
            },
            {
                tag: 'i',
                innerText: `Port-fwd ${this.service}`,
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
        return new PortForwardView({
            service: elem.getAttribute('target'),
            namespace: elem.getAttribute('namespace'),
            hostPort: parseInt(elem.getAttribute('hostPort')),
            state,
            router,
        })
    }
}

export class K8sShellView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'w-100 border p-1 rounded bg-light'
    public readonly children: ChildrenLike

    public readonly pwd?: string
    public readonly content: string
    public readonly state: State
    public readonly router: Router

    constructor(params: {
        pwd?: string
        content: string
        state: State
        router: Router
    }) {
        Object.assign(this, params)
        const editor = new MdWidgets.CodeSnippetView({
            language: 'unknown',
            content: this.content,
        })
        this.children = [
            this.pwd
                ? {
                      tag: 'div',
                      class: 'w-100 d-flex justify-content-center align-items-center',
                      children: [
                          {
                              tag: 'i',
                              class: 'fas fa-folder-open',
                          },
                          { tag: 'i', class: 'mx-2' },
                          { tag: 'i', innerText: this.pwd },
                      ],
                  }
                : undefined,
            {
                tag: 'div',
                style: { position: 'relative' },
                children: [
                    editor,
                    {
                        tag: 'button',
                        style: {
                            position: 'absolute',
                            top: '1%',
                            right: '1%',
                        },
                        class: 'btn btn-sm btn-light py-0 px-1',
                        children: [
                            {
                                tag: 'i',
                                class: 'fas fa-clipboard',
                            },
                        ],
                        onclick: () => {
                            void navigator.clipboard.writeText(this.content)
                        },
                    },
                ],
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
        return new K8sShellView({
            pwd: elem.getAttribute('pwd'),
            content: elem.textContent,
            state,
            router,
        })
    }
}

export class MdPageView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly state: State
    public readonly router: Router
    public readonly disconnected$ = new ReplaySubject<boolean>()

    constructor(params: { path: string; state: State; router: Router }) {
        Object.assign(this, params)
        const url = `${State.urlBase}/assets/${params.path}`

        this.children = [
            {
                source$: fromFetch(url).pipe(switchMap((resp) => resp.text())),
                untilFirst: new PendingK8sView(),
                vdomMap: (mdSrc: string) => {
                    return parseMd({
                        src: mdSrc,
                        router: this.router,
                        views: viewsFactory({
                            state: this.state,
                            router: this.router,
                        }),
                    })
                },
            },
        ]
    }
}

export function getDecoration(icon: string) {
    return {
        icon: {
            tag: 'i' as const,
            class: `fas ${icon} me-2`,
        },
    }
}
