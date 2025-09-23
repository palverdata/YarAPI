from fastapi.openapi.utils import get_openapi
from typing import Iterable


def register_custom_swagger(app, secure_prefixes: Iterable[str] = ("/v1",)):
    """
    Adds a 'basicAuth' security scheme and marks only operations whose path
    starts with any prefix in `secure_prefixes` as requiring Basic Auth.
    Does NOT set a global `security` requirement.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(title=app.title, version=app.version, routes=app.routes)

    # 1) Ensure the security scheme exists
    comps = schema.setdefault("components", {}).setdefault("securitySchemes", {})
    comps["basicAuth"] = {"type": "http", "scheme": "basic"}

    # 2) Remove any global security if present (so only /v1 gets it)
    schema.pop("security", None)

    # 3) Add per-operation security only for paths under the desired prefixes
    auth_req = [{"basicAuth": []}]
    for path, path_item in schema.get("paths", {}).items():
        if not any(path.startswith(pfx) for pfx in secure_prefixes):
            continue

        # For each HTTP method object in the path item
        for method in (
            "get",
            "post",
            "put",
            "patch",
            "delete",
            "options",
            "head",
            "trace",
        ):
            op = path_item.get(method)
            if not op:
                continue
            # Respect explicit per-op security if you've set it elsewhere
            if "security" not in op:
                op["security"] = auth_req

    app.openapi_schema = schema
    return schema
