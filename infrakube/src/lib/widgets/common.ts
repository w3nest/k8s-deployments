import { AnyVirtualDOM, ChildrenLike, VirtualDOM } from 'rx-vdom'
import { MdWidgets, Router } from 'mkdocs-ts'
import { State } from '../state'
import { iconsFactory, navBase } from '../utils.view'
import { K8sResourceKind } from '../models'

export class K8sResourceAnchor implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly innerText: string
    public readonly href: string
    public readonly onclick: (ev: MouseEvent) => void
    public readonly connectedCallback: (elem: HTMLAnchorElement) => void

    constructor(params: {
        namespace: string
        kind: K8sResourceKind
        name: string
        router: Router
        state: State
    }) {
        this.innerText = params.name
        const path = `${params.state.basePath}/namespace/${navBase[params.kind]}/${window.btoa(params.name)}`
        this.href = path
        this.onclick = (ev) => {
            ev.preventDefault()
            params.state.selectNamespace(params.namespace)
            params.router.fireNavigateTo({
                path,
            })
        }
    }
}

export class InlinedResourceView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = ''
    public readonly children: ChildrenLike

    constructor(params: {
        kind: K8sResourceKind
        name: string
        namespace: string
        extraHeader?: AnyVirtualDOM
        content: () => AnyVirtualDOM
        router: Router
        state: State
    }) {
        const sep = { tag: 'i' as const, class: 'mx-2' }
        this.children = [
            new MdWidgets.NoteView({
                level: 'hint',
                icon: `fas ${iconsFactory[params.kind]}`,
                label: {
                    tag: 'div',
                    class: 'd-flex align-items-center w-100',
                    children: [
                        {
                            tag: 'strong',
                            innerText: params.kind,
                        },
                        sep,
                        new K8sResourceAnchor({
                            namespace: params.namespace,
                            name: params.name,
                            kind: params.kind,
                            router: params.router,
                            state: params.state,
                        }),
                        sep,
                        params.extraHeader,
                    ],
                },
                content: params.content(),
                parsingArgs: {},
                expandable: true,
            }),
        ]
    }
}
