import { attr$, AttributeLike, ChildrenLike, VirtualDOM } from 'rx-vdom'
import { State } from '../state'

export class ExtLink implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly children: ChildrenLike
    public readonly innerText: string
    public readonly href: string
    public readonly target = '_blank'

    constructor(elem: HTMLElement) {
        const target = elem.getAttribute('target')
        if (!target) {
            return
        }
        const navs = {
            w3nest: '/apps/@w3nest/doc/latest',
            nginx: 'https://hub.docker.com/_/nginx/',
        }
        if (!(target in navs)) {
            return
        }
        this.href = navs[target as keyof typeof navs]
        this.children = [
            {
                tag: 'i',
                innerText: elem.textContent ?? '',
            },
            {
                tag: 'i',
                class: 'fas fa-external-link-alt',
                style: { transform: 'scale(0.6)' },
            },
        ]
    }
}

export class GitHubLink implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly children: ChildrenLike
    public readonly innerText: string
    public readonly href: string
    public readonly target = '_blank'

    constructor(elem: HTMLElement) {
        const target = elem.getAttribute('target')

        if (!target) {
            return
        }
        const navs = {
            'k8s-deployments': 'https://github.com/w3nest/k8s-deployments',
        }
        if (!(target in navs)) {
            return
        }
        this.href = navs[target as keyof typeof navs]
        this.children = [
            {
                tag: 'i',
                innerText: elem.textContent ?? '',
            },
            {
                tag: 'i',
                class: 'fab fa-github',
                style: { transform: 'scale(0.8)' },
            },
        ]
    }
}

export class CrossLink implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly children: ChildrenLike
    public readonly innerText: string
    public readonly href: string

    constructor(elem: HTMLElement) {
        const target = elem.getAttribute('target')
        if (!target) {
            return
        }
        const baseNav = '@nav/plugins/k8s-colab-plugin'
        const navs = {
            deployments: `${baseNav}/w3nest/deployments`,
            access: `${baseNav}/w3nest/access`,
            'deploy.cluster-setup': `${baseNav}/w3nest/deployments/cluster-setup`,
            'deploy.config': `${baseNav}/w3nest/deployments/configuration`,
            'deploy.infra': `${baseNav}/w3nest/deployments/infra`,
            'deploy.w3nest': `${baseNav}/w3nest/deployments/apps`,
            'db.restore': `${baseNav}/w3nest/databases/restore`,
        }
        if (!(target in navs)) {
            return
        }
        this.href = navs[target as keyof typeof navs]
        this.children = [
            {
                tag: 'i',
                innerText: elem.textContent ?? '',
            },
            {
                tag: 'i',
                class: 'fas fa-book-open',
                style: { transform: 'scale(0.6)' },
            },
        ]
    }
}

export class ClusterLink implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly class = 'align-items-center'
    public readonly children: ChildrenLike
    public readonly innerText: string
    public readonly style = {
        display: 'inline-block' as const,
    }
    public readonly href: AttributeLike<string>
    public readonly target = '_blank'

    constructor(params: { target: string; text: string; state: State }) {
        this.href = attr$({
            source$: params.state.configMap$({
                namespace: 'apps',
                configMap: 'cluster-config',
            }),
            vdomMap: ({ data }) =>
                `https://${data.clusterDomain}/${params.target}`,
        })
        this.children = [
            {
                tag: 'i',
                innerText: params.text,
            },
            {
                tag: 'i',
                class: 'fas fa-link',
                style: { transform: 'scale(0.6)' },
            },
        ]
    }

    static fromHtmlElement({
        elem,
        state,
    }: {
        elem: HTMLElement
        state: State
    }) {
        return new ClusterLink({
            text: elem.textContent ?? '',
            target: elem.getAttribute('target') ?? '',
            state,
        })
    }
}
