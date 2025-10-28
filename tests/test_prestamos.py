def test_crear_prestamo_marca_ejemplares_como_prestados(client, db):

    from app.models.usuario import Usuario
    from app.models.ejemplar import Ejemplar

    u = Usuario(id=1, rut="11111111-1", nombres="Juan", apellidos="Pérez", email="juan@a.com", password_hash="x", rol="usuario", activo=True)
    b = Usuario(id=2, rut="22222222-2", nombres="Ana", apellidos="Biblio", email="ana@b.com", password_hash="x", rol="bibliotecario", activo=True)
    ej1 = Ejemplar(id=1, documento_id=1, codigo="LIB-001", estado="disponible", ubicacion="A1")
    ej2 = Ejemplar(id=2, documento_id=1, codigo="LIB-002", estado="disponible", ubicacion="A1")

    db.add_all([u, b, ej1, ej2])
    db.commit()

    response = client.post(
        "/prestamos/registrar",
        json={
            "tipo_prestamo": "domicilio",
            "usuario_id": 1,
            "bibliotecario_id": 2,
            "ejemplares_ids": [1, 2]
        }
    )

    assert response.status_code == 200
    data = response.json()

    ej1_db = db.query(Ejemplar).get(1)
    ej2_db = db.query(Ejemplar).get(2)
    assert ej1_db.estado == "prestado"
    assert ej2_db.estado == "prestado"