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
