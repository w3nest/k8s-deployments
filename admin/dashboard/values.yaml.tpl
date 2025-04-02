dashboard:
  metricsScraper:
    enabled: true
  serviceMonitor:
    enabled: true
  app:
    ingress:
      enabled: true
      hosts:
        - ${TOOLING_DOMAIN}
      ingressClassName: nginx
      path: /dashboard
      issuer:
        name: letsencrypt-youwol
        scope: cluster
      tls:
        secretName: tooling-tls
