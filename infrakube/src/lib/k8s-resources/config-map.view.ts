import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { State } from '../state'
import { Router, MdWidgets } from 'mkdocs-ts'
import { ConfigMap } from '../models'

export class ConfigMapView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State
    public readonly router: Router
    public readonly namespace: string
    public readonly configMap: ConfigMap

    constructor(params: {
        configMap: ConfigMap
        namespace: string
        state: State
        router: Router
    }) {
        Object.assign(this, params)
        this.children = [
            new MdWidgets.CodeSnippetView({
                language: 'javascript',
                content: JSON.stringify(this.configMap.data, null, 4),
            }),
        ]
    }
}
