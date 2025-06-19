import {
    attr$,
    AttributeLike,
    child$,
    ChildrenLike,
    EmptyDiv,
    VirtualDOM,
} from 'rx-vdom'
import { State } from '../state'
import { StructuredLogData } from '../models'
import { ImmutableTree, ObjectJs } from '@w3nest/rx-tree-views'
import {
    BehaviorSubject,
    combineLatest,
    Observable,
    Subject,
    switchMap,
} from 'rxjs'
import { parseMd } from 'mkdocs-ts'

export class LogsView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly class = 'overflow-auto'
    constructor({ state }: { state: State }) {
        const refresh$ = new Subject<boolean>()
        this.children = [
            {
                tag: 'button',
                class: 'btn btn-primary',
                innerText: 'refresh',
                onclick: () => refresh$.next(true),
            },
            child$({
                source$: refresh$.pipe(switchMap(() => state.logs$())),
                vdomMap: (resp) => {
                    const structured: StructuredLogData[] = resp.results
                        .filter((r) => typeof r.data !== 'string')
                        .map((r) => r.data) as unknown as StructuredLogData[]

                    const rootNode = createRootNode(structured)
                    const treeState = new ImmutableTree.State<Node>({
                        rootNode: rootNode,
                        expandedNodes: ['/'],
                    })
                    const view = new ImmutableTree.View<Node>({
                        state: treeState,
                        headerView: (_, node) => {
                            return new LogHeaderView({ node })
                        },
                    })
                    return view
                },
            }),
        ]
    }
}
export class LogHeaderView implements VirtualDOM<'div'> {
    static readonly CssSelector = 'infrakube-LogHeaderView'
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly class: AttributeLike<string>
    public readonly style = {
        cursor: 'pointer',
    }
    constructor({ node }: { node: RootNode | LogNode }) {
        if (node instanceof RootNode) {
            this.children = []
            return
        }
        const { labels, attributes, data, message } = node.log

        const toggledData$ = new BehaviorSubject<boolean>(false)
        const toggledMetadata$ = new BehaviorSubject<boolean>(false)

        this.class = attr$({
            source$: combineLatest([toggledData$, toggledMetadata$]),
            vdomMap: ([toggled1, toggled2]): string =>
                toggled1 || toggled2 ? 'mkdocs-bg-info' : '',
            wrapper: (d) =>
                `${d} ms-2 p-1 rounded ${LogHeaderView.CssSelector}`,
        })

        const toggleClass$ = (toggled$: Observable<boolean>) =>
            attr$({
                source$: toggled$,
                vdomMap: (toggled): string =>
                    toggled ? 'btn-primary' : 'btn-light',
                wrapper: (d) => `${d} btn btn-sm mx-1`,
            })
        const icon = () => {
            if (labels.includes('Label.DONE')) {
                return {
                    tag: 'i' as const,
                    class: 'fas fa-flag-checkered me-2',
                }
            }
            if (labels.includes('Label.FAILED')) {
                return {
                    tag: 'i' as const,
                    class: 'fas fa-times text-danger me-2',
                }
            }
            if (node instanceof EntryNode && Array.isArray(node.children)) {
                const error = node.children.find((l) => {
                    return (
                        l instanceof LogNode &&
                        l.log.labels.includes('Label.FAILED')
                    )
                })
                if (error) {
                    return {
                        tag: 'i' as const,
                        class: 'fas fa-times text-danger me-2',
                    }
                }
            }
            return undefined
        }
        const text = () => {
            if (labels.includes('Label.DONE')) {
                return message.split(' in ')[1]
            }
            if (labels.includes('Label.STARTED')) {
                return message.replace('<START>', '')
            }
            return message
        }

        const dataView = (title: string, data: unknown) => ({
            tag: 'div' as const,
            style: {
                fontFamily: 'monospace',
                fontSize: 'small',
            },
            children: [
                new ObjectJs.View({
                    state: new ObjectJs.State({
                        title,
                        data,
                        expandedNodes: [`${title}_0`],
                    }),
                }),
            ],
        })
        this.children = [
            {
                tag: 'div',
                class: 'd-flex align-items-center',
                style: {
                    whiteSpace: 'nowrap',
                },
                children: [
                    icon(),
                    parseMd({ src: text() }),
                    data && Object.keys(data).length > 0
                        ? {
                              tag: 'button',
                              class: toggleClass$(toggledData$),
                              innerText: 'data',
                              onclick: () =>
                                  toggledData$.next(!toggledData$.value),
                          }
                        : EmptyDiv,
                    {
                        tag: 'button',
                        class: toggleClass$(toggledMetadata$),
                        innerText: 'metadata',
                        onclick: () =>
                            toggledMetadata$.next(!toggledMetadata$.value),
                    },
                ],
            },
            child$({
                source$: toggledData$,
                vdomMap: (toggled) => {
                    if (!toggled) {
                        return EmptyDiv
                    }
                    return dataView('data', data)
                },
            }),
            child$({
                source$: toggledMetadata$,
                vdomMap: (toggled) => {
                    if (!toggled) {
                        return EmptyDiv
                    }
                    return dataView('metadata', {
                        labels,
                        attributes,
                    })
                },
            }),
        ]
    }
}

class Node extends ImmutableTree.Node {
    constructor({ id, children }: { id: string; children?: Node[] }) {
        super({ id, children })
    }
}

class RootNode extends Node {
    constructor({ children }: { children: LogNode[] }) {
        super({ id: '/', children })
    }
}
class LogNode extends Node {
    public readonly log: StructuredLogData
    constructor({
        log,
        children,
    }: {
        log: StructuredLogData
        children?: LogNode[]
    }) {
        super({ id: `${Math.floor(Math.random() * 1e6)}`, children })
        this.log = log
    }
}
class EntryNode extends LogNode {
    constructor({ log }: { log: StructuredLogData }) {
        super({ log, children: [] })
    }
}
class MessageNode extends LogNode {
    constructor({ log }: { log: StructuredLogData }) {
        super({ log })
    }
}

function createRootNode(logs: StructuredLogData[]): RootNode {
    const starts = logs.filter((log) => log.labels.includes('Label.STARTED'))
    const startsMap: { [spanId: string]: Node } = {
        root: new RootNode({ children: [] }),
    }

    starts.forEach((log) => {
        startsMap[log.spanId] = new EntryNode({ log })
    })
    logs.forEach((log) => {
        if (log.labels.includes('Label.STARTED')) {
            const parent = startsMap[log.parentId]
            if (parent) {
                const children = parent.children as LogNode[]
                children.unshift(startsMap[log.spanId] as EntryNode)
                children.sort((a, b) => a.log.timestamp - b.log.timestamp)
            }
        } else {
            const parent = startsMap[log.spanId]
            if (parent) {
                const children = parent.children as LogNode[]
                children.unshift(new MessageNode({ log }))
                children.sort((a, b) => a.log.timestamp - b.log.timestamp)
            }
        }
    })

    const dandlingStarts = starts
        .filter((start) => startsMap[start.parentId] === undefined)
        .map((s) => startsMap[s.spanId])

    const rootChildren = [
        ...(startsMap.root.children as LogNode[]),
        ...(dandlingStarts as LogNode[]),
    ].sort((a, b) => b.log.timestamp - a.log.timestamp)

    return new RootNode({ children: rootChildren })
}
