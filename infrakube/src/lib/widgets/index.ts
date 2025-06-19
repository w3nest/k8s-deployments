import { K8sDeploymentsRepoView } from './k8s-deployments-repo.view'
import { State } from '../state'
import { IngressView } from './ingress.view'
import { Router } from 'mkdocs-ts'
import { ServiceView } from './service.view'
import { K8sLinkView, K8sShellView, PortForwardView } from '../utils.view'
import { CrossLink, ExtLink, GitHubLink, ClusterLink } from './links'
import { LogsView } from '../w3nest/logs.view'
import { GuestsView } from './keycloak'

export * from './ingress.view'
export * from './service.view'
export * from './k8s-deployments-repo.view'

export const viewsFactory = ({
    state,
    router,
}: {
    state: State
    router: Router
}) => ({
    k8sDeploymentsReadMe: (elem: HTMLElement) => {
        return K8sDeploymentsRepoView.fromHtmlElement({ elem, state })
    },
    ingress: (elem: HTMLElement) => {
        return IngressView.fromHtmlElement({ elem, state, router })
    },
    service: (elem: HTMLElement) => {
        return ServiceView.fromHtmlElement({
            elem,
            state,
            router,
        })
    },
    k8sLink: (elem: HTMLElement) => {
        return K8sLinkView.fromHtmlElement({
            elem,
            state,
            router,
        })
    },
    portForward: (elem: HTMLElement) => {
        return PortForwardView.fromHtmlElement({
            elem,
            state,
            router,
        })
    },
    k8sShell: (elem: HTMLElement) => {
        return K8sShellView.fromHtmlElement({
            elem,
            state,
            router,
        })
    },
    'cluster-link': (elem: HTMLElement) => {
        return ClusterLink.fromHtmlElement({
            elem,
            state,
        })
    },
    'ext-link': (elem: HTMLElement) => new ExtLink(elem),
    'cross-link': (elem: HTMLElement) => new CrossLink(elem),
    'github-link': (elem: HTMLElement) => new GitHubLink(elem),
    logs: () => new LogsView({ state }),
    'guest-users': () => new GuestsView({ state }),
})
