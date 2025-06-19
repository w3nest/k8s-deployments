import { AppNav } from '../..'
import { mdPage } from '../../config.markdown'
import { State } from '../../state'

const mdPagesInput = {
    admin: { name: 'Admin', icon: 'fa-users-cog', path: 'w3nest.admin.md' },
    keycloak: {
        name: 'Keycloak',
        icon: 'fa-id-card',
        path: 'w3nest.admin.keycloak.md',
    },
}
export const navigation: (state: State) => AppNav = (state: State) => ({
    ...mdPage({ ...mdPagesInput.admin, state }),
    routes: {
        '/admin': mdPage({ ...mdPagesInput.keycloak, state }),
    },
})
