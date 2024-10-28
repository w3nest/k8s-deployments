ARG kc_version=26.0.1
FROM quay.io/keycloak/keycloak:$kc_version AS builder

# See https://www.keycloak.org/server/all-config for build-time configuration
ENV KC_CACHE_STACK=kubernetes
ENV KC_DB=postgres
ENV KC_FEATURES="token-exchange,admin-fine-grained-authz,recovery-codes"
ENV KC_HTTP_RELATIVE_PATH="/auth"
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

WORKDIR /opt/keycloak
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:$kc_version
COPY --from=builder /opt/keycloak /opt/keycloak

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
