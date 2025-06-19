/* eslint-disable */
const runTimeDependencies = {
    "externals": {
        "@w3nest/rx-tree-views": "^0.2.0",
        "@w3nest/webpm-client": "^0.1.4",
        "mkdocs-ts": "^0.3.1",
        "rx-vdom": "^0.1.3",
        "rxjs": "^7.5.6"
    },
    "includedInBundle": {}
}
const externals = {
    "@w3nest/rx-tree-views": {
        "commonjs": "@w3nest/rx-tree-views",
        "commonjs2": "@w3nest/rx-tree-views",
        "root": "@w3nest/rx-tree-views_APIv02"
    },
    "@w3nest/webpm-client": {
        "commonjs": "@w3nest/webpm-client",
        "commonjs2": "@w3nest/webpm-client",
        "root": "@w3nest/webpm-client_APIv01"
    },
    "mkdocs-ts": {
        "commonjs": "mkdocs-ts",
        "commonjs2": "mkdocs-ts",
        "root": "mkdocs-ts_APIv03"
    },
    "rx-vdom": {
        "commonjs": "rx-vdom",
        "commonjs2": "rx-vdom",
        "root": "rx-vdom_APIv01"
    },
    "rxjs": {
        "commonjs": "rxjs",
        "commonjs2": "rxjs",
        "root": "rxjs_APIv7"
    },
    "rxjs/fetch": {
        "commonjs": "rxjs/fetch",
        "commonjs2": "rxjs/fetch",
        "root": [
            "rxjs_APIv7",
            "fetch"
        ]
    }
}
const exportedSymbols = {
    "@w3nest/rx-tree-views": {
        "apiKey": "02",
        "exportedSymbol": "@w3nest/rx-tree-views"
    },
    "@w3nest/webpm-client": {
        "apiKey": "01",
        "exportedSymbol": "@w3nest/webpm-client"
    },
    "mkdocs-ts": {
        "apiKey": "03",
        "exportedSymbol": "mkdocs-ts"
    },
    "rx-vdom": {
        "apiKey": "01",
        "exportedSymbol": "rx-vdom"
    },
    "rxjs": {
        "apiKey": "7",
        "exportedSymbol": "rxjs"
    }
}

const mainEntry: { entryFile: string; loadDependencies: string[] } =
    {
    "entryFile": "./index.ts",
    "loadDependencies": [
        "rx-vdom",
        "rxjs",
        "mkdocs-ts",
        "@w3nest/webpm-client",
        "@w3nest/rx-tree-views"
    ]
}

const secondaryEntries: {
    [k: string]: { entryFile: string; name: string; loadDependencies: string[] }
} = {}

const entries = {
    '@w3nest/infrakube': './index.ts',
    ...Object.values(secondaryEntries).reduce(
        (acc, e) => ({ ...acc, [e.name]: e.entryFile }),
        {},
    ),
}
export const setup = {
    name: '@w3nest/infrakube',
    assetId: 'QHczbmVzdC9pbmZyYWt1YmU=',
    version: '0.1.0-wip',
    webpmPath: '/api/assets-gateway/webpm/resources/QHczbmVzdC9pbmZyYWt1YmU=/0.1.0-wip',
    apiVersion: '01',
    runTimeDependencies,
    externals,
    exportedSymbols,
    entries,
    secondaryEntries,
    getDependencySymbolExported: (module: string) => {
        return `${exportedSymbols[module].exportedSymbol}_APIv${exportedSymbols[module].apiKey}`
    },

    installMainModule: ({
        cdnClient,
        installParameters,
    }: {
        cdnClient: {
            install: (_: unknown) => Promise<WindowOrWorkerGlobalScope>
        }
        installParameters?
    }) => {
        const parameters = installParameters || {}
        const scripts = parameters.scripts || []
        const modules = [
            ...(parameters.modules || []),
            ...mainEntry.loadDependencies.map(
                (d) => `${d}#${runTimeDependencies.externals[d]}`,
            ),
        ]
        return cdnClient
            .install({
                ...parameters,
                modules,
                scripts,
            })
            .then(() => {
                return window[`@w3nest/infrakube_APIv01`]
            })
    },
    installAuxiliaryModule: ({
        name,
        cdnClient,
        installParameters,
    }: {
        name: string
        cdnClient: {
            install: (_: unknown) => Promise<WindowOrWorkerGlobalScope>
        }
        installParameters?
    }) => {
        const entry = secondaryEntries[name]
        if (!entry) {
            throw Error(
                `Can not find the secondary entry '${name}'. Referenced in template.py?`,
            )
        }
        const parameters = installParameters || {}
        const scripts = [
            ...(parameters.scripts || []),
            `@w3nest/infrakube#0.1.0-wip~dist/${entry.name}.js`,
        ]
        const modules = [
            ...(parameters.modules || []),
            ...entry.loadDependencies.map(
                (d) => `${d}#${runTimeDependencies.externals[d]}`,
            ),
        ]
        return cdnClient
            .install({
                ...parameters,
                modules,
                scripts,
            })
            .then(() => {
                return window[`@w3nest/infrakube_APIv01`][`${entry.name}`]
            })
    },
    getCdnDependencies(name?: string) {
        if (name && !secondaryEntries[name]) {
            throw Error(
                `Can not find the secondary entry '${name}'. Referenced in template.py?`,
            )
        }
        const deps = name
            ? secondaryEntries[name].loadDependencies
            : mainEntry.loadDependencies

        return deps.map((d) => `${d}#${runTimeDependencies.externals[d]}`)
    },
}
