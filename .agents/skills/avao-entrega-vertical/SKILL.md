---
name: avao-entrega-vertical
description: Implementar con el usuario una HU o funcionalidad pequeña y utilizable de AVAO mediante AI pair programming y un vertical slice. Usar al construir código; no usar para crear o repriorizar backlog.
---

# Entrega vertical con usuario Navigator e IA Driver

1. Toma una HU refinada o resultado acotado por el usuario. Lee solo el contexto técnico y de dominio pertinente. Resume comportamiento observable, límites, dudas que bloquean y qué comprobará el usuario. El usuario decide valor, reglas de negocio, alcance y aceptación; la IA propone decisiones técnicas reversibles y explica riesgos.
2. Acuerda una unidad pequeña **usable desde la web** que conecte lo necesario de interfaz, backend y persistencia. Incluye base de datos cuando guardar o reabrir información sea parte de la aceptación. No construyas una capa completa por anticipado ni obligues a que toda unidad toque las tres capas. Mantén separada la lógica de medidas/cortes de la presentación para comprobarla.
3. Implementa el mínimo comportamiento correcto. Usa ejemplos y valores confirmados para cálculos; comprueba entradas y estados capaces de producir medidas o cortes falsos, pérdida de datos o exposición de datos. «Mínimo» no significa omitir verificaciones esenciales. Prefiere comprobaciones observables; automatiza las que protejan cálculos, persistencia o regresiones reales y revisa manualmente interacciones visuales cuando corresponda. No exijas TDD ni cantidad fija de pruebas, criterios, líneas o archivos.
4. Informa al usuario cuando surja una decisión material de negocio, alcance, arquitectura o refactorización significativa. Pregunta si una regla de dominio impide continuar; no la sustituyas por una suposición. Resuelve detalles técnicos pequeños y reversibles dentro del alcance. Propón abstracciones o refactorizaciones ante duplicación, dolor concreto o requisito nuevo; preserva comportamiento al hacerlas.
5. Muestra la funcionalidad integrada, evidencia de comprobaciones y límites restantes. Contrasta resultado con criterios de aceptación y deja al usuario validar el flujo real. No cierres HU solo porque se completaron subtareas o pasó una prueba. Una nueva idea pasa al backlog; no la añadas silenciosamente.

Para Kanban y criterios actuales consulta `docs/workflow/GuiaBacklogKanban.md`; para producto `docs/product/Backlog.md` y el documento pertinente en `docs/domain/`. Esta skill adapta conceptos útiles de [hola-ai](https://github.com/nschurmann/hola-ai) —slicing, alcance explícito y humano al mando— a AVAO; no adopta límites rígidos de tamaño ni pausas tras cada prueba.
