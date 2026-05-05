# Android Properties — Templates

Per-variant `.properties` files. Only declarative values Android cannot derive automatically.

## Per-variant files (one per brand×env combination)

```properties
# {brand1}-{env1}.properties
APP_BASE_URL = https://{env1-subdomain}.{brand1-domain}

# {brand1}-{env2}.properties
APP_BASE_URL = https://{brand1-domain}

# {brand2}-{env1}.properties
APP_BASE_URL = https://{env1-subdomain}.{brand2-domain}

# {brand2}-{env2}.properties
APP_BASE_URL = https://{brand2-domain}
```

Repeat the pattern for each additional brand×env combination.

## Extra fields

Add to all relevant files:

```properties
APP_BASE_URL   = https://...
ANALYTICS_KEY  = {key-value}
FEATURE_FLAG_X = true
```