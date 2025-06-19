import { ChildrenLike, VirtualDOM } from 'rx-vdom'

export class LabelsView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'd-flex flex-wrap'
    public readonly children: ChildrenLike

    constructor(params: { labels: { [k: string]: string } }) {
        this.children = Object.entries(params.labels).map(([k, v]) => {
            return {
                tag: 'div',
                style: {
                    width: 'fit-content',
                },
                class: 'mx-2 my-1 p-1 d-flex align-items-center rounded bg-light',
                children: [
                    {
                        tag: 'div',
                        innerText: k,
                    },
                    {
                        tag: 'div',
                        class: 'mx-1',
                        innerText: ':',
                    },
                    {
                        tag: 'div',
                        innerText: v,
                    },
                ],
            }
        })
    }
}
