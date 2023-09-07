# Helm chart for Keycloak Operator

Adapted from 
[Installing by using kubectl without Operator Lifecycle Manager](https://www.keycloak.org/operator/installation#_installing_by_using_kubectl_without_operator_lifecycle_manager)

## [`keycloak-operator-cluster-resources` (in ./cluster-resources/)](./cluster-resources)

Chart for resources common to all insances of Keycloak Operator (CRDs & ClusterRoles). Since these resources are not 
namespace scoped, only one release of this chart can be installed.

_NB: Helm has special handling of CRDs,
see [offictial documentation](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/)._


## [`keycloak-operator` (in ./operator/)](./operator)

Chart for installing one operator. All objects for a release of this chart are both namespace scoped and uniquely 
named from the release name.

A single release of `keycloak-operator-cluster-resources` should be deployed alongside 
any number of releases of this chart.

_NB: a Keycloak Operator deployment only watch its namespace._
