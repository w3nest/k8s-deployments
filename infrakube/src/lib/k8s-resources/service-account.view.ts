import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { Router } from 'mkdocs-ts'
import { State } from '../state'
import { ResourceBase } from '../models'

export class ServiceAccountView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State
    public readonly serviceAccount: ResourceBase
    public readonly router: Router

    constructor(params: {
        state: State
        serviceAccount: ResourceBase
        router: Router
    }) {
        Object.assign(this, params)

        this.children = [
            new CopyTokenView({
                serviceAccount: this.serviceAccount,
                state: this.state,
            }),
        ]
    }
}

class CopyTokenView implements VirtualDOM<'button'> {
    public readonly tag = 'button'
    public readonly class =
        'btn btn-sm btn-light d-flex align-items-center my-1'
    public readonly children: ChildrenLike

    public readonly onclick: (ev: MouseEvent) => void
    constructor({
        serviceAccount,
        state,
    }: {
        serviceAccount: ResourceBase
        state: State
    }) {
        this.children = [
            {
                tag: 'i',
                class: 'fas fa-copy',
            },
            { tag: 'i', class: 'mx-1' },
            {
                tag: 'div',
                innerHTML: `Copy token`,
            },
        ]
        this.onclick = () => {
            state
                .serviceAccountToken$({
                    namespace: serviceAccount.namespace,
                    serviceAccount: serviceAccount.name,
                })
                .subscribe(({ token }) => {
                    void navigator.clipboard.writeText(token)
                })
        }
    }
}
