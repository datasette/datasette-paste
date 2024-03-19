from datasette import hookimpl, Response, Forbidden


async def paste_create_table(datasette, request):
    database = request.url_vars["database"]
    if not await can_paste(datasette, request.actor, database):
        raise Forbidden("Permission denied to import data")
    return Response.html(
        await datasette.render_template(
            "paste_create_table.html",
            {
                "database": database,
                "papaparse_url": datasette.urls.static_plugins(
                    "datasette-paste", "papaparse-5-4-1.min.js"
                ),
            },
            request=request,
        )
    )


@hookimpl
def register_routes():
    return [
        (r"^/(?P<database>[^/]+)/-/paste$", paste_create_table),
    ]


@hookimpl
def database_actions(datasette, actor, database):
    async def inner():
        if not await can_paste(datasette, actor, database):
            return []
        return [
            {
                "href": datasette.urls.database(database) + "/-/paste",
                "label": "Create table with pasted data",
                "description": "Paste in JSON, CSV or TSV data (e.g. from Google Sheets)",
            }
        ]

    return inner


async def can_paste(datasette, actor, database_name, to_table=None):
    if actor is None:
        return False
    if not to_table:
        # Need create-table for database
        can_create_table = await datasette.permission_allowed(
            actor, "create-table", resource=database_name
        )
        if not can_create_table:
            return False
        return True
    else:
        # Need insert-row for that table
        return await datasette.permission_allowed(
            actor, "insert-row", resource=(database_name, to_table)
        )
