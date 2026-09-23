# vision_ws : le workspace du conteneur vision (Jetson, GPU)

Construit dans le conteneur `vision` (`make build C=vision IMG=vision`), jamais sur le portable : l'image ne se construit que sur la Jetson.

Contenu attendu de `src/` :

- `vision -> ../../../packages/vision` (symlink, `make link C=vision PKG=vision`)
- `custom_interfaces -> ../../../packages/custom_interfaces` (symlink)
- `vision_bringup/` : paquet local avec `launch/vision.launch.py`, lancé par `compose/vision.yml`. À créer avec la première mission qui utilise la caméra : `ros2 pkg create --build-type ament_python vision_bringup`.
