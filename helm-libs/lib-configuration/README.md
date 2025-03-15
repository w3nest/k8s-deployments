# lib-configuration

Provide templates for managing ConfigMap and Secret, including managing annotations
```w3nest/force-update-marker``` and ```w3nest/checksum```.

To start using it, add it to your Helm chart dependencies :

```yaml
# file ./Chart.yaml
apiVersion: v2
name: mychart
version: 0.1.0
appVersion: 0.0.1

dependencies:
  - name: lib-configuration
    version: 0.0.1
    repository: file://path/to/lib-configuration

```

Then build your Helm chart dependencies :

```shell
helm dependencies build .
```

The recommended way for templating a Secret or a ConfigMap using this lib is to use one file per object, for instance :

```gotemplate
{{/* file ./templates/credentials-secret.yaml */}}
{{- $keys := list "username" "password"}}
{{- $args := dict "root" . "name" "credentials" "keys" $keys }}
{{- include "lib-configuration.secret" $args }}
```

## ```lib-configuration.secret```

Template a Kubernetes Secret if it does not exists, or use deployed Secret for its data.

This template take a dictionary as its argument, with the following keys:

* ```root``` : the root object, for accessing ```.Release```, ```.Values```, etc. in subcharts
* ```name``` : the name of the Secret to template
* ```keys``` : the keys of the data part of the Secret

### Values generation

For each key ```my-key``` in a secret ```my-secret```, the following logic is applied to determine its associated
value :

1. If it exists a value ```.Values.overrideSecrets.my-secret.my-key```, use it
2. Else if there is an secret named ```my-secret``` in release namespace
   and that object has a key ```my-key```, use its value.
3. Else generate an alphanumeric string of 32 characters and use it.

### Annotations

The following annotations are managed :

* ```w3nest/force-update-marker``` : see relevant section below.
* ```w3nest/checksum``` : checksum (SHA256) the data of the final object.

### Example

Given the currently deployed Secret with one entry ```existingKey``` containing the value '__foo__' (some metadata
ignored for
sake of brevity) :

```yaml
# In cluster (some metadata ignored)
apiVersion: v1
kind: Secret
type: Opaque
data:
  existingKey: Zm9v      # string 'foo' encoded in base64
metadata:
  annotations:
    meta.helm.sh/release-name: release
    meta.helm.sh/release-namespace: ns
    w3nest/checksum: 8b05a8dcb13b8e3a54edb998e009c3dc4aa2f0a3fd8b907fdd76542df5a857e8
    w3nest/force-update-marker: 4e3762d8-2e9b-4c39-b4d8-0cdee4595f55
  name: example
  namespace: ns
```

Given the following template :

```gotemplate
{{/* file ./templates/example-secret.tpl */}}
{{- $keys := list "existingKey" "generatedKey" "valuedKey" }}
{{- $args := dict "root" . "name" "example" "keys" $keys }}
{{- include "lib-configuration.secret" $args }}
```

Given the following Helm command :

```shell
helm upgrade --namespace ns \
  release . \
  --set overrideSecrets.example.valuedKey=bar
```

The following Kubernetes Secret will be templated (some metadata ignored for sake of brevity):

```yaml
# Generated manifest
apiVersion: v1
kind: Secret
type: Opaque
data:
  existingKey: Zm9v                                          # string 'foo' encoded in base64
  valuedKey: YmFy                                            # string 'bar' encoded in base64
  generatedKey: Q2h5TlJmdUdZR2VHdmJCaHd4dFhiUDY1QUVrbmRVb3o= # alphanumeric string of 32 characters encoded in base64 
metadata:
  annotations:
    meta.helm.sh/release-name: release
    meta.helm.sh/release-namespace: ns
    w3nest/checksum: 553c015d77c1eabf1143f59e68e9f149a082fd7d2a41851236b57fa979354325
    w3nest/force-update-marker: 4e3762d8-2e9b-4c39-b4d8-0cdee4595f55 # marker unchanged
  name: example
  namespace: ns
```

## ```lib-configuration.config-map```

Template a Kubernetes ConfigMap from a Go dictionary, or use deployed ConfigMap.

This template take a dictionary as its argument, with the following keys:

* ```root``` : the root object, for accessing ```.Release```, ```.Values```, etc. in subcharts
* ```name``` : the name of the ConfigMap to template
* ```values``` : a dictionary of values for the data part of the ConfigMap

### Values

The simplest way to obtain a dictionary for the values is to use an external YAML file :

```gotemplate
{{ $values := .Files.get "config/example.yaml" }}
```

WARNING : values in this file MUST be string, not numbers. Numbers MUST be quoted.

### Annotations

The following annotations are managed :

* ```w3nest/force-update-marker``` : see relevant [README.md](../lib-utils/README.md)
* ```w3nest/checksum``` : checksum (SHA256) the data of the final object.


### Example

Given the file :

```yaml
# file ./config/example.yaml
foo: "toto"
bar: "42"
```

Given the following template :

```gotemplate
{{/* file ./templates/example-configmap.tpl */}}
{{- $values := .Files.get "./config/example.yaml" }}
{{- $args := dict "root" . "name" "example" "values" $values }}
{{- include "lib-configuration.config-map" $args }}
```

Given the following Helm command :

```shell
helm upgrade --namespace ns \
  release .
```

The following Kubernetes ConfigMap will be templated (some metadata ignored for sake of brevity):

```yaml
# Generated manifest
apiVersion: v1
kind: ConfigMap
data:
   foo: "toto"
   bar: "42"
metadata:
   annotations:
      meta.helm.sh/release-name: release
      meta.helm.sh/release-namespace: ns
      w3nest/checksum: 553c015d77c1eabf1143f59e68e9f149a082fd7d2a41851236b57fa979354325
      w3nest/force-update-marker: 4e3762d8-2e9b-4c39-b4d8-0cdee4595f55
   name: example
   namespace: ns
```

## ```lib-configuration.duplicate-config-map```

Duplicating existing Kubernetes ConfigMaps across namespaces.

This template take a dictionary as its argument, with the following keys:

* ```root``` : the root object, for accessing ```.Release```, ```.Values```, etc. in subcharts
* ```name``` : the name of the original and templated ConfigMaps
* ```namespace``` : the namespace of the original ConfigMap

### Annotations

In addition of the original ConfigMAp annotations, the templated ConfigMap will have an additional annotation :

* ```youwol.com/duplicate-of```: will have the value ```configmap/<ns>.<name>```, with <ns> the namespace of the 
  original ConfigMAp 

## ```lib-configuration.duplicate-secret```

Duplicating existing Kubernetes Secrets across namespaces.

This template take a dictionary as its argument, with the following keys:

* ```root``` : the root object, for accessing ```.Release```, ```.Values```, etc. in subcharts
* ```name``` : the name of the original and templated Secrets
* ```namespace``` : the namespace of the original ConfigMap

### Annotations

In addition of the original Secret annotations, the templated Secret will have an additional annotation :

* ```youwol.com/duplicate-of```: will have the value ```secret/<ns>.<name>```, with <ns> the namespace of the original Secret


## ```lib-configuration.force-update```

Manage annotation ```w3nest/force-update-marker```, which allow to force the update of an object by modifying the
marker.
Though currently the annotation’s value is an UUIDv4, it has no meaning by itself.

This template take a dictionary as its argument, with the following keys:

* ```root``` : the root object, for accessing ```.Release```, ```.Values```, etc. in subcharts
* ```kind``` : the kind of the object templated
* ```name``` : the name of the object templated

### Policy

Three policies can be used :

* ```install```: Default policy. Use value from deployed object if it bears the annotation or create the annotation.
* ```force```: Force generation of a new value for the annotation, even if the deployed object bears the annotation.
* ```keep ```: Use current marker if the object exists and bears the annotation, or do nothing.

The policy is specified :

* By default it will be ```install```
* For all objects in the release, using ```.Values.forceUpdatePolicy```.
* For each object, using ```.Values.forceUpdatePolicies.<name>``` where ```<name>``` is the object name

NB: Do note that on subsequent upgrade, a given release will keep policy previously specified.

### Examples

Here we want to ignore this mechanism for almost all objects in the release but force update of object ```updatedObject```.
Only ```updatedObject``` will bear a new value for the annotation, regardless its current metadata. All other deployed
objects will be untouched, should they bear the annotation or not.

```gotemplate
{{/* Far sake of brevity tow objects: 'updatedObject' will be updated, 'untouchedObject' will not */}}
---
{{- $name := "updatedObject" }}
  {{- $forceUpdateArgs := dict "root" . "name" $name "kind" "ConfigMap" }}
apiVersion: v1
kind: ConfigMap

metadata:
  name: {{ $name }}
  namespace: {{ .Release.Namespace }}
  annotations:
    {{- include "lib-configuration.force-update" $forceUpdateArgs | indent 4 }}

data:
  foo: "toto"
---
{{- $name := "untouchedObject" }}
  {{- $forceUpdateArgs := dict "root" . "name" $name "kind" "ConfigMap" }}
apiVersion: v1
kind: ConfigMap

metadata:
  name: {{ $name }}
  namespace: {{ .Release.Namespace }}
  annotations:
    {{- include "lib-configuration.force-update" $forceUpdateArgs | indent 4 }}

data:
  bar: "42"
```



#### Using ```values.yaml``` file

```values.yaml``` file :

```yaml
# file ./values.yaml
forceUpdatePolicy: "keep"
forceUpdatePolicies:
  updatedObject: force
```

Command line :

```shell
helm upgrade release .
```

#### Using Command line arguments

```shell
helm upgrade release . --set forceUpdatePolicy=keep --set forceUpdatePolicies.updatedObject=force
```

#### Using an external file

```/tmp/release.yaml``` file :

```yaml
# file /tmp/release.yaml
forceUpdatePolicy: "keep"
forceUpdatePolicies:
  updatedObject: force
```

Command line :

```shell
helm upgrade release . -f /tmp/release.yaml
```
