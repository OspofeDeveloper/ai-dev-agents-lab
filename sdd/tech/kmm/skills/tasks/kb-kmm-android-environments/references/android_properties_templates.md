# Android Properties — Templates

Estos ejemplos muestran ficheros `.properties` por variante. Solo deben contener valores declarativos que Android no pueda derivar automáticamente.

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

Si hay variables adicionales, añadirlas en todos los ficheros relevantes:

```properties
APP_BASE_URL   = https://...
ANALYTICS_KEY  = {key-value}
FEATURE_FLAG_X = true
```
