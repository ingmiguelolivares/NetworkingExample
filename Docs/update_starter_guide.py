from pathlib import Path
import re


guide_path = Path(__file__).with_name("GUIA_LAB_UNITY_NETWORKING_LINUX.md")
old = guide_path.read_text(encoding="utf-8")
middle = old[old.index("## 9. Preparación de VirtualBox"):old.index("## 16. Unity Dedicated Server")]
middle = re.sub(r"\n### CHECKPOINT .*?(?=\n---|\n## )", "\n", middle, flags=re.S)

prefix = r'''# GUÍA DE LABORATORIO
## Unity Multiplayer Networking con Linux Kubernetes y Agones

> **Proyecto:** NetworkingExample Starter Project
> **Versión:** Unity 6000.6.0f1
> **Estado:** starter docente con baseline local y bases NGO y NFE
> **Fecha de actualización:** 23 de septiembre de 2026
> **Hosts contemplados:** macOS Apple Silicon y Windows x86-64

## Cómo usar esta guía

El repositorio no es una solución multiplayer terminada. Contiene un gameplay local completo, una base funcional de Netcode for GameObjects y una base ECS de Netcode for Entities. Siete marcadores `STUDENT TODO` señalan el trabajo de programación que completa el estudiante. El Dedicated Server, la máquina virtual, el contenedor, Kubernetes y Agones son pasos del laboratorio y no se han ejecutado ni generado en el starter.

Esta guía usa tres etiquetas:

- **YA IMPLEMENTADO:** existe en el repositorio y compila.
- **ACTIVIDAD DEL ESTUDIANTE:** el estudiante modifica o configura el proyecto.
- **PASO DE LABORATORIO:** se ejecuta fuera del starter y debe demostrarse con evidencia.

Los valores entre `< >`, como `<IP_VM>`, son marcadores. Deben sustituirse por valores observados en el equipo.

> [!IMPORTANT]
> El objetivo final sí es conectar clientes Unity a un Dedicated Server Linux administrado por Kubernetes y Agones. La infraestructura no está preconstruida porque forma parte del aprendizaje. La guía indica qué ya existe y qué debe completar el estudiante.

## 1. Objetivo y resultado final

El laboratorio compara dos implementaciones del mismo comportamiento: NGO, basado en GameObjects y componentes, y NFE, basado en ECS, Worlds, Systems y Ghosts. En ambos casos, el servidor debe validar el movimiento y comunicar el evento PowerUp a todos los clientes.

```text
MISMO COMPUTADOR FÍSICO
│
├── Unity Editor y clientes
│   ├── Cliente 1
│   ├── Cliente 2
│   ├── Cliente 3
│   └── Cliente 4
│          │
│          │ Address UDP Port
│          ▼
└── VirtualBox
    └── Debian
        └── Minikube Kubernetes
            └── Agones GameServer
                └── Unity Dedicated Server
```

Al finalizar, el estudiante deberá demostrar conexión, aparición de jugadores, ownership, movimiento replicado, PowerUp comunicado y UI consistente.

## 2. Arquitectura de CPU y limitación en Apple Silicon

| Host | Arquitectura del host | Guest VirtualBox | ISO Debian | Server Player del starter |
|---|---|---|---|---|
| iMac o MacBook Apple Silicon | ARM64 | ARM64 | `arm64` | Linux x86-64, no nativo |
| Windows Intel o AMD | x86-64 | x86-64 | `amd64` | Linux x86-64, compatible |

`amd64` es el nombre de Debian para x86-64 y funciona en procesadores Intel y AMD. VirtualBox 7.2 sobre macOS ARM ejecuta guests ARM; no convierte una VM ARM64 en una VM x86-64. El target Linux Server estándar disponible en este proyecto produce un ejecutable x86-64.

Consecuencia para el aula:

```text
iMac M4 ARM64
└── Debian ARM64 y Minikube ARM64        disponibles
    └── Unity Linux Server x86-64       no ejecutable de forma nativa
```

En Windows x86-64 puede completarse la ruta end to end descrita. En Apple Silicon se completan el starter, Debian, red, SSH, contenedores y orquestación ARM64, pero la ejecución del servidor requiere un artefacto Linux ARM64 proporcionado por el docente mediante una plataforma Unity compatible o un entorno x86-64 autorizado. No se debe ocultar esta incompatibilidad ni presentar emulación no validada como solución.

## 3. Estado real del repositorio

### 3.1 Versiones y paquetes

| Elemento | Estado real |
|---|---|
| Unity | 6000.6.0f1 |
| Render pipeline | URP 17.6.0 |
| Input System | 1.20.0 |
| Multiplayer Play Mode | 3.0.0 instalado |
| Netcode for GameObjects | 2.13.3, embebido localmente por compatibilidad de ensamblados |
| Netcode for Entities | 6.6.0 resuelto por Unity |
| Entities | 6.6.0 resuelto por Unity |
| Unity Transport | 2.7.4 solicitado, 6.6.0 resuelto con NFE |
| Dedicated Server package | 3.0.0 resuelto por Unity |
| Dedicated Server build | No generado; paso del estudiante |
| Docker Kubernetes Agones | Plantillas incluidas; no ejecutadas |

### 3.2 Escenas y prefabs

| Recurso | Propósito |
|---|---|
| `Assets/Scenes/LocalGameplayBaseline.unity` | Gameplay local de referencia |
| `Assets/Scenes/NGOGameplay.unity` | Base NGO con NetworkManager, UnityTransport y UI de conexión |
| `Assets/Scenes/NFEGameplay.unity` | Presentación y UI de la base NFE |
| `Assets/Scenes/NFE/NFEGameplaySubScene.unity` | SubScene ECS con spawner y Ghost prefab |
| `Assets/Prefabs/NGOPlayer.prefab` | Player GameObject de red |
| `Assets/Prefabs/NFEPlayer.prefab` | Ghost authoring para conversión a Entity |

### 3.3 Estructura relevante

```text
Assets
├── Input/LocalPlayers.inputactions
├── Prefabs/NGOPlayer.prefab y NFEPlayer.prefab
├── Scenes/LocalGameplayBaseline.unity
├── Scenes/NGOGameplay.unity
├── Scenes/NFEGameplay.unity
├── Scenes/NFE/NFEGameplaySubScene.unity
└── Scripts
    ├── Player PowerUp UI
    ├── NGO/NgoConnectionUI.cs
    ├── NGO/NgoPlayerNetwork.cs
    ├── NFE/NfeBootstrap.cs
    ├── NFE/NfeComponents.cs
    ├── NFE/NfeConnectionUI.cs
    ├── NFE/NfeGameplaySystems.cs
    └── NFE/NfePresentationBridge.cs
Infrastructure
├── Containers/NGO/Dockerfile y NFE/Dockerfile
├── Kubernetes/Agones/ngo-gameserver.yaml y nfe-gameserver.yaml
└── Scripts de instalación y construcción para estudio
```

## 4. Gameplay local ya implementado

Abra `Assets/Scenes/LocalGameplayBaseline.unity` y presione Play. La escena contiene plano, cámara, UI y cuatro jugadores.

| Jugador | Movimiento | PowerUp |
|---|---|---|
| Player 1 | W A S D | Space |
| Player 2 | Flechas | Right Ctrl |
| Player 3 | I J K L | O |
| Player 4 | Numpad 8 4 5 6 | Numpad 0 |

`LocalPlayers.inputactions` contiene cuatro Action Maps. `PlayerInputSource` traduce las acciones a movimiento y evento; `PlayerController` mueve sin conocer teclas; `PlayerPowerUp` publica en `PowerUpEvents`; `PowerUpMessageUI` muestra el mensaje durante unos dos segundos.

```text
Input System
├── Move ───────► PlayerController ─► Transform local
└── PowerUp ────► PlayerPowerUp ────► PowerUpEvents ─► UI
```

Esta separación es la referencia observable para NGO y NFE.

## 5. Base NGO incluida

### 5.1 Escena y componentes

`NGOGameplay.unity` contiene `NetworkManager`, `UnityTransport`, el prefab registrado `NGOPlayer.prefab` y un panel de conexión. `NgoConnectionUI` acepta Address y Port, permite Server, Host, Client y Shutdown, y usa UDP 7979 como valor inicial. En batch mode inicia servidor; `-client`, `-address` y `-port` permiten configurar un cliente desde línea de comandos.

`NGOPlayer.prefab` incluye `NetworkObject`, `NetworkTransform` y `NgoPlayerNetwork`. La identidad se replica con `NetworkVariable<int> playerNumber`. El servidor asigna Player 1 a Player 4, cambia etiqueta y color, y coloca el objeto en una posición inicial.

### 5.2 Qué falta

La UI y el transporte están preparados, pero el movimiento autoritativo y el PowerUp por RPC son ejercicios. La vista previa local permite comprobar input antes de completar la red; no debe confundirse con sincronización terminada.

```text
Owner lee input
    │            NGO 01 pendiente
    ▼
Server RPC recibe input
    │            NGO 02 pendiente
    ▼
Servidor mueve NetworkTransform
    │
    ▼
Clientes observan el estado
```

## 6. Base NFE incluida

### 6.1 ECS real

`NfeBootstrap` crea ClientWorld y ServerWorld solo en la escena NFE o con `-nfe`. `NfePlayerAuthoring` y su Baker producen una Entity con `NfePlayerTag`, `NfePlayerState` y `NfePlayerInput`. `NfePlayerState` replica `PlayerNumber` y `Position` mediante `GhostField`. `NfePlayerInput` implementa `IInputComponentData` y contiene movimiento más un `InputEvent` de PowerUp.

`NFEPlayer.prefab` tiene `GhostAuthoring`, modo Owner Predicted, owner habilitado y auto command target. La SubScene contiene `NfePlayerSpawnerAuthoring`. `NfePresentationBridge` crea cápsulas GameObject únicamente para presentar el estado ECS; la autoridad y la simulación deben permanecer en componentes y sistemas ECS.

### 6.2 Flujo que debe completar el estudiante

```text
NfeConnectionUI
    │ NFE 01
    ▼
NetworkStreamDriver Listen y Connect
    │ NFE 02
    ▼
GoInGame RPC y spawn de Ghost con GhostOwner
    │ NFE 03
    ▼
InputComponentData y PredictedSimulationSystemGroup
    │ NFE 04
    ▼
PowerUp RPC del servidor a clientes
```

NFE usa UDP 7980 como valor inicial para evitar mezclar accidentalmente los dos stacks durante las pruebas.

## 7. Comparación de las bases

| Aspecto | NGO | NFE |
|---|---|---|
| Escena | `NGOGameplay.unity` | `NFEGameplay.unity` y SubScene |
| Representación | GameObject y componentes | Entity y componentes de datos |
| Player | `NGOPlayer.prefab` | Ghost `NFEPlayer.prefab` |
| Identidad | `NetworkVariable<int>` | `GhostField PlayerNumber` y `GhostOwner` |
| Input | Input System en `NetworkBehaviour` | `IInputComponentData` en ClientWorld |
| Movimiento | servidor más `NetworkTransform` | sistema predicho y Ghost replication |
| PowerUp | Server RPC y broadcast RPC | `IRpcCommand` y sistemas por World |
| Endpoint inicial | UDP 7979 | UDP 7980 |

Ninguna columna se presenta como mejor. La práctica busca que el estudiante observe cómo dos arquitecturas producen el mismo comportamiento.

## 8. Actividades de programación del estudiante

============================================================

A PARTIR DE AQUÍ COMIENZA EL TRABAJO DE IMPLEMENTACIÓN DEL ESTUDIANTE

============================================================

Existen exactamente siete identificadores `STUDENT TODO`. Cada actividad siguiente corresponde a un identificador único, aunque un mismo identificador aparezca en los lados cliente y servidor.

### ACTIVIDAD STUDENT TODO NGO-01 Enviar input del owner

**OBJETIVO:** enviar el Vector2 del cliente propietario al servidor.
**ARCHIVO:** `Assets/Scripts/NGO/NgoPlayerNetwork.cs`.
**COMPONENTE:** método `Update` y RPC `SubmitMoveRpc`.
**PASOS:** después de leer y limitar `move`, invoque `SubmitMoveRpc(move)`. Mantenga `RpcDelivery.Unreliable` porque el siguiente input reemplaza al anterior.
**RESULTADO ESPERADO:** el servidor actualiza `pendingServerInput`.
**VERIFICACIÓN:** un log temporal o el depurador confirma valores en servidor; elimine logs repetitivos al terminar.

### ACTIVIDAD STUDENT TODO NGO-02 Movimiento autoritativo

**OBJETIVO:** mover solo en servidor y replicar el resultado.
**ARCHIVO:** `Assets/Scripts/NGO/NgoPlayerNetwork.cs`.
**COMPONENTE:** `FixedUpdate`, `pendingServerInput`, `NetworkTransform`.
**PASOS:** valide y limite input, calcule desplazamiento con `moveSpeed` y tiempo fijo, aplique límites horizontales y actualice el Transform en servidor. Decida si conserva la vista previa local; explique el efecto visual.
**RESULTADO ESPERADO:** todos los clientes observan la posición autoritativa.
**VERIFICACIÓN:** mover un cliente y comparar las demás ventanas.

### ACTIVIDAD STUDENT TODO NGO-03 PowerUp por RPC

**OBJETIVO:** sustituir el evento local por solicitud, validación y broadcast.
**ARCHIVO:** `Assets/Scripts/NGO/NgoPlayerNetwork.cs`.
**COMPONENTE:** `OnPowerUpPerformed` y nuevos RPC.
**PASOS:** cree un RPC owner a servidor; valide que el objeto esté spawned y tenga identidad; desde servidor envíe un RPC a clientes; en cada cliente llame `PowerUpEvents.RaiseActivated` una sola vez.
**RESULTADO ESPERADO:** cuatro clientes muestran `Player N activated PowerUp` durante unos dos segundos.
**VERIFICACIÓN:** un solo mensaje por pulsación, con el número asignado por servidor.

### ACTIVIDAD STUDENT TODO NFE-01 Listen y Connect

**OBJETIVO:** abrir el endpoint del ServerWorld y conectar el ClientWorld.
**ARCHIVO:** `Assets/Scripts/NFE/NfeConnectionUI.cs`.
**COMPONENTE:** `StartServer` y `ConnectClient`.
**PASOS:** obtenga `NetworkStreamDriver` del World correspondiente. En servidor llame `Listen(NetworkEndpoint.AnyIpv4.WithPort(ReadPort()))`. En cliente use el `endpoint` ya construido y `Connect(client.EntityManager, endpoint)`.
**RESULTADO ESPERADO:** aparece `NetworkId` en ClientWorld.
**VERIFICACIÓN:** la UI muestra Local client ID y el puerto UDP 7980 aparece en escucha.

### ACTIVIDAD STUDENT TODO NFE-02 GoInGame y spawn

**OBJETIVO:** marcar la conexión InGame y crear un Ghost con owner.
**ARCHIVO:** `Assets/Scripts/NFE/NfeGameplaySystems.cs`.
**COMPONENTE:** `NfeGoInGameClientSystem` y `NfeGoInGameServerSystem`.
**PASOS:** el cliente añade `NetworkStreamInGame` y envía `NfeGoInGameRequest`. El servidor consume el RPC, marca la conexión, instancia `NfePlayerSpawner.PlayerPrefab`, asigna `GhostOwner.NetworkId`, fija `PlayerNumber` y vincula la entidad a la conexión.
**RESULTADO ESPERADO:** un Ghost distinto por conexión.
**VERIFICACIÓN:** Entities Hierarchy muestra owner e identidad coherentes.

### ACTIVIDAD STUDENT TODO NFE-03 Movimiento predicho

**OBJETIVO:** aplicar `NfePlayerInput.Move` dentro de la simulación predicha.
**ARCHIVO:** `Assets/Scripts/NFE/NfeGameplaySystems.cs`.
**COMPONENTE:** `NfeMovementSystem`.
**PASOS:** consulte ghosts simulados, normalice el input, actualice `NfePlayerState.Position` con `DeltaTime` y aplique los límites del baseline. Mantenga el sistema en `PredictedSimulationSystemGroup`.
**RESULTADO ESPERADO:** cliente propietario predice y servidor confirma el estado.
**VERIFICACIÓN:** las ventanas convergen en la misma posición y un no owner no controla el Ghost.

### ACTIVIDAD STUDENT TODO NFE-04 PowerUp RPC

**OBJETIVO:** convertir el InputEvent en un resultado de servidor para todos los clientes.
**ARCHIVO:** `Assets/Scripts/NFE/NfeGameplaySystems.cs`.
**COMPONENTE:** `NfePowerUpServerSystem`, `NfePowerUpClientSystem` y `NfePowerUpResultRpc`.
**PASOS:** el servidor detecta `PowerUp.IsSet`, crea un RPC por conexión con el `PlayerNumber`; el cliente consume el RPC, publica `PowerUpEvents` y destruye la entidad RPC recibida.
**RESULTADO ESPERADO:** UI idéntica en todos los clientes sin duplicados.
**VERIFICACIÓN:** una pulsación produce un resultado por cliente y desaparece a los dos segundos.

'''

suffix = r'''## 16. Generación del Dedicated Server

Este paso lo realiza el estudiante después de completar y probar uno de los stacks. NGO y NFE necesitan builds separados porque usan escenas, bootstrap y puertos distintos.

### 16.1 Preparar un perfil NGO

1. Abra `File > Build Profiles`.
2. Seleccione `Add Build Profile` y luego `Linux Server`.
3. Instale el módulo desde Unity Hub solo si Unity indica que falta.
4. Active únicamente `Assets/Scenes/NGOGameplay.unity` para este perfil.
5. Elija la carpeta de salida `Builds/NGO-LinuxServer`.
6. Use `Build`, no `Build and Run` durante la preparación.

### 16.2 Preparar un perfil NFE

Repita el proceso con `Assets/Scenes/NFEGameplay.unity` y salida `Builds/NFE-LinuxServer`. La SubScene es una dependencia de la escena principal. No mezcle la escena NGO en este build.

### 16.3 Verificar el artefacto

En el host, identifique el ejecutable y su arquitectura:

```bash
file Builds/NGO-LinuxServer/<EJECUTABLE>
```

El build Linux Server estándar debe informar ELF x86-64. Registre el nombre real; no reemplace `<EJECUTABLE>` hasta observarlo.

## 17. Transferencia y ejecución en Debian

Copie el directorio completo mediante SSH:

```bash
scp -r Builds/NGO-LinuxServer student@<IP_VM>:/home/student/ngo-server
```

En Debian:

```bash
cd /home/student/ngo-server
ls -la
chmod +x <EJECUTABLE>
./<EJECUTABLE> -batchmode -nographics -port 7979
```

Para NFE use su directorio, `-nfe` cuando el arranque lo requiera y puerto 7980. `chmod +x` concede permiso de ejecución; no use `chmod 777`. `./` ejecuta el archivo del directorio actual.

Verifique proceso y socket:

```bash
pgrep -af <EJECUTABLE>
sudo ss -lunp | grep -E '7979|7980'
```

`ss -lunp` muestra sockets UDP en escucha con valores numéricos y proceso. `pgrep -af` demuestra que el proceso existe; `ss` demuestra que abrió un puerto.

## 18. Contenedor del servidor

Una imagen contiene el ejecutable y sus dependencias. Un container es una ejecución aislada de esa imagen. El Dockerfile describe la construcción y un registry almacena imágenes para que Kubernetes pueda obtenerlas.

El repositorio incluye `Infrastructure/Containers/NGO/Dockerfile` y `Infrastructure/Containers/NFE/Dockerfile`. Ambos esperan que el estudiante haya generado previamente el build correspondiente. No se construyeron en el starter.

En Debian amd64, desde la raíz transferida del repositorio:

```bash
docker build -f Infrastructure/Containers/NGO/Dockerfile -t networking-lab-ngo:local .
docker image inspect networking-lab-ngo:local
```

Antes de construir, abra el Dockerfile, confirme la ruta `COPY`, el ejecutable y el puerto. En Apple Silicon, una imagen ARM64 no puede ejecutar un binario Unity x86-64 de forma nativa. La plataforma de imagen y la del ejecutable deben coincidir.

## 19. Kubernetes single node con Minikube

Esta guía selecciona Minikube con driver Docker porque crea un cluster de un nodo, funciona en Linux amd64 y arm64 y es apropiado para un laboratorio. Agones documenta Minikube para evaluación local. No se instala en el starter.

Conceptos:

| Término | Función en el laboratorio |
|---|---|
| Cluster | conjunto administrado por Kubernetes |
| Node | Debian o nodo Minikube que ejecuta Pods |
| Pod | unidad que contiene el servidor de juego |
| Container | proceso aislado creado desde la imagen |
| YAML | descripción declarativa de recursos |
| kubectl | cliente para consultar y aplicar recursos |

El script `Infrastructure/Scripts/install-minikube-agones.sh` es material de referencia. Léalo antes de ejecutarlo y compruebe versiones. La combinación documentada al preparar el starter es Minikube 1.39.0, Kubernetes 1.34.6 y Agones 1.60.0.

Ejemplo de comprobación después de la instalación del estudiante:

```bash
minikube start --driver=docker --kubernetes-version=v1.34.6
kubectl get nodes -o wide
```

El estado esperado es `Ready`. Si aparece `NotReady`, consulte `kubectl describe node` y no continúe a Agones.

## 20. Agones y GameServer

Kubernetes administra workloads. Agones añade recursos y controladores para servidores de juegos. Agones no reemplaza Unity Transport ni NGO o NFE.

```text
Unity Client ── UDP ──► Unity Dedicated Server
                              ▲
                              │ administrado como GameServer
                           Agones
                              ▲
                         Kubernetes
```

Instale Agones siguiendo la versión del script y compruebe el namespace:

```bash
kubectl get pods -n agones-system
kubectl get crd gameservers.agones.dev
```

Las plantillas están en `Infrastructure/Kubernetes/Agones`. Antes de aplicar, el estudiante debe sustituir la imagen, confirmar `containerPort`, `hostPort` o política de asignación, protocolo UDP y puerto del stack.

```bash
kubectl apply -f Infrastructure/Kubernetes/Agones/ngo-gameserver.yaml
kubectl get gameserver
kubectl describe gameserver <NOMBRE>
kubectl get pods -o wide
```

Un GameServer solo alcanza `Ready` cuando el proceso integra el ciclo de vida requerido por Agones. Las plantillas no incorporan silenciosamente esa integración. El estudiante debe implementar el uso del SDK o del REST sidecar expuesto mediante `AGONES_SDK_HTTP_PORT`, llamar `/ready` cuando el transporte escuche y enviar `/health` de forma periódica. Esto es una actividad de infraestructura, no uno de los siete TODO de gameplay.

## 21. Address y Port desde el host

El cliente está en macOS o Windows; el Pod está dentro de Minikube en Debian. La IP interna del Pod no es el endpoint que debe escribirse en Unity.

Para este laboratorio, el GameServer debe publicar un `hostPort` UDP en el nodo Minikube y la red Host Only debe permitir llegar a Debian. Obtenga datos reales:

```bash
kubectl get gameserver <NOMBRE> -o jsonpath='{.status.address}{"\n"}{.status.ports[0].port}{"\n"}'
minikube ip
```

Si Agones publica la IP del nodo interno de Minikube, el host físico puede no enrutarla. En ese caso configure un reenvío UDP explícito desde la IP Host Only de Debian al endpoint del nodo, o ejecute Minikube con una configuración de red validada por el docente. No use la IP del Pod ni asuma que `localhost` cruza la VM.

Los campos de Unity son:

- NGO: Address más UDP 7979 por defecto.
- NFE: Address más UDP 7980 por defecto.

Reemplace esos puertos por el puerto asignado que muestre `GameServer.status` si Agones lo cambia.

## 22. Multiplayer Play Mode y cuatro clientes

Multiplayer Play Mode 3.0 está instalado. Abra `Window > Play Mode > Scenarios`, cree un escenario y añada hasta tres Additional Editor Instances además del Editor principal. Cada proceso cliente debe usar el mismo Address y Port; no inicie un servidor local si el objetivo es el GameServer de Debian.

Verifique primero un cliente. Después agregue los demás uno a uno y observe logs de cliente, servidor y Agones. Cuatro jugadores locales en `LocalGameplayBaseline` no equivalen a cuatro clientes.

## 23. Veintiún checkpoints

### CHECKPOINT 1 Starter project comprendido
**OBJETIVO:** reconocer entregables y límites. **PROCEDIMIENTO:** leer secciones 1 a 3. **VERIFICACIÓN:** ubicar tres escenas y dos prefabs. **RESULTADO ESPERADO:** distinguir implementado y pendiente.

### CHECKPOINT 2 Gameplay comprendido
**OBJETIVO:** seguir input a UI. **PROCEDIMIENTO:** ejecutar el baseline. **VERIFICACIÓN:** cuatro controles y mensajes. **RESULTADO ESPERADO:** referencia local operativa.

### CHECKPOINT 3 Base NGO comprendida
**OBJETIVO:** reconocer componentes NGO. **PROCEDIMIENTO:** abrir escena y prefab. **VERIFICACIÓN:** NetworkManager, UnityTransport, NetworkObject y NetworkTransform. **RESULTADO ESPERADO:** mapa de responsabilidades.

### CHECKPOINT 4 Base NFE comprendida
**OBJETIVO:** reconocer ECS y Ghost. **PROCEDIMIENTO:** revisar escena, SubScene y scripts. **VERIFICACIÓN:** Components, Systems, Worlds y GhostAuthoring. **RESULTADO ESPERADO:** flujo NFE explicado.

### CHECKPOINT 5 TODO identificados
**OBJETIVO:** planificar programación. **PROCEDIMIENTO:** buscar `STUDENT TODO`. **VERIFICACIÓN:** siete identificadores únicos y siete actividades. **RESULTADO ESPERADO:** correspondencia exacta.

### CHECKPOINT 6 Dedicated Server generado
**OBJETIVO:** crear build de un stack. **PROCEDIMIENTO:** usar Linux Server Build Profile. **VERIFICACIÓN:** `file` identifica ejecutable y arquitectura. **RESULTADO ESPERADO:** directorio completo de build.

### CHECKPOINT 7 VirtualBox instalado
**OBJETIVO:** disponer del hipervisor. **PROCEDIMIENTO:** instalar versión correcta para el host. **VERIFICACIÓN:** VirtualBox abre. **RESULTADO ESPERADO:** aplicación operativa.

### CHECKPOINT 8 Debian instalado
**OBJETIVO:** preparar guest mínimo. **PROCEDIMIENTO:** instalar ISO de arquitectura correcta. **VERIFICACIÓN:** login y `uname -m`. **RESULTADO ESPERADO:** Debian inicia sin GUI.

### CHECKPOINT 9 Host y VM comunicados
**OBJETIVO:** comprobar Host Only. **PROCEDIMIENTO:** obtener IP y hacer ping. **VERIFICACIÓN:** respuestas desde el host. **RESULTADO ESPERADO:** red privada funcional.

### CHECKPOINT 10 SSH funcionando
**OBJETIVO:** administrar Debian remotamente. **PROCEDIMIENTO:** instalar y habilitar ssh. **VERIFICACIÓN:** sesión `ssh student@<IP_VM>`. **RESULTADO ESPERADO:** terminal remota.

### CHECKPOINT 11 Server transferido
**OBJETIVO:** copiar build. **PROCEDIMIENTO:** usar `scp -r`. **VERIFICACIÓN:** `ls -la` muestra todos los archivos. **RESULTADO ESPERADO:** copia íntegra.

### CHECKPOINT 12 Container preparado
**OBJETIVO:** empaquetar servidor. **PROCEDIMIENTO:** revisar Dockerfile y construir. **VERIFICACIÓN:** `docker image inspect`. **RESULTADO ESPERADO:** imagen con arquitectura correcta.

### CHECKPOINT 13 Kubernetes instalado
**OBJETIVO:** crear cluster local. **PROCEDIMIENTO:** iniciar Minikube con Docker. **VERIFICACIÓN:** `kubectl version` y contexto Minikube. **RESULTADO ESPERADO:** API accesible.

### CHECKPOINT 14 Node Ready
**OBJETIVO:** validar nodo. **PROCEDIMIENTO:** `kubectl get nodes`. **VERIFICACIÓN:** estado Ready. **RESULTADO ESPERADO:** scheduler disponible.

### CHECKPOINT 15 Agones instalado
**OBJETIVO:** añadir controladores de juego. **PROCEDIMIENTO:** instalar versión compatible. **VERIFICACIÓN:** Pods y CRD de Agones. **RESULTADO ESPERADO:** agones-system saludable.

### CHECKPOINT 16 GameServer desplegado
**OBJETIVO:** crear recurso. **PROCEDIMIENTO:** aplicar YAML ajustado. **VERIFICACIÓN:** GameServer, Pod y logs. **RESULTADO ESPERADO:** proceso ejecutándose y ciclo de vida integrado.

### CHECKPOINT 17 Address y Port obtenidos
**OBJETIVO:** identificar endpoint. **PROCEDIMIENTO:** consultar status de GameServer. **VERIFICACIÓN:** valores reales y ruta desde host. **RESULTADO ESPERADO:** endpoint UDP alcanzable.

### CHECKPOINT 18 Unity conectado
**OBJETIVO:** conectar un cliente. **PROCEDIMIENTO:** introducir Address y Port. **VERIFICACIÓN:** ID y logs de ambos extremos. **RESULTADO ESPERADO:** conexión estable.

### CHECKPOINT 19 Movimiento de red
**OBJETIVO:** validar autoridad y réplica. **PROCEDIMIENTO:** mover un owner. **VERIFICACIÓN:** servidor y clientes convergen. **RESULTADO ESPERADO:** posición consistente.

### CHECKPOINT 20 PowerUp de red
**OBJETIVO:** validar evento. **PROCEDIMIENTO:** activar PowerUp. **VERIFICACIÓN:** mensaje único y jugador correcto en todos. **RESULTADO ESPERADO:** broadcast y UI por dos segundos.

### CHECKPOINT 21 Múltiples clientes
**OBJETIVO:** probar cuatro procesos. **PROCEDIMIENTO:** añadir clientes uno a uno en MPPM. **VERIFICACIÓN:** cuatro conexiones y cuatro owners. **RESULTADO ESPERADO:** laboratorio completo.

## 24. Diagnóstico de problemas

| Problema | Posible causa | Verificación | Solución segura |
|---|---|---|---|
| Unity no compila | TODO incompleto o API incorrecta | Console y primer error C# | Corregir el primer error antes de continuar |
| NGO no conecta | Address o UDP 7979 incorrecto | UI y `ss -lunp` | Usar endpoint real y confirmar servidor |
| NFE no conecta | NFE 01 incompleto | NetworkId y logs | Completar Listen y Connect |
| No aparece Player NGO | prefab no registrado o spawn falló | NetworkManager Prefabs y logs | Restaurar registro y revisar servidor |
| No aparece Ghost NFE | NFE 02 incompleto | Entities Hierarchy | Completar GoInGame y owner |
| VM no inicia | ISO con arquitectura incorrecta | nombre de ISO | usar arm64 en Mac ARM o amd64 en Windows x64 |
| Binario no ejecuta | x86-64 dentro de Debian ARM64 | `uname -m` y `file` | usar entorno o artefacto compatible definido por docente |
| Debian sin Internet | NAT desconectado | `ip route` y ping | habilitar Adapter 1 NAT |
| Host no llega a VM | Host Only ausente | `ip -br addr` | habilitar Adapter 2 Host Only |
| SSH falla | servicio detenido o IP incorrecta | `systemctl status ssh` | habilitar servicio y usar IP Host Only |
| Permission denied | falta permiso x | `ls -l` | `chmod +x` al ejecutable |
| Container cierra | ruta o ejecutable incorrecto | `docker logs` | revisar Dockerfile y arquitectura |
| Node NotReady | Minikube o runtime incompleto | `kubectl describe node` | resolver condición antes de Agones |
| Agones Pods fallan | versión incompatible o recursos | Pods de agones-system | revisar eventos y matriz de versiones |
| GameServer no llega a Ready | falta ciclo de vida Agones | describe y logs | implementar Ready y Health mediante SDK o REST |
| Address no es alcanzable | dirección interna de Minikube | ruta y ping | publicar o reenviar UDP por IP Host Only |
| Puerto no aparece | transporte no escucha | `ss -lunp` | revisar puerto y logs del servidor |
| Movimiento solo local | NGO 01/02 o NFE 03 incompletos | comparar ventanas | completar autoridad y réplica |
| PowerUp solo local | NGO 03 o NFE 04 incompleto | logs y UI | completar solicitud y broadcast |
| Firewall bloquea UDP | regla específica ausente | `nft list ruleset` | abrir solo el puerto UDP requerido |

## 25. Actividades de análisis

1. Explique por qué `127.0.0.1` del host no apunta a Debian.
2. Distinga NetworkObject de Ghost usando archivos reales del starter.
3. Explique por qué el input no debe otorgar autoridad ilimitada al cliente.
4. Compare un RPC de PowerUp con la réplica frecuente de posición.
5. Explique la función de `GhostOwner` y de `NetworkVariable<int>`.
6. ¿Qué demuestra `ss` que `ps` no demuestra?
7. ¿Por qué el Address de un Pod no suele ser el endpoint del host?
8. ¿Qué administra Agones y qué sigue administrando Unity Transport?
9. ¿Por qué una imagen ARM64 no corrige un ejecutable x86-64 dentro de ella?
10. ¿Qué cambia al cerrar el Dedicated Server mientras los clientes están conectados?

Deje espacio para responder en una hoja separada o en la copia digital. No consulte una respuesta automática antes de justificarla con evidencias del laboratorio.

## 26. Evidencias a entregar

- ☐ Baseline con cuatro jugadores y PowerUp local
- ☐ Siete TODO identificados y código comentado
- ☐ Compilación NGO y NFE sin errores
- ☐ Dedicated Server generado y arquitectura identificada
- ☐ Debian instalado y `uname -m`
- ☐ IP Host Only identificada y ping
- ☐ SSH funcionando
- ☐ Build transferido
- ☐ Imagen de container inspeccionada
- ☐ Node Kubernetes Ready
- ☐ Agones operativo
- ☐ GameServer y Pod observados
- ☐ Address y Port reales
- ☐ Primer cliente conectado
- ☐ Cuatro clientes conectados
- ☐ Movimiento replicado
- ☐ PowerUp visible en cuatro clientes
- ☐ Preguntas de análisis respondidas

No entregue capturas simuladas. Incluya comandos y resultados suficientes para que el docente pueda relacionar cada evidencia con su checkpoint.

## 27. Seguridad y buenas prácticas

- Use `sudo` solo para administración del sistema.
- No ejecute el servidor como root.
- No use `chmod 777`.
- No desactive permanentemente el firewall.
- Abra únicamente el puerto UDP observado.
- Revise rutas antes de `rm`; el borrado desde terminal puede ser irreversible.
- No publique contraseñas, tokens ni kubeconfig.
- Detenga primero con `kill <PID>` y use señales forzadas solo después de diagnosticar.

## 28. Fuentes oficiales

- [Unity Dedicated Server build](https://docs.unity3d.com/6000.0/Documentation/Manual/dedicated-server-build.html)
- [Unity Multiplayer Play Mode 3.0](https://docs.unity3d.com/Packages/com.unity.multiplayer.playmode@3.0/manual/index.html)
- [Netcode for GameObjects](https://docs.unity3d.com/Packages/com.unity.netcode.gameobjects@2.13/manual/index.html)
- [Netcode for Entities](https://docs.unity3d.com/Packages/com.unity.netcode@6.6/manual/index.html)
- [Oracle VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads)
- [Oracle VirtualBox 7.2 User Manual](https://download.virtualbox.org/virtualbox/7.2.20/UserManual.pdf)
- [Debian stable](https://www.debian.org/releases/stable/)
- [Minikube documentation](https://minikube.sigs.k8s.io/docs/)
- [Agones install on Minikube](https://agones.dev/site/docs/installation/creating-cluster/minikube/)
- [Agones GameServer specification](https://agones.dev/site/docs/reference/gameserver/)
- [Agones REST SDK](https://agones.dev/site/docs/guides/client-sdks/rest/)

## 29. Cierre

El starter conserva el gameplay local y añade dos bases reales sin resolver los ejercicios centrales. NGO deja lista la conexión, identidad y réplica de Transform; NFE deja listos Worlds, componentes, Ghost y sistemas de extensión. El estudiante completa siete actividades y después construye, despliega y prueba el servidor mediante Debian, Minikube y Agones.

El resultado final se considera completo solo cuando la evidencia demuestra conectividad, ownership, movimiento y PowerUp en cuatro clientes. La incompatibilidad x86-64 frente a ARM64 debe resolverse con un artefacto o entorno aprobado, no con una suposición.
'''

middle = middle.replace("## 9. Preparación de VirtualBox", "## 9. Preparación de VirtualBox")
middle = middle.replace("La descarga oficial es", "VirtualBox es un hipervisor de escritorio. La descarga oficial es")
new = prefix + middle + suffix
guide_path.write_text(new, encoding="utf-8")
