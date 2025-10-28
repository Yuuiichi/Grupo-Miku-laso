# tests/test_ejemplares.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_buscar_ejemplares_por_codigo():
    # Simula una solicitud GET a /ejemplares/codigo/{codigo}
    response = client.get("/ejemplares/codigo/LIT-ESP-001-01")
    assert response.status_code == 200
    assert "codigo" in response.json()
    assert response.json()["codigo"] == "LIT-ESP-001-01"

def test_buscar_ejemplares_por_documento():
    # Simula una solicitud GET a /documentos/{id}/ejemplares
    response = client.get("/documentos/1/ejemplares")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0  # Asegúrate de que se devuelvan ejemplares

def test_filtros_disponibilidad():
    # Simula una solicitud GET a /documentos/{id}/disponibilidad
    response = client.get("/documentos/1/disponibilidad")
    assert response.status_code == 200
    data = response.json()
    assert "disponibles" in data
    assert "prestados_sala" in data
    assert "prestados_domicilio" in data
    assert data["disponibles"] >= 0

def test_ejemplares_disponibles():
    # Simula una solicitud GET a /ejemplares/disponibles
    response = client.get("/ejemplares/disponibles")
    assert response.status_code == 200
    ejemplares = response.json()
    assert isinstance(ejemplares, list)
    for ejemplar in ejemplares:
        assert ejemplar["estado"] == "disponible"

def test_codigo_unico():
    # Simula una solicitud POST a /ejemplares
    data = {
        "documento_id": 1,
        "codigo": "LIT-ESP-001-01",
        "ubicacion": "A1"
    }
    response = client.post("/ejemplares", json=data)
    assert response.status_code == 200

    # Intentar crear un ejemplar con el mismo código
    response_duplicate = client.post("/ejemplares", json=data)
    assert response_duplicate.status_code == 400  # Error de código duplicado
    assert "detail" in response_duplicate.json()

def test_marcar_como_prestado():
    # Crear un ejemplar en estado disponible primero
    data = {
        "documento_id": 1,
        "codigo": "LIT-ESP-001-01",
        "ubicacion": "A1"
    }
    response_create = client.post("/ejemplares", json=data)
    assert response_create.status_code == 200
    ejemplar_id = response_create.json()["id"]

    # Intentar marcarlo como prestado
    response = client.patch(f"/ejemplares/{ejemplar_id}/estado", json={"estado": "prestado"})
    assert response.status_code == 200
    assert response.json()["estado"] == "prestado"

    # Intentar marcar como prestado cuando no está disponible
    response = client.patch(f"/ejemplares/{ejemplar_id}/estado", json={"estado": "prestado"})
    assert response.status_code == 400  # No debe permitir cambiar a prestado si no está disponible

def test_devolucion_de_ejemplares():
    # Crear un ejemplar prestado primero
    data = {
        "documento_id": 1,
        "codigo": "LIT-ESP-001-01",
        "ubicacion": "A1"
    }
    response_create = client.post("/ejemplares", json=data)
    ejemplar_id = response_create.json()["id"]
    client.patch(f"/ejemplares/{ejemplar_id}/estado", json={"estado": "prestado"})

    # Simular devolución
    response = client.post("/devoluciones", json={"ejemplar_codigo": "LIT-ESP-001-01"})
    assert response.status_code == 200
    assert response.json()["estado"] == "devuelto"

    # Verificar que el ejemplar ahora esté disponible
    response = client.get(f"/ejemplares/codigo/LIT-ESP-001-01")
    assert response.json()["estado"] == "disponible"

def test_transiciones_de_estado():
    # Crear ejemplar
    data = {
        "documento_id": 1,
        "codigo": "LIT-ESP-001-01",
        "ubicacion": "A1"
    }
    response_create = client.post("/ejemplares", json=data)
    ejemplar_id = response_create.json()["id"]

    # Marcar como prestado
    response = client.patch(f"/ejemplares/{ejemplar_id}/estado", json={"estado": "prestado"})
    assert response.status_code == 200
    assert response.json()["estado"] == "prestado"

    # Intentar cambiar de "prestado" a "disponible" directamente
    response_invalid = client.patch(f"/ejemplares/{ejemplar_id}/estado", json={"estado": "disponible"})
    assert response_invalid.status_code == 400  # Debe pasar por "devuelto" antes
