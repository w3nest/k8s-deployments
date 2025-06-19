import { ChildrenLike, EmptyDiv, VirtualDOM, child$ } from 'rx-vdom'
import { State } from '../state'
import { BehaviorSubject, ReplaySubject, switchMap, take, tap } from 'rxjs'
import { GuestUser } from '../models'

export class GuestsView implements VirtualDOM<'div'> {
    public readonly tag = 'div'
    public readonly class = 'border-left rounded'

    public readonly children: ChildrenLike

    constructor(params: { state: State }) {
        const users$ = new ReplaySubject<GuestUser[]>(1)
        const pending$ = new BehaviorSubject(true)

        params.state.guestUsers$().subscribe((users) => {
            pending$.next(false)
            users$.next(users)
        })
        this.children = [
            {
                tag: 'button',
                class: 'btn btn-sm btn-danger',
                innerText: 'Delete All',
                onclick: () => {
                    pending$.next(true)
                    params.state
                        .deleteGuests$()
                        .pipe(
                            switchMap(() => {
                                return params.state.guestUsers$()
                            }),
                            take(1),
                            tap(() => pending$.next(false)),
                        )
                        .subscribe((users) => users$.next(users))
                },
            },
            child$({
                source$: pending$,
                vdomMap: (pending) => {
                    return pending
                        ? { tag: 'i', class: 'fas fa-spinner fa-spin' }
                        : EmptyDiv
                },
            }),
            child$({
                source$: users$,
                vdomMap: (users) => {
                    return {
                        tag: 'div',
                        children: users.map((user) => {
                            return {
                                tag: 'div',
                                class: 'border rounded p-1 my-1',
                                innerText: user.username,
                            }
                        }),
                    }
                },
            }),
        ]
    }
}
