import { AnyVirtualDOM, ChildrenLike, VirtualDOM } from 'rx-vdom'
import { State } from '../state'
import { PersistentVolume, PersistentVolumeList } from '../models'
import { K8sLinkView, PendingK8sView } from '../utils.view'
import { MdWidgets, parseMd, Router } from 'mkdocs-ts'

export class PersistentVolumesView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly children: ChildrenLike

    public readonly state: State
    public readonly router: Router
    public readonly namespace: string

    constructor(params: { state: State; router: Router }) {
        Object.assign(this, params)
        this.children = [
            {
                source$: this.state.persistentVolumes$(),
                untilFirst: new PendingK8sView(),
                vdomMap: (volumes: PersistentVolumeList) => {
                    return parseMd({
                        src: `
# Persistent Volumes

<volumes></volumes>
                    `,
                        router: this.state.router,
                        views: {
                            volumes: () => {
                                return {
                                    tag: 'div',
                                    children: volumes.items.map((volume) =>
                                        volumeView({
                                            volume,
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

function volumeView({
    volume,
    state,
    router,
}: {
    volume: PersistentVolume
    state: State
    router: Router
}): AnyVirtualDOM {
    return new MdWidgets.NoteView({
        label: volume.name,
        level: 'info',
        icon: 'fas fa-hdd',
        parsingArgs: {},
        content: parseMd({
            src: `
* **Status**: ${volume.status}                                                        
* **Capacity**: ${volume.capacity}
* **Access Modes**: ${volume.accessModes.reduce((acc, e) => acc + ', ' + e, '')} 
* **Storage Class**: ${volume.storageClass} 
* **Reclaim Policy**: ${volume.reclaimPolicy} 
* **Volume Mode**: ${volume.volumeMode}                                  
        
<pods></pods>
`,
            views: {
                pods: () => {
                    return {
                        tag: 'div',
                        children: volume.pods
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
