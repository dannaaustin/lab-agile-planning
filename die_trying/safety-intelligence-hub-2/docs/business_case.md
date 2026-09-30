# Business case y justificación de decisiones

## El problema de negocio

Un H&S Manager de una empresa multi-site no necesita "más datos" — recibe informes de
8+ sites cada mes y no tiene forma rápida de saber dónde intervenir primero. El coste
real no es la falta de datos, es la falta de **priorización accionable**.

## Por qué esta fórmula de risk score (y no otra)

```
risk_score =
    30% TRIR normalizado          (severidad real ya ocurrida — lagging)
  + 20% % acciones overdue        (ejecución del programa preventivo)
  + 20% hallazgos major de auditoría (cumplimiento normativo / ISO 45001)
  + 15% brecha de formación       (preparación de la plantilla)
  + 15% (100 - near-miss rate normalizado)  (cultura de reporte, invertido)
```

**Por qué el near-miss rate resta en vez de sumar riesgo**: es la decisión de diseño
más importante del proyecto y la que hay que saber defender. Un site con reporte de
near-miss muy bajo no es un site seguro — normalmente es un site donde la gente no
reporta por miedo, desconocimiento o falta de cultura preventiva, lo cual es en sí un
riesgo oculto. Por eso el modelo premia (resta al risk score) el reporte alto de
near-miss, en vez of tratarlo como "más eventos = más peligro". Esto es coherente con
cómo el sector trata los leading indicators (ver referencias del propio README del
proyecto).

**Por qué pesos fijos y no aprendidos (ML)**: con ~2 años de histórico por site
(dataset pequeño por diseño, para que sea real de gestionar manualmente) cualquier
modelo entrenado daría pesos inestables y no defendibles. Un HR/H&S Director puede
cuestionar "por qué 30% y no 25%" — y con una fórmula explícita se puede responder con
lógica de negocio, no con "lo dijo el modelo".

## Qué NO se demuestra con este proyecto (honestidad de scope)

- No es un sistema en producción ni conectado a datos reales de ninguna empresa.
- El módulo de detección de EPI (`ppe_module/`) es una extensión documentada, no
  entrenada end-to-end dentro de este repo — requiere un dataset público (Roboflow/
  Kaggle) y GPU que no forman parte del alcance base del proyecto.
- Los pesos del risk score son un punto de partida razonado, no una verdad estadística
  validada con datos reales de accidentabilidad.

Esto se dice así, explícito, porque en entrevista es mejor defender un scope claro y
honesto que sobrevender el proyecto y que se caiga con la primera pregunta técnica.
