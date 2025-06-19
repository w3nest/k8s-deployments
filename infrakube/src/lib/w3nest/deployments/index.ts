import { AppNav } from '../..'
import { mdPage } from '../../config.markdown'
import { State } from '../../state'

export const mdPagesInput = {
    deployment: {
        name: 'Deployments',
        icon: 'fa-cloud-upload-alt',
        path: 'w3nest.deployments.md',
    },
    clusterSetup: {
        name: 'K8s Cluster Setup',
        icon: 'fas fa-server',
        path: 'w3nest.deployments.k8s-cluster-setup.md',
    },
    minikubePcSetup: {
        name: 'Minikube PC',
        icon: `${State.urlBase}/assets/minikube.png`,
        path: 'w3nest.deployments.k8s-cluster-setup.minikube-pc.md',
    },
    minikubeOvhSetup: {
        name: 'Minikube OVH',
        icon: `${State.urlBase}/assets/minikube.png`,
        path: 'w3nest.deployments.k8s-cluster-setup.minikube-ovh.md',
    },
    certificates: {
        name: 'Certificates',
        icon: 'fas fa-shield-alt',
        path: 'w3nest.deployments.k8s-cluster-setup.certificates.md',
    },
    configuration: {
        name: 'Configuration',
        icon: 'fas fa-wrench',
        path: 'w3nest.deployments.configuration.md',
    },
    infra: {
        name: 'Infra',
        icon: 'fas fa-network-wired',
        path: 'w3nest.deployments.infra.md',
    },
    kcRealm: {
        name: 'KC W3nest Realm',
        icon: 'fas fa-university',
        path: 'w3nest.deployments.infra.kc-realm.md',
    },
    apps: {
        name: 'W3Nest Services',
        icon: 'fas fa-subway',
        path: 'w3nest.deployments.w3nest-services.md',
    },
    misc: {
        name: 'Misc',
        icon: 'fas fa-sticky-note',
        path: 'w3nest.deployments.misc.md',
    },
}
export const navigation: (state: State) => AppNav = (state: State) => ({
    ...mdPage({ ...mdPagesInput.deployment, state }),
    routes: {
        '/cluster-setup': {
            ...mdPage({ ...mdPagesInput.clusterSetup, state }),
            routes: {
                '/minikube-pc': mdPage({
                    ...mdPagesInput.minikubePcSetup,
                    state,
                }),
                '/minikube-ovh': mdPage({
                    ...mdPagesInput.minikubeOvhSetup,
                    state,
                }),
                '/certificates': mdPage({
                    ...mdPagesInput.certificates,
                    state,
                }),
            },
        },
        '/configuration': mdPage({ ...mdPagesInput.configuration, state }),
        '/infra': {
            ...mdPage({ ...mdPagesInput.infra, state }),
            routes: {
                '/kc-realm': mdPage({ ...mdPagesInput.kcRealm, state }),
            },
        },
        '/apps': mdPage({ ...mdPagesInput.apps, state }),
        '/misc': mdPage({ ...mdPagesInput.misc, state }),
    },
})
