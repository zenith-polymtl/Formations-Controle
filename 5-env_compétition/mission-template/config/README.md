# config/ : ce qui change sans toucher au code

| Fichier | Change quand | Chargé par |
|---|---|---|
| `<mission>.yaml` | On règle la mission : gains, PWM des servos, mapping des interrupteurs de la manette, seuils, chemins de sauvegarde | Le launch de la mission, qui le passe aux nœuds |
| `sites/<site>.yaml` | On change de terrain : coordonnées, altitudes | Le launch, avec `site:=<nom>` (par défaut `sim`) |
| `drones/<drone>.json5` | On vise un autre drone depuis le sol : adresses Zenoh | `compose/zenoh-ground.yml`, avec `DRONE=<nom>` |
| `mavros.yaml` | Rarement : paramètres mavros | `compose/mavros.yml` |
| `zenoh-air.json5` | Rarement : ce qui a le droit de traverser la radio | `compose/zenoh-air.yml` |
| `zed.yaml` | Réglages de la caméra ZED | `compose/zed.yml` |

Règle : une valeur qui change entre deux drones, deux terrains ou deux essais n'est jamais écrite dans un nœud ni dans un launch. Elle est ici.

Exemple de `config/<mission>.yaml`, à copier pour une nouvelle mission :

```yaml
mission:
  name: water
  rc:                  # interrupteurs de la manette, numéro de canal (0 = premier canal)
    go: 7
    abort: 8
  servo:
    channel: 9
    pwm_open: 1900
    pwm_closed: 1100
  approach:
    speed_mps: 2.0
    tolerance_m: 1.5
  save_dir: /aeac/bags  # dossier ignoré par git
```
