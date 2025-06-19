import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { parseMd, Router } from 'mkdocs-ts'
import { State } from '../state'
import { Secret } from '../models'

export class SecretView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State
    public readonly namespace: string
    public readonly secret: Secret
    public readonly router: Router

    constructor(params: {
        state: State
        namespace: string
        secret: Secret
        router: Router
    }) {
        Object.assign(this, params)

        this.children = [
            parseMd({
                src: `
<copySecrets></copySecrets>
                        `,
                router: this.router,
                views: {
                    copySecrets: () => {
                        return new CopySecretsView(this.secret.data)
                    },
                },
            }),
        ]
    }
}

class CopySecretsView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    constructor(secrets: { [k: string]: string }) {
        this.children = Object.entries(secrets).map(([k, v]) => {
            return new CopySecretView({ title: k, token: v })
        })
    }
}

class CopySecretView implements VirtualDOM<'button'> {
    public readonly tag = 'button'
    public readonly class =
        'btn btn-sm btn-light d-flex align-items-center my-1'
    public readonly children: ChildrenLike

    public readonly onclick: (ev: MouseEvent) => void
    constructor({ token, title }: { token: string; title: string }) {
        this.children = [
            {
                tag: 'i',
                class: 'fas fa-copy',
            },
            { tag: 'i', class: 'mx-1' },
            {
                tag: 'div',
                innerHTML: `Copy <i>${title}</i> secret`,
            },
        ]
        this.onclick = () => {
            void navigator.clipboard.writeText(token)
        }
    }
}
