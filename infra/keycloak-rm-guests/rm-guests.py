import asyncio
from datetime import datetime
import getpass
import os
from pathlib import Path
import signal

import psutil

from w3nest_client import AioHttpExecutor, ContextReporter, LogEntry
from w3nest_client.context import Context

from w3nest_infrakube_backend.environment import Environment

from w3nest_client.oidc import OidcConfig, KeycloakUsersManagement

from w3nest_infrakube_backend.routers.w3nest import (
    GuestUser,
    users_mgr_client,
    explorer_client,
)

from w3nest.app.config.cloud import (
    get_standard_auth_provider,
)


class ConsoleContextReporter(ContextReporter):

    entries: list[LogEntry] = []

    async def log(self, entry: LogEntry):
        self.entries.append(entry)
        if "Label.STD_OUTPUT" in entry.labels:
            print(entry.text)


async def tear_down(context: Context):

    async with context.start(action="tear_down") as ctx:
        for k, v in Environment.port_fwds.items():
            await ctx.terminal("lookup", f"Kill port fwd on {k}")
            pid = v[1]
            try:
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait(timeout=5)
                print(f"Process {pid} terminated.")
            except psutil.NoSuchProcess:
                print(f"No such process: {pid}")
            except psutil.TimeoutExpired:
                print(f"Process {pid} did not terminate in time.")


async def remove_guest(
    k8s_ctx: str,
    guest: GuestUser,
    users_client: KeycloakUsersManagement,
    guests_error: list[str],
    context: Context,
):
    async with context.start(action="remove_guest") as ctx:

        explorer = await explorer_client(
            k8s_ctx=k8s_ctx, request_executor=AioHttpExecutor()
        )
        creation_date = datetime.fromtimestamp(guest.createdTimestamp / 1000)
        await ctx.terminal(
            "in_progress",
            f"Start removing {guest.username} created at {creation_date}",
        )
        headers = ctx.headers()

        resp = await explorer.get_drives(
            group_id=f"private_{guest.id}",
            headers=headers,
        )
        if len(resp.drives) > 0:
            await ctx.terminal(
                "forbidden",
                f"Can not remove user {guest.id}: there are drives associated ",
            )
            guests_error.append(guest.id)
            return

        await ctx.terminal(
            "info", f"No data associated to guest, proceed to deletion ({guest.id})"
        )
        await users_client.delete_user(user_id=guest.id, context=ctx)
        await ctx.terminal("success", f"Guest {guest.id} deleted")

        with open(Path(__file__).parent / "output_logs.txt", "a") as file:
            file.writelines([f"{guest.id} {guest.createdTimestamp}\n"])


async def remove_guests_chunk(
    k8s_ctx: str,
    chunk: list[GuestUser],
    guests_error: list[str],
    users_client,
    admin_name: str,
    admin_pwd: str,
    context: Context,
):
    auth_provider = get_standard_auth_provider(host="w3nest.org")
    oidc_client = OidcConfig(auth_provider.openidBaseUrl).for_client(
        auth_provider.openidClient
    )
    tokens_data = await oidc_client.direct_auth_flow(
        username=admin_name,
        password=admin_pwd,
        context=context,
    )
    async with context.start(
        action="remove_guests_chunk",
        with_headers={
            "authorization": f"Bearer {tokens_data.access_token}",
        },
        on_exit=tear_down,
    ) as ctx:

        for guest in chunk:
            await remove_guest(
                k8s_ctx=k8s_ctx,
                users_client=users_client,
                guest=GuestUser(
                    id=guest.id,
                    username=guest.username,
                    createdTimestamp=guest.createdTimestamp,
                ),
                guests_error=guests_error,
                context=ctx,
            )


async def remove_guests(
    k8s_ctx: str,
    admin_name: str,
    admin_pwd: str,
    guests_error: list[str],
    context: Context,
):

    async with context.start(
        action="remove_guests",
        with_headers={
            "x-trace-id": "rm-guest-users",
        },
        on_exit=tear_down,
    ) as ctx:

        def handle_sigint(*_):
            print("Interrupted. Cleaning up...")
            loop.run_until_complete(tear_down(context))
            exit(0)

        signal.signal(signal.SIGINT, handle_sigint)

        users_client = await users_mgr_client(k8s_ctx=k8s_ctx)

        while True:
            guests = await users_client.get_temporary_users(first=0, context=ctx)
            valid_guests = [
                GuestUser(
                    id=g.id,
                    username=g.username,
                    createdTimestamp=g.createdTimestamp,
                )
                for g in guests
                if g.id not in guests_error
            ]
            if not valid_guests:
                await ctx.terminal("success", f"No more guests to delete.")
                break

            await remove_guests_chunk(
                k8s_ctx=k8s_ctx,
                chunk=valid_guests,
                guests_error=guests_error,
                users_client=users_client,
                admin_name=admin_name,
                admin_pwd=admin_pwd,
                context=ctx,
            )


context = Context(logs_reporters=[ConsoleContextReporter()])

loop = asyncio.get_event_loop()

guests_error = []

admin_pwd = getpass.getpass("Password: ")
admin_name = os.environ.get("ADMIN_NAME")
if not admin_name:
    raise RuntimeError(
        "Admin name should be provide as environment variable 'ADMIN_NAME'"
    )
loop.run_until_complete(
    remove_guests(
        k8s_ctx="minikube-ovh",
        admin_name=admin_name,
        admin_pwd=admin_pwd,
        guests_error=guests_error,
        context=context,
    )
)

if guests_error:
    print("Error deleting guests for:")
    print(guests_error)
