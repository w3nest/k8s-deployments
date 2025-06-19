import { ChildrenLike, VirtualDOM } from 'rx-vdom'
import { MdWidgets, parseMd, Router } from 'mkdocs-ts'
import { State } from '../state'
import { Container, Pod } from '../models'
import { LogsView } from './logs.view'

export class PodView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State
    public readonly namespace: string
    public readonly pod: Pod

    constructor(params: { namespace: string; pod: Pod; state: State }) {
        Object.assign(this, params)
        this.children = [
            parseMd({
                src: `
<note level="abstract" title="Resource info." expandable="true">
*  **Created at**: ${String(new Date(params.pod.creationTimestamp * 1000))}
*  **CPU usage**: ${Math.floor(params.pod.cpu / 1e3) / 1e6} cores
*  **Memory usage**: ${params.pod.memory / 1000} Mb
*  **Phase** : ${this.pod.resourceInfo.phase}
*  **IP** : ${this.pod.resourceInfo.podIP}
*  **QOS class** : ${this.pod.resourceInfo.qosClass}
*  **Service Account** : ${this.pod.resourceInfo.serviceAccount}
*  **Image Pull Secrets** : ${this.pod.resourceInfo.imagePullSecrets.reduce((acc, e) => acc + ' ' + e, '')}
</note>

<note level="quote" title="Logs" expandable="true">
<logs></logs>
</note>

<containers></containers>

<containers kind="Init Container"></containers>

`,
                views: {
                    logs: () => {
                        return new LogsView({
                            state: this.state,
                            namespace: this.namespace,
                            pod: this.pod.name,
                        })
                    },
                    containers: (elem) => {
                        const tKind = elem.getAttribute('kind')
                        const [kind, containers] =
                            tKind === 'Init Container'
                                ? [tKind, this.pod.initContainers]
                                : ['Container', this.pod.containers]
                        return {
                            tag: 'div',
                            children: containers.map(
                                (container) =>
                                    new ContainerView({
                                        container,
                                        router: this.state.router,
                                        kind: kind as unknown as
                                            | 'Container'
                                            | 'Init Container',
                                    }),
                            ),
                        }
                    },
                },
            }),
        ]
    }
}

export class ContainerView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike
    public readonly router: Router
    public readonly container: Container
    public readonly kind: 'Container' | 'Init Container'

    constructor(params: {
        container: Container
        router: Router
        kind: 'Container' | 'Init Container'
    }) {
        Object.assign(this, params)
        this.children = [
            parseMd({
                src: `
## ${this.kind} \`${this.container.name}\`

*  **Image** : ${this.container.image}
*  **Image Pull Policy** : ${this.container.imagePullPolicy}
   <command></command>
            `,
                router: this.router,
                views: {
                    command: () => {
                        return new CommandView({
                            command: this.container.command,
                        })
                    },
                },
            }),
        ]
    }
}

export class CommandView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    constructor({ command }: { command?: string[] }) {
        if (!command) {
            this.children = []
            return
        }
        this.children = [
            new MdWidgets.NoteView({
                label: 'Command',
                level: 'quote',
                expandable: true,
                parsingArgs: {},
                content: {
                    tag: 'div',
                    class: 'w-100 overflow-auto bg-dark text-light px-2',
                    children: [
                        {
                            tag: 'span',
                            innerText: command.reduce(
                                (acc, e) => `${acc}${e}\n`,
                                '',
                            ),
                        },
                    ],
                },
            }),
        ]
    }
}
