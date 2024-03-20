from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
async def test_create_table_permissions():
    datasette = Datasette()
    datasette.add_memory_database("test")
    anon_response = await datasette.client.get("/test")
    assert anon_response.status_code == 200
    fragment = ">Create table with pasted data"
    assert fragment not in anon_response.text
    root_response = await datasette.client.get(
        "/test", cookies={"ds_actor": datasette.client.actor_cookie({"id": "root"})}
    )
    assert root_response.status_code == 200
    assert fragment in root_response.text
    # And check access to the /-/paste page
    anon_paste_response = await datasette.client.get("/test/-/paste")
    assert anon_paste_response.status_code == 403
    root_paste_response = await datasette.client.get(
        "/test/-/paste",
        cookies={"ds_actor": datasette.client.actor_cookie({"id": "root"})},
    )
    assert root_paste_response.status_code == 200
