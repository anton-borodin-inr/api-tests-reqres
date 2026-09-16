from config import base_url, TIMEOUT


def test_product_lifecycle(api_session):
    payload = {"data": {
        "name": "Bialetti espresso machine",
        "price": 100,
        "category": "Electronics",
        "in_stock": True}
    }
    # POST
    response = api_session.post(f"{base_url}/api/collections/products/records", json=payload, timeout=TIMEOUT)
    assert response.status_code == 201, f"Expected 201 for new product, received {response.status_code}"
    body = response.json()
    assert "data" in body
    record = body["data"]
    assert "data" in record
    assert record["data"]["name"] == payload["data"][
        "name"], f"Expected name {payload['data']['name']}, got {record['data']['name']}"
    assert record["data"]["price"] == payload["data"][
        "price"], f"Expected price {payload['data']['price']}, got {record['data']['price']}"
    assert "created_at" in record
    assert "id" in record
    assert isinstance(record["id"], str), f"Expected 'id' to be str, got {type(record['id']).__name__}"
    product_id = record["id"]

    # GET_AFTER_POST
    response = api_session.get(f"{base_url}/api/collections/products/records/{product_id}", timeout=TIMEOUT)
    assert response.status_code == 200, f"Expected 200 for new product, received {response.status_code}"
    body = response.json()
    assert "data" in body
    record = body["data"]
    assert "data" in record
    product = record["data"]
    assert "id" in record
    assert record["id"] == product_id
    assert product["name"] == payload["data"]["name"]
    assert product["price"] == payload["data"]["price"]
    assert "created_at" in record

    # PUT
    updated_payload = {"data": {
        "name": "Bialetti espresso machine",
        "price": 200,
        "category": "Electronics",
        "in_stock": True}
    }
    put_update = api_session.put(f"{base_url}/api/collections/products/records/{product_id}", json=updated_payload, timeout=TIMEOUT)
    assert put_update.status_code == 200, f"Expected 200 for price update after PUT, received {put_update.status_code}"
    body = put_update.json()
    assert "data" in body
    record = body["data"]
    assert "data" in record
    product = record["data"]
    assert "id" in record
    assert record["id"] == product_id
    assert product["name"] == payload["data"]["name"]
    assert product["price"] == updated_payload["data"]["price"]
    assert "created_at" in record
    assert "updated_at" in record

    # GET_AFTER_PUT
    response = api_session.get(f"{base_url}/api/collections/products/records/{product_id}", timeout=TIMEOUT)
    assert response.status_code == 200, f"Expected 200 for GET after PUT, received {response.status_code}"
    body = response.json()
    assert "data" in body
    record = body["data"]
    assert "data" in record
    product = record["data"]
    assert "id" in record
    assert record["id"] == product_id
    assert product["name"] == payload["data"]["name"]
    assert product["price"] == updated_payload["data"]["price"]
    assert "created_at" in record
    assert "updated_at" in record
    assert product["category"] == payload["data"]["category"]
    assert product["in_stock"] is payload["data"]["in_stock"]

    # DELETE
    delete_product = api_session.delete(f"{base_url}/api/collections/products/records/{product_id}", timeout=TIMEOUT)
    assert delete_product.status_code == 204, f"Expected 204 for deleted product, received {delete_product.status_code}"

    # GET_AFTER_DELETE
    response = api_session.get(f"{base_url}/api/collections/products/records/{product_id}", timeout=TIMEOUT)
    assert response.status_code == 404, f"Expected 404 for deleted product, received {response.status_code}"
    body = response.json()
    assert "error" in body
    assert isinstance(body["error"], str)
    assert body["error"] == "record_not_found", f"Expected record_not_found, received {body['error']}"
