---
name: wf-spec-retire
description: "Gestiona la vigencia de una feature: la da de baja cuando el producto deja de contemplarla —auditando quien depende de ella y sellando el spec como RETIRADO con su traza— y la reactiva si se revierte."
when_to_use: "Activa en frases como 'esta feature ya no va', 'damos de baja X', 'quitamos esa capacidad del producto', y tambien en las inversas: 'recupera la feature X', 'vuelve a activar X', 'al final si la hacemos'. Retirar exige que el cambio este formalizado antes en el PRD. No activa para posponer una feature a una fase futura —eso no la retira, sigue comprometida—, ni para eliminar una HU o un CA sueltos, que es wf-spec-delta."
argument-hint: "<feature_spec.md> --change CR-XXX [--reason 'texto'] | reactivate <feature_spec.md>"
effort: medium
allowed-tools: [Bash, Agent, AskUserQuestion]
user-invocable: true
---

# Workflow: SPEC-RETIRE

Tu rol es de **orquestador puro**: compruebas la traza del cambio, delegas el diagnóstico de impacto al agente `sdd-spec-auditor`, presentas ese impacto en un gate y dejas que el sellador determinista escriba la baja. **No escribes el spec** ni decides tú si la feature se retira.

**Dos modos, uno por dirección.** Sin modo explícito, o con `retire`, das de baja (Pasos 1-7). Con **`reactivate <spec.md>`**, deshaces una baja (Paso R). Las dos direcciones viven aquí porque la responsabilidad es la misma —**la vigencia de la feature**— y porque una reversión que no tiene vía sancionada no es reversible: es una promesa. Hasta [[D-074]] el modo existía en el sellador y no lo alcanzaba nadie.

Este workflow corre en el **hilo principal** por la misma razón que `wf-spec-validate` ([[D-065]]) y `wf-spec-delta` ([[D-073]]): dar de baja una feature es una **decisión de producto con coste irreversible** —hay specs, planes y tasks construidos encima—, y una decisión así se presenta a quien puede tomarla. Ningún fork retira nada: los que detectan el caso (`wf-prd-sync-impact`, `wf-spec-sync-from-prd`) lo **reportan** y terminan aquí.

**Regla de oro:** no hagas `Read` ni `cat` del spec. Lo que necesitas sale del informe de tu delegado y de los scripts ([[D-031]]/[[D-060]]). El único contacto directo con el fichero es un `grep` de una línea de cabecera: extracción determinista y acotada ([[D-048]]), no lectura del artefacto.

---

## Paso 1: Parsear argumentos y exigir la traza

De `$ARGUMENTS` extrae **el modo** (`reactivate` si aparece como primer token; en cualquier otro caso, dar de baja), el path del spec, `--change CR-XXX` y el `--reason` opcional.

**Si el modo es `reactivate`, salta directamente al Paso R**: no aplica nada de lo que sigue —ni la traza, ni el diagnóstico, ni el gate—, porque deshacer una baja no destruye nada.

Sin path:
> "Necesito saber qué feature quieres dar de baja, o cuál quieres recuperar."

**Sin `--change`**, o con un `CR-XXX` cuyo directorio no existe: **detente**. Retirar una capacidad sin el cambio de producto detrás es cancelar producto sin registro, y quien lo vea dentro de tres meses no sabrá quién lo decidió ni por qué.

```bash
!test -d "<dir_del_proyecto>/changes/<CR-XXX>" && echo "CR_EXISTE" || echo "CR_NO_EXISTE"
```

Si no existe, remite en lenguaje natural a formalizar antes la decisión en el PRD —sin nombrar el workflow— y termina. **No propongas continuar igualmente**: aquí no hay override, porque no es un gate de seguridad que se pueda asumir, es la evidencia de que la decisión existe.

---

## Paso 2: Verificar el spec, mecánicamente

```bash
!test -f "<path>" && echo "EXISTE" || echo "NO_EXISTE"
!grep -m1 -E '^\s*>?\s*\**Estado' "<path>"
```

- No existe → informa con la ruta exacta y detén.
- Ya dice `RETIRADO` → informa de que esa feature ya estaba dada de baja, con la traza que ya lleva, y termina. La operación es **idempotente**: no vuelvas a preguntar ni a sellar.

---

## Paso 3: Delegar el diagnóstico de impacto (tool `Agent`, y esperar)

Lo que hay que saber antes de retirar no es si el spec está bien escrito: es **quién se queda colgando**. Delega con la tool `Agent` ([[D-043]]), `subagent_type: "sdd-spec-auditor"` y **`run_in_background: false`**:

  prompt: "Diagnostica el impacto de dar de baja la feature cuyo spec es <path>. NO escribas ningún archivo y NO modifiques nada: devuélveme el diagnóstico. Reporta: (1) qué shared models declara esta feature como owner y qué otras features los referencian —esos specs se quedan sin dueño—; (2) qué otras features la declaran como dependencia en su README o en el índice de features; (3) conflictos abiertos donde aparezca; (4) qué artefactos derivados existen ya en disco para esta feature (plan, tasks, plan de QA, informe de QA, release, bugs), con su path. Termina con una línea que diga si la baja deja algo huérfano o no."

**Has esperado cuando el diagnóstico está en tu contexto como resultado de tu propia llamada** ([[D-047]]). Si no lo tienes, **paras y lo dices**: no reconstruyes el impacto leyendo artefactos por tu cuenta, y no presentas el gate a ciegas — un gate sin el impacto delante es la firma de algo que no se ha visto.

---

## Paso 4 (gate, hilo principal): Confirmar la baja

Presenta el diagnóstico y **pregunta con `AskUserQuestion`**, siempre, con el impacto delante:

- **Retirar la feature** — nombrando en la opción lo que se pierde: los artefactos derivados que quedan sin origen vigente y las features que se quedan sin el shared model que esta poseía.
- **No retirarla** — no se escribe nada.

**Dos cosas que la opción de retirar tiene que decir, cuando apliquen:**

- **Si la feature tiene `_release.md`**, dilo explícitamente: el código está **entregado y en producción**, y dar de baja el spec **no lo retira**. Retirar aquí documenta que el producto ya no contempla la capacidad; quitarla del sistema es trabajo aparte que nadie está aprobando en este gate.
- **Si deja shared models huérfanos**, nómbralos: otra feature los referencia y su spec pasará a apuntar a un dueño retirado.

No hay flag de override y no debe haberlo ([[D-026]]): los `--allow-*` existen para lo que **no puede preguntar**. Este workflow puede, así que el gate **es** el mecanismo. Si el usuario no elige, no se retira nada.

---

## Paso 5: Estampar la baja (deterministamente)

El estado lo escribe **solo** el sellador. Nunca edites la línea `Estado:` a mano.

```bash
!python3 .sdd/scripts/sdd-seal.py spec "<path>" --retire --change <CR-XXX> --reason "<razón>"
```

Si la feature tiene plan, **degrádalo en la misma pasada**:

```bash
!python3 .sdd/scripts/sdd-seal.py plan "<path_del_plan>" --unseal
```

> Un plan `VALIDADO` de una feature cancelada es exactamente lo que no puede quedar en pie: es la
> línea que leen `wf-prepare-tasks` y `wf-task-run` para dejar pasar trabajo. El gate mecánico ya
> deniega los dos —resuelve el `Spec origen` y ve la baja—, pero dejar el plan afirmando que está
> validado es sostener por escrito algo que dejó de ser verdad.

Y regenera el índice, que es de donde sale el estado `RETIRADA`:

```bash
!python3 .sdd/scripts/sdd-features-index.py "<raíz_de_artefactos_spec>"
```

**Script ausente** → no escribas nada a mano: informa de que falta y que hay que reponer los scripts reinstalando el ecosistema.

---

## Paso 6: Verificar lo que ha quedado

```bash
!grep -m1 -E '^\s*>?\s*\**Estado' "<path>"
!grep -m1 "<F-00X>" "<raíz>/<basename>_features.md"
```

Si el spec no dice `RETIRADO` o el índice no dice `RETIRADA`, **dilo**: no des por hecha una baja que no ves escrita.

---

## Paso R (modo `reactivate`): Deshacer una baja

La dirección inversa es **la segura** —nada se destruye: el spec vuelve a `BORRADOR`, que es donde estaría un spec sin validar— así que no lleva gate propio ni exige un `CR-XXX` nuevo. Lo que sí lleva es **decir la verdad de lo que queda**.

1. Verifica que el spec existe y que está dado de baja:
   ```bash
   !test -f "<path>" && grep -m1 -E '^\s*>?\s*\**Estado' "<path>"
   ```
   Si no dice `RETIRADO` → informa de que esa feature ya está vigente y termina. No toques nada.

2. Deshaz la baja y regenera el índice:
   ```bash
   !python3 .sdd/scripts/sdd-seal.py spec "<path>" --unretire
   !python3 .sdd/scripts/sdd-features-index.py "<raíz_de_artefactos_spec>"
   ```
   El script devuelve el spec a `BORRADOR` y **retira la línea `Retirada:`**: una traza que afirma una baja que ya no existe la lee tanto el índice como una persona.

3. **Informa de lo que NO se ha restaurado**, que es lo que importa:
   - El spec vuelve a `BORRADOR`, **no a validado**: hay que volver a validarlo antes de planificar sobre él. La reactivación no reabre un sello, lo deja pendiente.
   - Si la feature tenía plan, ese plan sigue en `BORRADOR` desde la baja: también hay que revalidarlo.
   - **Y el aviso de fondo**: si el PRD sigue sin contemplar esa capacidad, el spec que acabas de reactivar contradice al PRD vigente. Dilo — reactivar un spec no reactiva la decisión de producto, y esa se formaliza en el PRD.

---

## Paso 7: Informar

En lenguaje natural, sin nombrar workflows:

- qué feature se ha dado de baja y con qué cambio de producto;
- que su **Feature ID se conserva y no se reutiliza** (`kb-traceability-rules` Regla 12): la siguiente feature toma el siguiente número libre, no el hueco;
- que a partir de ahora no se puede planificar sobre ella, ni generarle tareas, ni ejecutarlas;
- **qué queda en pie**: si había release, que el código sigue entregado y retirarlo es otra conversación; si deja shared models huérfanos, qué features hay que revisar;
- y que, si la decisión cambia, **puedes pedirme que la recuperes**: volvería a `BORRADOR` y habría que validarla de nuevo. Descríbeselo como acción, no como comando.
