import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from db import execute_returning, fetch_all
from org import require_organization
from response import json_response
from clients.generateLatLng import generateLatLng


def lambda_handler(event, context):
    """
    PUT /clients/{id}
    """
    try:
        client_id = event.get("pathParameters", {}).get("id")
        body = json.loads(event.get("body") or "{}")

        if not client_id:
            return json_response(400, {"error": "id is required in the URL path"})

        org_id, err = require_organization(event, body)
        if err:
            return err

        allowed_fields = [
            "address",
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "city",
        ]
        updates = {k: v for k, v in body.items() if k in allowed_fields}

        if not updates:
            return json_response(400, {"error": "no valid fields to update"})

        if "address" in updates or "city" in updates:
            existing_rows = fetch_all(
                "SELECT address, city FROM clients WHERE id = %s AND organization_id = %s",
                (client_id, org_id),
            )
            if not existing_rows:
                return json_response(404, {"error": "client not found"})

            existing = existing_rows[0]
            address = updates.get("address", existing.get("address"))
            city = updates.get("city", existing.get("city"))
            coords = generateLatLng({"address": address, "city": city}) or {}

            updates["latitude"] = coords.get("latitude")
            updates["longitude"] = coords.get("longitude")
            updates["postal_code"] = coords.get("postal_code")

        set_clause = ", ".join(f"{field} = %s" for field in updates.keys())
        values = list(updates.values()) + [client_id, org_id]

        updated_row = execute_returning(
            f"UPDATE clients SET {set_clause} WHERE id = %s AND organization_id = %s RETURNING *",
            values,
        )

        if not updated_row:
            return json_response(404, {"error": "client not found"})

        return json_response(200, updated_row)
    except Exception as e:
        return json_response(500, {"error": str(e)})
