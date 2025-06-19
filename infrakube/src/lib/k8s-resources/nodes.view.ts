import { AnyVirtualDOM, ChildrenLike, VirtualDOM } from 'rx-vdom'
import { parseMd, MdWidgets, Router } from 'mkdocs-ts'
import { State } from '../state'
import { NodeList, Node } from '../models'
import { K8sLinkView, PendingK8sView } from '../utils.view'

export class NodesView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly state: State
    public readonly router: Router

    constructor(params: { state: State; router: Router }) {
        Object.assign(this, params)

        this.children = [
            {
                source$: this.state.nodes$(),
                untilFirst: new PendingK8sView(),
                vdomMap: (nodes: NodeList) => {
                    return parseMd({
                        src: `
# Nodes

<nodes></nodes>
                    `,
                        router: this.state.router,
                        views: {
                            nodes: () => {
                                return {
                                    tag: 'div',
                                    children: nodes.items.map((node) =>
                                        nodeView({
                                            node,
                                            state: this.state,
                                            router: this.router,
                                        }),
                                    ),
                                }
                            },
                        },
                    })
                },
            },
        ]
    }
}

function nodeView({
    node,
    state,
    router,
}: {
    node: Node
    state: State
    router: Router
}): AnyVirtualDOM {
    return new MdWidgets.NoteView({
        label: node.name,
        level: 'info',
        icon: 'fas fa-server',
        parsingArgs: {},
        content: parseMd({
            src: `
* **Status**: ${node.status}                                                        
* **Internal IP**: ${node.internalIp}
* **External IP**: ${node.externalIp} 
* **Hostname**: ${node.hostname} 
* **memory capacity**: ${node.memoryCapacity} 
* **cpu capacity**: ${node.cpuCapacity}                                  
        
<pods></pods>
`,
            views: {
                pods: () => {
                    return {
                        tag: 'div',
                        children: node.pods
                            .sort((a, b) => a.name.localeCompare(b.name))
                            .map((pod) => ({
                                tag: 'div',
                                children: [
                                    new K8sLinkView({
                                        kind: 'Pod',
                                        state: state,
                                        router: router,
                                        name: pod.name,
                                        namespace: pod.namespace,
                                    }),
                                ],
                            })),
                    }
                },
            },
        }),
    })
}
