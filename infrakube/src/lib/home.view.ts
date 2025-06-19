import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { parseMd } from 'mkdocs-ts'
import { State } from './state'
import { Context } from './models'
import { PendingK8sView } from './utils.view'

export class HomeView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly state: State
    constructor(params: { state: State }) {
        Object.assign(this, params)

        this.children = [
            {
                source$: this.state.context$(),
                untilFirst: new PendingK8sView(),
                vdomMap: (info: Context) => {
                    return parseMd({
                        src: `
# Context \`${info.name}\`

*  **cluster**: ${info.cluster}
*  **user**: ${info.user}
                        `,
                        router: this.state.router,
                    })
                },
            },
        ]
    }
}
