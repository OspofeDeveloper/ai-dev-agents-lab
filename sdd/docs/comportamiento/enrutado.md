# Enrutado por lenguaje natural — `EC-ROUTE`

!!! warning "Área en construcción"
    Casos del paso de argumentos en la cadena orquestador → skill → agente
    (ROADMAP 11.1). Cobertura prevista: el usuario **habla**, nunca teclea `/wf-*`,
    y el orquestador acierta la skill y construye los args (rutas resueltas, flags
    como `--features F-001,F-002`, modos `analyze|apply|generate`); los argumentos
    sobreviven el salto wf→wf y wf→subagente; los gates `PreToolUse` reciben los args
    en el formato que esperan aunque los construya un agente y no un humano. Es la
    parte más dependiente del LLM: se valida sobre todo a mano (liga con el
    playbook 11.6).
