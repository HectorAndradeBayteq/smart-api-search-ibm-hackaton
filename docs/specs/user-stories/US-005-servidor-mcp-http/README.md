# US-005: Servidor MCP HTTP con herramientas de búsqueda y consulta de spec

**Estado:** Ready
**Fecha de creación:** 2025-07-19
**Última actualización:** 2025-07-19

## Descripción

**COMO** desarrollador que trabaja en un IDE compatible con MCP (IBM Bob, VS Code, Cursor, GitHub Copilot)
**QUIERO** conectar mi IDE a un servidor MCP HTTP que exponga las herramientas de búsqueda semántica y consulta de spec de APIs
**PARA** descubrir y explorar endpoints de API en lenguaje natural directamente desde mi entorno de desarrollo sin salir del IDE

## Contexto

El servidor MCP se expone sobre transporte `streamable-http` mediante FastMCP y uvicorn. Debe arrancarse por referencia ASGI del módulo (nunca ejecutando el módulo como `__main__`) para evitar que el paquete cargue dos veces y que uvicorn sirva una segunda instancia sin herramientas registradas. El servidor opera en modo sin estado: no comparte memoria con el proceso de ingesta.

## Reglas de negocio

- **BR-01:** El servidor DEBE exponerse mediante la referencia ASGI del módulo; está PROHIBIDO ejecutarlo como `__main__`. El paquete NO DEBE reexportar símbolos que sombreen a sus propios submódulos. → verificado por AC-008
- **BR-02:** `get_endpoint_spec` DEBE tratar un `spec_ref` inválido o no encontrado como error de herramienta, NO como excepción del servidor. → verificado por AC-005

## Referencias

- Ninguna por ahora

## Criterios de aceptación

- **AC-001 (Integraciones):** El servidor DEBE arrancar con uvicorn en los valores de `MCP_HOST`, `MCP_PORT` y `MCP_PATH`, con valores por defecto `127.0.0.1`, `8000` y `/mcp` respectivamente, en modo sin estado.
- **AC-002 (Reglas de negocio):** Un middleware DEBE interceptar peticiones `GET` al endpoint MCP y DEBE responder `405 Method Not Allowed` con cabecera `Allow: POST, DELETE`.
  Casos de prueba: [TC-003](./test-cases/TC-003-middleware-get-405-happy.md)
- **AC-003 (Salidas del sistema):** La herramienta `search_openapi(query, top_k=5)` DEBE devolver markdown compacto más contenido estructurado; NO DEBE devolver el JSON OpenAPI completo.
- **AC-004 (Salidas del sistema):** La herramienta `get_endpoint_spec(spec_ref)` DEBE devolver markdown más contenido estructurado con el fragmento OpenAPI, la URL de llamada y el deeplink del endpoint solicitado.
- **AC-005 (Fiabilidad):** Un `spec_ref` inválido o no encontrado en `get_endpoint_spec` DEBE marcarse como error de herramienta; NO DEBE propagarse como excepción del servidor.
  Casos de prueba: [TC-004](./test-cases/TC-004-get-endpoint-spec-ref-invalido-tool-error.md)
- **AC-006 (Interacción de usuario):** DEBE existir un prompt `find_backend_api(need)` que guíe el flujo: buscar → presentar → pedir el spec solo si el usuario lo solicita explícitamente.
- **AC-007 (Interacción de usuario):** Las instrucciones del servidor DEBEN indicar: usar esta base de conocimiento para descubrir APIs, no buscar en el workspace, no traducir los nombres de categoría y no pegar JSON salvo petición explícita del usuario.
- **AC-008 (Fiabilidad):** El servidor DEBE exponerse mediante la referencia ASGI del módulo, nunca ejecutando el módulo como `__main__`; el paquete NO DEBE reexportar símbolos que sombreen a sus propios submódulos.
  Casos de prueba: [TC-001](./test-cases/TC-001-asgi-init-no-reexporta-simbolos-happy.md)
- **AC-009 (Fiabilidad):** DEBE existir una verificación sobre el mismo objeto ASGI que sirve el entrypoint de producción que afirme que expone las dos herramientas (`search_openapi`, `get_endpoint_spec`) y el prompt (`find_backend_api`); importar la aplicación por un camino distinto al de producción no es suficiente.
  Casos de prueba: [TC-002](./test-cases/TC-002-asgi-app-registra-herramientas-y-prompt-happy.md)
- **AC-010 (Salidas del sistema):** DEBE entregarse un ejemplo de configuración de cliente MCP (`type: http` y URL) usable en IBM Bob, VS Code, Cursor y GitHub Copilot, más un script `.ps1` de arranque que use el Python del entorno virtual.
- **AC-011 (Salidas del sistema):** El README del repositorio DEBE documentar cómo registrar el servidor en IBM Bob.

---

## Complejidad sugerida

- **Story points:** 5
- **Justificación:** La exposición MCP, el middleware de método, las dos herramientas, el prompt y la documentación de configuración son piezas bien delimitadas. El requisito crítico de arranque por referencia ASGI (AC-008/AC-009) añade riesgo de integración.

## Repositorios

- smart-api-search-ibm-hackaton

## Validación

### INVEST

| Letra | Criterio      | Resultado | Notas |
| ----- | ------------- | --------- | ----- |
| **I** | Independiente | Parcial   | Depende de que las herramientas `search_openapi` (US-004) y `get_endpoint_spec` existan; el servidor puede implementarse y probarse con stubs de esas herramientas. |
| **N** | Negociable    | Cumple    | Los valores por defecto de host/puerto, el formato del markdown de respuesta y los IDEs documentados son negociables. |
| **V** | Valiosa       | Cumple    | Sin el servidor el desarrollador no puede usar el sistema desde su IDE; es la capa de exposición de todo el valor del producto. |
| **E** | Estimable     | Cumple    | FastMCP, uvicorn y el protocolo MCP son conocidos; el riesgo de la referencia ASGI está documentado y cuantificado. |
| **S** | Cumple        | Cumple    | Alcance acotado al servidor y su documentación; no incluye lógica de búsqueda ni de ingesta. |
| **T** | Cumple        | Cumple    | Todos los criterios son verificables; AC-009 exige una prueba específica sobre el objeto ASGI de producción. |

### Definition of Ready (DoR)

| Criterio DoR                       | Estado  | Notas |
| ---------------------------------- | ------- | ----- |
| Dependencias listas                | Cumple  | FastMCP y uvicorn están en el stack del proyecto; las herramientas pueden desarrollarse en paralelo con stubs. |
| Inputs/outputs claros              | Cumple  | Entradas: peticiones HTTP MCP del IDE. Salidas: respuestas markdown estructuradas de las dos herramientas y el prompt. |
| Repositorios definidos             | Cumple  | smart-api-search-ibm-hackaton |
| Sin decisiones técnicas pendientes | Cumple  | Arranque ASGI, middleware de método, herramientas y prompt están especificados; el requisito de verificabilidad AC-009 cubre el riesgo de la doble instancia. |
| Referencias de UI                  | No aplica | El IDE es el cliente; el servidor no tiene UI propia. |
| Sin aclaraciones pendientes        | Cumple  | Ninguna. |

## Observaciones

- AC-008 y AC-009 son directamente los requisitos RF-06.9 y RF-V.4 del SRS, derivados del fallo A-6 de la primera implementación (servidor conectado sin herramientas). Son los criterios de verificabilidad de mayor prioridad en esta historia.
