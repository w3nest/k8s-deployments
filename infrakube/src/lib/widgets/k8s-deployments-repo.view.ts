import { VirtualDOM, AttributeLike } from 'rx-vdom'
import { State } from '../state'
import { Context } from '../models'

export class K8sDeploymentsRepoView implements VirtualDOM<'a'> {
    public readonly tag = 'a'
    public readonly innerText: string
    public readonly href: AttributeLike<string>
    public readonly target = '_blank'

    constructor(params: { text: string; path: string; state: State }) {
        this.href = {
            source$: params.state.context$(),
            vdomMap: (info: Context) => {
                return `https://github.com/w3nest/k8s-deployments/tree/${info.cluster}/${params.path}`
            },
        }
        this.innerText = params.text
    }

    static fromHtmlElement({
        elem,
        state,
    }: {
        elem: HTMLElement
        state: State
    }) {
        return new K8sDeploymentsRepoView({
            state,
            text: elem.textContent,
            path: elem.getAttribute('path'),
        })
    }
}
