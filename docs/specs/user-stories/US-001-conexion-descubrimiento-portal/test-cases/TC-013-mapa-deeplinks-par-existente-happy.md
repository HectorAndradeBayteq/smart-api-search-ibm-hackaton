# TC-013 — Dado que el sistema tiene el mapa de deeplinks construido con pares (path, MÉTODO) existentes, Cuando se consulta un par presente en el mapa, Entonces devuelve la URL correcta

**Perspectiva:** Happy Path
**Tipo de prueba:** Unit
**Prioridad:** Alta
**Criterio de aceptación:** AC-007 (Procesamiento de datos) — Mapa de deeplinks (path, MÉTODO) → URL
**Artefacto padre:** US-001
**Estado:** Ready
**Creado por:** David
**Fecha:** 2025-07-19

## Precondiciones

- El sistema ha procesado el detalle de una API que incluye recursos con paths y métodos HTTP.
- El detalle de la API contiene: `GET /payments/{id}` → URL deeplink `https://portal.example.com/apis/payments/resources/get-payment-by-id`.
- El entorno de prueba es unitario.

## Datos de prueba

| Campo | Valor | Notas |
|-------|-------|-------|
| path | /payments/{id} | Path del endpoint |
| metodo | GET | Método HTTP del endpoint |
| url_deeplink_esperada | https://portal.example.com/apis/payments/resources/get-payment-by-id | URL de deeplink para ese par |

## Pasos de ejecución

| # | Actor | Acción | Resultado esperado del paso |
|---|-------|--------|-----------------------------|
| 1 | Sistema | Construir el mapa de deeplinks a partir del detalle de la API | El mapa contiene la entrada `(GET, /payments/{id})` → URL |
| 2 | Verificador (test) | Consultar el mapa con la clave `(GET, /payments/{id})` | El mapa devuelve `https://portal.example.com/apis/payments/resources/get-payment-by-id` |
| 3 | Verificador (test) | Verificar que las claves del mapa incluyen el método en mayúsculas | El método HTTP se almacena en mayúsculas (`GET`, `POST`, etc.) |

## Resultado esperado final

El mapa de deeplinks contiene la entrada `(GET, /payments/{id})` y devuelve la URL correcta al consultarla. El par `(path, MÉTODO)` es la clave del mapa y la URL de deeplink es el valor.

## Observaciones

- Verificar que el método HTTP en la clave del mapa está normalizado en mayúsculas.
