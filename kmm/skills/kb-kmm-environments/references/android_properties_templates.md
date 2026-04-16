# Android Properties — Templates

Ficheros `.properties` en la **raíz del proyecto** (no dentro de ningún módulo), uno por variante brand×env.

Solo incluir aquí valores que Gradle **no puede derivar** de brand/env (URLs, API keys, tokens). No incluir `BRAND` ni `IS_PRE` — esos los calcula el bloque `buildConfig` dinámicamente.

---

## § {brand1}-{env1}.properties

```properties
APP_BASE_URL = https://{env1-subdomain}.{brand1-domain}
```

## § {brand1}-{env2}.properties

```properties
APP_BASE_URL = https://{brand1-domain}
```

## § {brand2}-{env1}.properties

```properties
APP_BASE_URL = https://{env1-subdomain}.{brand2-domain}
```

## § {brand2}-{env2}.properties

```properties
APP_BASE_URL = https://{brand2-domain}
```

Repetir el patrón para cada combinación brand×env adicional.

---

## § Campos extra

Si hay variables adicionales (API keys, feature flags, analytics keys), añadirlas en todos los ficheros:

```properties
APP_BASE_URL      = https://...
ANALYTICS_KEY     = {key-value}
FEATURE_FLAG_X    = true
```

Consultar Regla 8 del kb- para decidir qué valores son seguros de commitear y cuáles deben ir en `.gitignore` + CI secrets.
