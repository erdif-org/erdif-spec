# UtilityNetwork

## Description

`UtilityNetwork` states how the property is connected to one utility
network. The network (water, sewage, electricity, heating, cooling, gas,
telecom, internet) and the means of connection (public mains, private well,
septic tank, ...) are two independent axes, so they are expressed by two
properties with two codelists.

Which connections belong to which network is defined machine-readably by
`appliesTo` in the [`UtilityConnection`](../codelists/utility-connection.md)
codelist. A connection may belong to several networks: a reversible heat
pump or air conditioning unit both heats and cools. Such a device is stated
once per network, so that a consumer can ask for heating and for cooling
separately.

The network is therefore not derivable from the connection, which is why
both properties are always given.

## Properties

--8<-- "_partials/terms-utility-network.md"

## Validation rules

--8<-- "_partials/rules-utility-network.md"

## Example

```json
"utilityNetworks": [
  { "@type": "erdif:UtilityNetwork", "network": "Water", "connection": "PublicMains" },
  { "@type": "erdif:UtilityNetwork", "network": "Heating", "connection": "HeatPump" },
  { "@type": "erdif:UtilityNetwork", "network": "Cooling", "connection": "HeatPump" },
  { "@type": "erdif:UtilityNetwork", "network": "Internet", "connection": "FiberOptic" }
]
```
