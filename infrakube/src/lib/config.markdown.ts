import { AnyVirtualDOM } from 'rx-vdom'
import { State } from './state'
import { MdPageView } from './utils.view'
import { Router } from 'mkdocs-ts'

export const url = (restOfPath: string) => `../assets/${restOfPath}`

export const mdPage = ({
    path,
    icon,
    name,
    state,
}: {
    path: string
    icon: string
    name: string
    state: State
}) => {
    const iconView: AnyVirtualDOM = icon.startsWith(State.urlBase)
        ? {
              tag: 'img',
              width: 25,
              src: icon,
          }
        : {
              tag: 'div' as const,
              class: `fas ${icon} me-2`,
          }
    return {
        name,
        header: {
            icon: iconView,
        },
        layout: {
            content: ({ router }: { router: Router }) =>
                new MdPageView({ path, state, router }),
        },
    }
}
