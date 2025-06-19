import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { State } from '../state'
import { PendingK8sView } from '../utils.view'

export type LogEntry = {
    timestamp: string
    message: string
    data: { [k: string]: unknown }
}
export type LogsResponse = {
    logs: LogEntry[]
}

export class LogsView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'overflow-auto'
    public readonly style = {
        height: '50vh',
    }
    public readonly children: ChildrenLike
    public readonly state: State
    public readonly namespace: string
    public readonly pod: string

    constructor(params: { state: State; namespace: string; pod: string }) {
        Object.assign(this, params)

        this.children = [
            {
                source$: this.state.podLogs$({
                    namespace: this.namespace,
                    pod: this.pod,
                }),
                untilFirst: new PendingK8sView(),
                vdomMap: (resp: LogsResponse) => {
                    return {
                        tag: 'div',
                        children: resp.logs.map((l) => {
                            return {
                                tag: 'pre',
                                class: 'm-0',
                                style: {
                                    width: 'fit-content',
                                },
                                innerText: `${l.timestamp} : ${l.message}`,
                            }
                        }),
                    }
                },
            },
        ]
    }
}
