import { AppNav } from '..'
import { mdPage } from '../config.markdown'
import { State } from '../state'

import { navigation as navDeployments } from './deployments'
import { navigation as navAdmin } from './admin'

const mdPagesInput = {
    w3nest: { name: 'w3Nest', icon: 'fa-atlas', path: 'w3nest.md' },
    logs: {
        name: 'Logs',
        icon: 'fa-newspaper',
        path: 'w3nest.logs.md',
    },
}
export const navigation: (state: State) => AppNav = (state: State) => ({
    ...mdPage({ ...mdPagesInput.w3nest, state }),
    routes: {
        '/deployments': navDeployments(state),
        '/admin': navAdmin(state),
        '/logs': mdPage({ ...mdPagesInput.logs, state }),
    },
})
