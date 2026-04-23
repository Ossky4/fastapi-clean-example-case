# Case Project: ruta multicapa con alternativas competitivas (PR1)

## Propósito del caso
Delimitar una hipótesis de trabajo, conservadora y revisable, para un cleanup pequeño en una ruta interna con varias capas (`inbound -> core -> outbound`) sin implementar cambios técnicos todavía.

## Hipótesis del experimento
En este repositorio, es posible mantener disciplina de PR pequeña y validación clara al trabajar sobre una ruta interna profunda, incluso cuando hay 2–3 alternativas de cleanup realmente competitivas en el mismo hotspot.

## Capas o módulos bajo observación
- `src/app/inbound/http/users/*` (entrada HTTP y mapeo de errores).
- `src/app/core/commands/*` (casos de uso y reglas de negocio).
- `src/app/outbound/adapters/*` (adaptadores de persistencia y puertos).
- `tests/integration/with_infra/users/*` y `tests/unit/core/*` (cobertura existente relacionada).

## Ruta interna bajo observación (hipótesis de trabajo)
Ruta candidata: **Create User**.

Recorrido visible: `inbound/http/users/create_user.py` -> `core/commands/create_user.py` -> puertos de comandos (`user_tx_storage`, `flusher`, `transaction_manager`, `utc_timer`) -> adaptadores SQLA (`sqla_user_tx_storage.py` y relacionados), con validación observable en tests de integración de `users`.

> Nota: esta ruta se toma como hipótesis inicial por su trazabilidad visible y cobertura existente; no se declara como defecto.

## Alternativas plausibles y competitivas de cleanup pequeño
1. **Ajuste mínimo de consistencia en handlers HTTP de `users`**
   - Objetivo: reducir pequeñas divergencias de estilo/ensamblado entre handlers (p. ej., creación de request DTO, forma de declarar `status`, estructura homogénea del endpoint), sin cambiar comportamiento.

2. **Ajuste mínimo de consistencia en comandos del hotspot (`create/grant/revoke/activate/deactivate/set_password`)**
   - Objetivo: homogeneizar detalles locales de construcción de request/response y secuencia de pasos internos cuando ya son semánticamente equivalentes.

3. **Ajuste mínimo de borde puerto-adaptador en la ruta `create_user`**
   - Objetivo: limpieza focalizada en un punto de frontera (nombres, contrato local o micro-duplicación), manteniendo intacta la semántica y los contratos externos.

## Criterio para elegir entre alternativas
Elegir primero la opción que cumpla mejor, en este orden:
1. menor superficie de cambio;
2. menor riesgo de regresión funcional;
3. validación más directa con tests ya existentes;
4. mayor claridad del diff para revisión rápida.

## Fuera de alcance
- Rediseño arquitectónico amplio o transversal.
- Cambios de comportamiento funcional, reglas de negocio o contratos de API.
- Reorganización masiva de módulos.

## Secuencia prevista de PRs
- **PR1 (esta):** delimitación documental de hipótesis y alternativas.
- **PR2 (técnica, una sola intención):** ejecutar solo una alternativa elegida con cambio mínimo.
- **PR3 (opcional, técnica):** segunda mejora pequeña únicamente si queda evidencia clara y acotada tras PR2.

---

## Retrospectiva breve de fastapi-clean-example-case

### Propósito del caso
Evaluar si Codex puede mantener criterio conservador en una ruta interna profunda con varias capas (`inbound -> core -> outbound`), enfrentando alternativas pequeñas y competitivas dentro del mismo hotspot, sin perder disciplina de PR pequeña ni claridad de validación.

### Resumen del ciclo

#### PR1 — Delimitación del caso
Se definió como ruta bajo observación **Create User**:

`inbound/http/users/create_user.py` → `core/commands/create_user.py` → puertos/adaptadores de persistencia relacionados.

También se fijaron varias alternativas pequeñas y competitivas de cleanup dentro del mismo hotspot.

#### PR2 — Ajuste técnico mínimo
Se eligió una limpieza mínima en el borde `core ↔ outbound`: eliminar un `try/except UsernameAlreadyExistsError: raise` redundante en `CreateUser.execute`, dejando más explícito que la traducción del error de persistencia pertenece al borde adaptador/flusher.

#### PR3 — Blindaje pequeño
Se añadió un test unitario focalizado para fijar que, si `Flusher.flush()` emite `UsernameAlreadyExistsError`, `CreateUser.execute` lo propaga y no alcanza `commit` en ese camino.

#### Evaluación de PR4
Se evaluó si existía una PR4 mínima para hacer ejecutable el test de PR3 en este entorno.

La conclusión fue negativa:
no existe una PR4 mínima real para Python 3.10 porque la incompatibilidad ya no era local ni superficial, sino estructural respecto al runtime esperado por el proyecto.

### Qué funcionó bien
- La ruta candidata se eligió tras inspección real de estructura y tests visibles.
- PR2 mantuvo un alcance claramente pequeño, reversible y de una sola intención.
- PR3 fijó bien la decisión tomada en PR2 con un test unitario específico.
- La evaluación de PR4 distinguió correctamente entre fricción superficial de entorno e incompatibilidad estructural de versión.

### Qué señal aportó este caso
Este caso añade una señal útil sobre una situación más exigente que las anteriores:
- existe una ruta interna profunda y trazable,
- había alternativas pequeñas realmente competitivas en el mismo hotspot,
- y Codex pudo ejecutar una decisión conservadora sin derivar a refactor amplio.

También aportó una señal metodológica importante:
cuando el bloqueo final proviene de un runtime fuera del contrato declarado del proyecto, la decisión correcta no es introducir workarounds locales, sino cerrar el caso con trazabilidad.

### Límite principal observado
La validación dinámica final quedó bloqueada por incompatibilidad estructural de entorno:
- falta de `src` en `sys.path` en invocaciones básicas,
- uso de `StrEnum` no compatible con Python 3.10,
- y sintaxis moderna del lenguaje fuera del rango soportado por ese runtime.

Además, el propio proyecto declara un runtime objetivo superior, por lo que perseguir compatibilidad local en 3.10 habría abierto un frente fuera del perímetro del experimento.

### Conclusión
`fastapi-clean-example-case` aporta señal útil sobre:
- trabajo conservador en una ruta profunda,
- competencia real entre alternativas pequeñas dentro del mismo hotspot,
- y buen criterio para no expandir alcance cuando el bloqueo ya pertenece al entorno y no al hotspot trabajado.

### Recomendación
Dar este caso por cerrado.

Cualquier continuación debería hacerse solo en un entorno alineado con la versión de Python objetivo del proyecto, y como hipótesis nueva explícita, no como continuación inercial de este mismo caso.
