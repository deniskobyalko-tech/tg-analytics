"""Tests for catalog, categories, and search API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_categories_returns_list():
    resp = client.get("/api/categories")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_catalog_returns_paginated():
    resp = client.get("/api/catalog?page=1&limit=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["meta"] is not None
    assert body["meta"]["page"] == 1
    assert body["meta"]["limit"] == 10


def test_catalog_limit_capped():
    resp = client.get("/api/catalog?page=1&limit=200")
    assert resp.status_code == 200
    body = resp.json()
    assert body["meta"]["limit"] == 100


def test_search_endpoint():
    resp = client.get("/api/search?q=test")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_search_empty_query():
    resp = client.get("/api/search?q=")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []
