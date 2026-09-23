# GUÍA DE LABORATORIO
## Unity Multiplayer — Cliente/Servidor con Linux

> **Proyecto:** Unity Multiplayer Networking Lab  
> **Versión inspeccionada:** Unity 6000.6.0f1  
> **Estado del proyecto:** `LOCAL BASELINE`  
> **Fecha de verificación técnica:** 22 de septiembre de 2026  
> **Hosts contemplados:** macOS Apple Silicon y Windows x86-64

---

## Cómo leer esta guía

Esta guía diferencia tres tipos de contenido:

- **YA IMPLEMENTADO:** existe y fue comprobado en el proyecto recibido.
- **PASO DEL ESTUDIANTE:** se puede realizar con el estado actual del laboratorio.
- **PENDIENTE DE IMPLEMENTACIÓN EN EL PROYECTO DOCENTE:** depende de una fase futura. No debe presentarse como una función disponible.

Los valores entre signos `< >`, por ejemplo `<IP_VM>`, son **marcadores de posición**. Deben reemplazarse con un valor observado en el equipo; no se copian literalmente.

> [!IMPORTANT]
> Esta versión del proyecto no contiene networking. No tiene NGO, NFE, `NetworkManager`, `UnityTransport`, Player prefab de red, dirección de servidor, puerto de juego ni Dedicated Server generado. La preparación de Linux sí puede realizarse; la conexión multiplayer queda documentada como trabajo futuro.

---

## 1. Introducción

El laboratorio separa primero el gameplay local de la tecnología de red. Esta separación permite estudiar más adelante dos implementaciones distintas —Netcode for GameObjects (NGO) y Netcode for Entities (NFE)— sin cambiar el comportamiento observable del juego.

En el baseline actual hay un plano, cuatro cápsulas que representan jugadores, una cámara y una interfaz. Los cuatro jugadores comparten el teclado del mismo computador. Cada jugador puede moverse y activar un PowerUp local que únicamente publica un mensaje en pantalla durante aproximadamente dos segundos.

El objetivo futuro es ejecutar clientes Unity en el host y un servidor sin interfaz gráfica dentro de Linux:

```text
COMPUTADOR FÍSICO (host)
│
├── Unity Editor / clientes
│   ├── Cliente 1
│   ├── Cliente 2
│   ├── Cliente 3
│   └── Cliente 4
│
└── VirtualBox
    └── Debian (guest)
        └── Unity Dedicated Server
```

Ese diagrama representa la meta pedagógica, no el estado actual.

---

## 2. Objetivos de aprendizaje

Al terminar las partes disponibles de esta guía, el estudiante podrá:

1. reconocer la estructura y el flujo del baseline local;
2. distinguir input, gameplay, evento y presentación;
3. explicar cliente, servidor, host, guest, IP y puerto;
4. instalar VirtualBox y Debian con la arquitectura correcta;
5. usar una terminal Linux para navegación, paquetes, red, procesos y permisos;
6. configurar una red reproducible entre el host y la VM;
7. instalar y comprobar SSH;
8. transferir archivos con `scp` cuando exista un build;
9. explicar cómo se produce y ejecuta un Dedicated Server;
10. identificar con precisión qué partes aún no están implementadas.

Los objetivos de conexión de cuatro clientes, ownership, sincronización de movimiento y broadcast de PowerUp se completarán después de implementar NGO.

---

## 3. Arquitectura del laboratorio y limitación de CPU

### 3.1 Conceptos

- **Host:** sistema operativo físico que ejecuta VirtualBox. En el aula será principalmente macOS sobre iMac M4.
- **Guest:** sistema operativo virtualizado. En esta guía será Debian.
- **Cliente:** proceso que recibe input del jugador y presenta el estado del juego.
- **Servidor:** proceso que acepta conexiones, valida solicitudes y mantiene el estado compartido.
- **Dedicated Server:** servidor sin jugador local y sin necesidad de renderizar la escena.

### 3.2 Arquitecturas diferentes

| Host | CPU del host | Guest que virtualiza VirtualBox | ISO Debian |
|---|---|---|---|
| iMac/MacBook Apple Silicon | ARM64/AArch64 | ARM64 | `arm64` |
| Windows típico Intel/AMD | x86-64 | x86-64 | `amd64` |

`amd64` no significa “solo AMD”; es el nombre usado por Debian para la arquitectura x86-64 de Intel y AMD.

### 3.3 Limitación crítica en Apple Silicon

Oracle VirtualBox 7.2 en macOS ARM64 ejecuta guests ARM64; no ejecuta guests x86. Sin embargo, Unity 6 soporta su plataforma de servidor Linux estándar en Ubuntu AMD64/x64, no en Linux ARM64. Las fuentes oficiales son:

- [Oracle VirtualBox 7.2 User Manual](https://download.virtualbox.org/virtualbox/7.2.20/UserManual.pdf)
- [Unity 6 system requirements — Server platform](https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html#server)

Consecuencia:

```text
iMac M4 (ARM64)
└── VirtualBox
    └── Debian ARM64                 FUNCIONA
        └── Unity Linux Server x64   NO ES COMPATIBLE
```

Por ello, en Apple Silicon esta guía permite completar Debian, terminal, red y SSH, pero el checkpoint de ejecutar el servidor Linux estándar queda **BLOQUEADO POR ARQUITECTURA** hasta que el proyecto docente adopte una solución compatible.

En Windows x86-64, VirtualBox puede ejecutar Debian amd64 y la arquitectura coincide con un build Unity Linux x64. Aun así, Unity documenta oficialmente Ubuntu 22.04/24.04 AMD64 para el Server Player; Debian 13 es una plataforma educativa razonable, pero su ejecución debe validarse y no se presenta como soporte oficial de Unity.

> [!NOTE]
> “Embedded Linux ARM64” es un producto/plataforma distinta y no equivale al Dedicated Server Linux estándar de este proyecto. No se asume disponible.

---

## 4. Requisitos

### Comunes

- proyecto completo del laboratorio;
- Unity Editor **6000.6.0f1** instalado mediante Unity Hub;
- al menos 20 GB libres para la VM y espacio adicional para Unity;
- conexión a Internet para descargar VirtualBox, Debian y paquetes;
- cuenta local con permiso para instalar aplicaciones.

### macOS — Apple Silicon

- iMac M4, MacBook M1 o posterior;
- instalador **macOS / Apple Silicon hosts** de VirtualBox;
- ISO Debian estable **arm64**.

### Windows — x86-64

- Windows 10/11 x86-64 sobre procesador Intel o AMD;
- virtualización de hardware habilitada en BIOS/UEFI;
- instalador **Windows hosts** de VirtualBox;
- ISO Debian estable **amd64**.

---

## 5. Conociendo el proyecto Unity

### 5.1 Estado inspeccionado

| Elemento | Estado real |
|---|---|
| Unity | 6000.6.0f1 |
| Render pipeline | URP 17.6.0 |
| Input System | 1.20.0, activo |
| Multiplayer Play Mode | 3.0.0 instalado |
| Escena principal | `Assets/Scenes/LocalGameplayBaseline.unity` |
| Escena de plantilla | `Assets/Scenes/SampleScene.unity` |
| Gameplay local | Implementado y probado |
| NGO | No instalado / no implementado |
| NFE | No instalado / no implementado |
| Dedicated Server Build Support | Módulo Linux instalado en el equipo de desarrollo inspeccionado |
| Build Profile de servidor | No existe |
| Build de servidor | No existe |
| Puerto de juego | No existe/configurado |
| IP configurable en UI | No existe |
| Player prefab de red | No existe |
| `NetworkManager` / `UnityTransport` | No existen |
| Escenario Multiplayer Play Mode | No configurado |

### 5.2 Estructura relevante

```text
Assets/
├── Input/
│   └── LocalPlayers.inputactions
├── Materials/
│   ├── Ground.mat
│   └── Player1.mat ... Player4.mat
├── Scenes/
│   ├── LocalGameplayBaseline.unity
│   └── SampleScene.unity
├── Scripts/
│   ├── Editor/LocalBaselineSceneBuilder.cs
│   ├── Player/PlayerInputSource.cs
│   ├── Player/PlayerController.cs
│   ├── PowerUp/PlayerPowerUp.cs
│   ├── PowerUp/PowerUpEvents.cs
│   └── UI/PowerUpMessageUI.cs
└── Tests/PlayMode/
    └── LocalBaselinePlayModeTests.cs
```

### 5.3 Abrir y ejecutar

1. Abra el proyecto con Unity 6000.6.0f1.
2. En `Project`, abra `Assets/Scenes/LocalGameplayBaseline.unity`.
3. Compruebe que la jerarquía contiene `Ground`, `Main Camera`, `UI`, `EventSystem` y `Player 1` a `Player 4`.
4. Presione **Play**.
5. Pruebe movimiento y PowerUp con la tabla siguiente.

| Jugador | Movimiento | PowerUp |
|---|---|---|
| Player 1 | W A S D | Space |
| Player 2 | Flechas | Right Ctrl |
| Player 3 | I J K L | O |
| Player 4 | Numpad 8, 4, 5, 6 | Numpad 0 |

> [!NOTE]
> Player 4 requiere un teclado con bloque numérico o un teclado externo.

### CHECKPOINT 1 — Proyecto Unity comprendido

**OBJETIVO:** identificar escena, objetos y flujo local.  
**PROCEDIMIENTO:** abrir la escena, entrar en Play Mode y probar cuatro controles.  
**VERIFICACIÓN:** existen cuatro cápsulas, cada control mueve su jugador y cada PowerUp muestra el nombre correcto.  
**RESULTADO ESPERADO:** baseline local operativo, sin conexiones de red.

---

## 6. Componentes reales del proyecto

### 6.1 `LocalPlayers.inputactions`

**Qué es:** un `InputActionAsset` del Input System.  
**Dónde está:** `Assets/Input/LocalPlayers.inputactions`.  
**Qué contiene:** cuatro action maps (`Player 1` ... `Player 4`), cada uno con acciones `Move` y `PowerUp`.  
**Qué produce:** valores `Vector2` para movimiento y callbacks cuando se activa PowerUp.  
**Por qué importa:** las teclas pueden cambiarse sin reescribir `PlayerController`.

### 6.2 `PlayerInputSource`

Es el adaptador entre Input System y gameplay. Recibe el asset y el nombre del action map serializados en la escena. Al habilitarse durante Play Mode resuelve `Move` y `PowerUp`, activa el mapa y expone:

```csharp
public Vector2 Movement => moveAction?.ReadValue<Vector2>() ?? Vector2.zero;
public event Action PowerUpPressed;
```

No mueve objetos ni muestra UI. Su salida es input abstracto.

### 6.3 `PlayerController`

Recibe un `PlayerInputSource`. En cada `Update` consulta `Movement`, normaliza el vector, multiplica por velocidad y `Time.deltaTime`, desplaza el `Transform` y limita X/Z dentro del terreno.

```text
InputAction Move
      │
      ▼
PlayerInputSource.Movement
      │
      ▼
PlayerController.Move
      │
      ▼
Transform.position
```

No conoce W, flechas, IJKL ni numpad. Tampoco hereda de `NetworkBehaviour`.

### 6.4 `PlayerPowerUp`

Guarda un nombre (`Player 1`, etc.) y una referencia a `PlayerInputSource`. Se suscribe a `PowerUpPressed`; al recibirlo llama `ActivatePowerUp()` y publica un evento de gameplay. No produce todavía otro efecto.

### 6.5 `PowerUpEvents`

Es un canal estático y neutral respecto a networking:

```csharp
public static event Action<string> Activated;
```

Recibe el nombre del jugador y lo entrega a cualquier suscriptor. En una fase futura un adaptador de red podría publicar el mismo evento después de validar una solicitud en el servidor.

### 6.6 `PowerUpMessageUI`

Se suscribe a `PowerUpEvents.Activated`, escribe `Player N activated PowerUp`, reinicia una coroutine si llega otro evento y limpia el texto después de dos segundos.

```text
Input PowerUp
    │
    ▼
PlayerPowerUp.ActivatePowerUp()
    │
    ▼
PowerUpEvents.Activated
    │
    ▼
PowerUpMessageUI
```

### 6.7 Identificación actual

No existe `PlayerIdentity`. La identificación es local y consiste en:

- nombre del GameObject;
- nombre del action map;
- campo `playerName` en `PlayerPowerUp`;
- material de color y `TextMesh` sobre cada cápsula.

No existe un ID asignado por servidor.

### 6.8 UI

El GameObject `UI` contiene Canvas, `Title`, `Controls`, `PowerUpMessage`, `PowerUpMessageUI`, `CanvasScaler` y `GraphicRaycaster`. `EventSystem` utiliza `InputSystemUIInputModule`.

### 6.9 Pruebas automatizadas

`LocalBaselinePlayModeTests` valida:

- cuatro jugadores, terreno, cámara y UI;
- movimiento con las teclas reales configuradas;
- bindings exactos;
- PowerUp de cada jugador y desaparición del mensaje.

---

## 7. Flujo actual y flujo futuro

### Actual — YA IMPLEMENTADO

```text
Teclado local
    │
    ▼
PlayerInputSource
    ├── Move ─────► PlayerController ─────► Transform local
    │
    └── PowerUp ──► PlayerPowerUp
                         │
                         ▼
                   PowerUpEvents
                         │
                         ▼
                   PowerUpMessageUI
```

### Futuro — PENDIENTE DE IMPLEMENTACIÓN

```text
Cliente: Input
    │
    ▼
Solicitud de red
    │
    ▼
Servidor: validación y estado autoritativo
    │
    ▼
Replicación / broadcast
    │
    ├──► Cliente 1
    ├──► Cliente 2
    ├──► Cliente 3
    └──► Cliente 4
```

El proyecto actual no implementa ninguna flecha de este segundo diagrama.

---

## 8. Introducción a cliente-servidor

En un modelo cliente-servidor, los clientes solicitan acciones y el servidor decide el estado válido. Un diseño autoritativo evita que cada cliente invente resultados distintos.

Ejemplo conceptual futuro:

1. Client 2 detecta el botón PowerUp.
2. Envía una solicitud que identifica al jugador y la acción.
3. El servidor comprueba si la acción es válida.
4. El servidor informa a todos los clientes.
5. Cada cliente actualiza su UI.

Movimiento y eventos tienen necesidades distintas. La posición cambia continuamente y necesita actualizaciones frecuentes, mientras que PowerUp puede representarse como un evento discreto.

---

## 9. Preparación de VirtualBox

Una máquina virtual simula otro computador utilizando recursos del host. RAM, CPU y disco asignados a la VM dejan de estar disponibles total o parcialmente para el host mientras la VM está encendida.

La descarga oficial es [Oracle VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads). La versión verificada al redactar esta guía fue 7.2.20. Use la última versión estable 7.2 disponible para el aula y no versiones Beta/RC.

### macOS — Apple Silicon

1. Descargue **macOS / Apple Silicon hosts**.
2. Abra el `.dmg` y ejecute el instalador.
3. Autorice los componentes solicitados por macOS.
4. Reinicie si el instalador lo requiere.
5. Abra VirtualBox y compruebe **Help > About VirtualBox**.

No descargue `macOS / Intel hosts` para un iMac M4.

### Windows — x86-64

1. Descargue **Windows hosts**.
2. Ejecute el instalador como usuario con privilegios de instalación.
3. Mantenga habilitados los componentes de red; Host-Only depende de ellos.
4. Acepte la interrupción breve de red que advierte el instalador.
5. Abra VirtualBox y compruebe **Help > About VirtualBox**.

### CHECKPOINT 2 — VirtualBox instalado

**OBJETIVO:** disponer del hipervisor correcto.  
**PROCEDIMIENTO:** instalar el paquete correspondiente al host.  
**VERIFICACIÓN:** VirtualBox abre sin error y muestra versión 7.2.x.  
**RESULTADO ESPERADO:** aplicación preparada para crear una VM.

---

## 10. Descarga de Debian

Debian estable verificado: **Debian 13 “trixie”**, actualización 13.7. Use una imagen `netinst`: es pequeña y descarga paquetes durante la instalación.

Fuentes oficiales:

- [Información de Debian estable](https://www.debian.org/releases/stable/)
- [Medios oficiales de instalación](https://www.debian.org/CD/)
- [Manual de instalación](https://www.debian.org/releases/stable/installmanual.en.html)

### macOS — Apple Silicon

Descargue la ISO `debian-13.x.x-arm64-netinst.iso` desde el directorio oficial de imágenes **arm64**. No descargue `amd64`: VirtualBox en Apple Silicon no ejecuta guests x86.

### Windows — x86-64

Descargue `debian-13.x.x-amd64-netinst.iso` desde el directorio oficial de imágenes **amd64**.

> [!WARNING]
> Verifique siempre las letras de arquitectura en el nombre del archivo antes de crear la VM.

---

## 11. Creación de la máquina virtual

Configuración recomendada:

| Parámetro | Valor | Explicación |
|---|---:|---|
| Nombre | `Debian-Unity-Server` | Identifica la VM |
| Tipo | Linux / Debian 64-bit | Sistema guest |
| CPU | 2 vCPU | Suficiente para el laboratorio inicial |
| RAM | 4 GB | Cómodo para Debian mínimo y futuro servidor; 2 GB es el mínimo práctico |
| Disco | 25 GB dinámico | Crece al usarlo, hasta el máximo |
| Adaptador 1 | NAT | Permite a Debian salir a Internet |
| Adaptador 2 | Host-Only Network | Comunicación host ↔ guest sin depender de Wi-Fi |

Pasos:

1. Seleccione **New**.
2. Nombre la VM `Debian-Unity-Server`.
3. Seleccione la ISO correcta.
4. Desactive instalación desatendida para seguir manualmente la práctica.
5. Asigne 4096 MB de RAM y 2 CPU sin entrar en la zona roja del indicador.
6. Cree un disco virtual de 25 GB, asignación dinámica.
7. Finalice, pero no inicie todavía.

### Configurar las dos interfaces

1. Abra **File > Tools > Network**.
2. Cree una **Host-Only Network** si no existe.
3. Mantenga DHCP habilitado. Un rango típico de VirtualBox es `192.168.56.0/24`, pero registre el rango real mostrado.
4. Abra **Settings > Network** de la VM.
5. Adapter 1: habilitado, Attached to **NAT**.
6. Adapter 2: habilitado, Attached to **Host-Only Network**.
7. En macOS reciente elija **Host-Only Network**, no la opción heredada Host-Only Adapter.

## 12. Instalación mínima de Debian

1. Inicie la VM.
2. Si se solicita un disco, seleccione la ISO descargada.
3. En el menú elija **Install** o **Graphical install**. Ambos producen el mismo sistema; Graphical install facilita el uso inicial.
4. Seleccione idioma, país y teclado que correspondan al estudiante.
5. Espere la detección de red.
6. Hostname: `unity-server`.
7. Domain name: déjelo vacío para este laboratorio.
8. Cuando se solicite la contraseña de `root`, déjela vacía. El instalador deshabilitará el acceso directo de `root` y permitirá al primer usuario administrar con `sudo`, que es el método usado en esta guía.
9. Cree un usuario normal, por ejemplo `student`. Use una contraseña de laboratorio que no reutilice en otros servicios.
10. Particionado: **Guided — use entire disk**. El “entire disk” es el disco virtual de 25 GB, no el disco físico del host.
11. Seleccione **All files in one partition**.
12. Confirme **Finish partitioning and write changes to disk**.
13. Configure un mirror de Debian cuando el instalador lo solicite.
14. En selección de software:
    - desmarque **Debian desktop environment** y cualquier escritorio;
    - marque **SSH server**;
    - marque **standard system utilities**.
15. Instale GRUB en el disco virtual cuando se solicite.
16. Finalice y reinicie.
17. Si regresa al instalador, apague la VM, retire la ISO de la unidad óptica virtual y vuelva a iniciar.
18. Inicie sesión con el usuario normal.

Una instalación sin escritorio consume menos RAM, disco y CPU. El servidor no necesita ventanas; además, la terminal hace visibles los procesos, puertos y logs que se estudian.

### CHECKPOINT 3 — Debian instalado

**OBJETIVO:** instalar Debian mínimo en el disco virtual.  
**PROCEDIMIENTO:** seguir el instalador y seleccionar SSH + utilidades estándar, sin escritorio.  
**VERIFICACIÓN:** aparece el prompt de login después de reiniciar.  
**RESULTADO ESPERADO:** el usuario puede iniciar sesión y ver un prompt similar a `student@unity-server:~$`.

---

## 13. Primera introducción a la terminal Linux

El prompt no se copia. En `student@unity-server:~$`, el símbolo `$` indica un usuario normal. Los comandos distinguen mayúsculas de minúsculas.

### `pwd`

**QUÉ HACE:** muestra el directorio actual.  
**COMANDO:**

```bash
pwd
```

**EJEMPLO:** `/home/student`

### `ls` y `ls -la`

**QUÉ HACEN:** `ls` lista archivos; `-l` muestra detalles y permisos; `-a` incluye nombres ocultos.

```bash
ls
ls -la
```

### `cd`

**QUÉ HACE:** cambia de directorio. `~` representa el home del usuario y `..` el directorio padre.

```bash
cd ~
cd ..
```

### `mkdir`

**QUÉ HACE:** crea directorios.

```bash
mkdir -p ~/server-build
```

`-p` crea los directorios intermedios necesarios y no falla si ya existen.

### `cp`

**QUÉ HACE:** copia. `-r` copia un directorio y su contenido.

```bash
cp archivo.txt copia.txt
cp -r carpeta carpeta-copia
```

### `mv`

**QUÉ HACE:** mueve o renombra.

```bash
mv nombre-antiguo.txt nombre-nuevo.txt
```

### `rm`

**QUÉ HACE:** elimina archivos. La terminal normalmente no ofrece papelera.

```bash
rm archivo-temporal.txt
```

> [!WARNING]
> `rm` es destructivo. Compruebe `pwd` y `ls` antes de usarlo. No use `rm -rf` en esta práctica.

### `cat`

**QUÉ HACE:** imprime el contenido de un archivo de texto; es útil para logs pequeños.

```bash
cat archivo.log
```

### `clear`

**QUÉ HACE:** limpia visualmente la terminal; no borra archivos ni historial.

```bash
clear
```

### `whoami`, `hostname` y `uname`

```bash
whoami
hostname
uname -m
```

- `whoami`: usuario actual.
- `hostname`: nombre de la máquina.
- `uname -m`: arquitectura. Debe mostrar `aarch64` en Debian ARM64 o `x86_64` en Debian amd64.

### `ip`

**QUÉ HACE:** consulta/configura red. En la práctica solo se usa para leer información.

```bash
ip -br addr
ip route
```

`-br` produce una salida breve; `addr` muestra direcciones. `ip route` indica rutas, incluida la salida predeterminada a Internet.

### `ping`

**QUÉ HACE:** envía mensajes ICMP para comprobar alcance. `-c 4` envía cuatro y termina.

```bash
ping -c 4 1.1.1.1
```

### `chmod`

**QUÉ HACE:** cambia permisos.

```bash
chmod +x <EJECUTABLE_REAL>
```

`+x` añade permiso de ejecución. No use `chmod 777`.

### `ps`, `pgrep` y `kill`

```bash
ps -ef
pgrep -af <NOMBRE_REAL>
kill <PID>
```

- `ps -ef`: fotografía de procesos.
- `pgrep -af`: busca por nombre y muestra argumentos.
- `kill PID`: solicita una terminación normal. Evite `kill -9` salvo diagnóstico avanzado.

### `sudo`

**QUÉ HACE:** ejecuta un único comando administrativo. Solicita la contraseña del usuario.

```bash
sudo apt update
```

No trabaje permanentemente como `root`. Use `sudo` solo para paquetes, servicios o firewall.

### `apt`

**QUÉ HACE:** instala y actualiza paquetes desde repositorios configurados.

```bash
sudo apt update
sudo apt upgrade
```

- **Repositorio:** servidor que publica paquetes firmados.
- **Índice:** catálogo local de versiones disponibles.
- **Paquete:** archivo instalable de software y metadatos.
- `apt update`: actualiza el índice; no actualiza todavía los programas.
- `apt upgrade`: instala versiones más nuevas de paquetes ya instalados.

Revise la lista antes de confirmar con `Y`.

### `systemctl`

**QUÉ HACE:** consulta y controla servicios gestionados por systemd.

```bash
sudo systemctl status ssh
sudo systemctl enable --now ssh
```

- `status`: muestra estado y logs recientes.
- `enable`: programa inicio automático.
- `--now`: además lo inicia inmediatamente.

### CHECKPOINT 4 — Linux operativo

**OBJETIVO:** comprobar usuario, hostname, arquitectura y paquetes.  
**PROCEDIMIENTO:** ejecutar `whoami`, `hostname`, `uname -m`, `sudo apt update` y `sudo apt upgrade`.  
**VERIFICACIÓN:** no hay errores de repositorio y la arquitectura coincide con la ISO elegida.  
**RESULTADO ESPERADO:** Debian actualizado y estudiante capaz de navegar la terminal.

---

## 14. Configuración de red

### 14.1 Vocabulario

- **IP:** dirección de una interfaz dentro de una red.
- **Puerto:** número que permite dirigir tráfico a un proceso concreto en una IP.
- **127.0.0.1 / localhost:** loopback; siempre significa “esta misma máquina/proceso de sistema operativo”.
- **Adaptador virtual:** tarjeta de red que VirtualBox presenta a Debian.
- **NAT:** permite que la VM salga a Internet; por defecto no facilita que el host inicie conexiones directas al guest.
- **Host-Only:** red privada entre host y VMs, independiente del Wi-Fi.
- **Bridged:** coloca la VM en la red física; depende de políticas del aula y no es la opción principal.
- **Firewall:** reglas que permiten o bloquean tráfico.

### 14.2 Diseño recomendado

```text
                           Internet
                               ▲
                               │ Adapter 1: NAT
HOST macOS/Windows             │
┌──────────────────────┐   ┌───┴───────────────┐
│ Unity / Terminal     │   │ Debian VM         │
│ Host-Only IP         ├───┤ Host-Only IP      │
└──────────────────────┘   └───────────────────┘
        Adapter 2: Host-Only Network
```

NAT se usa para `apt`. Host-Only se usa para SSH y, en el futuro, para tráfico del juego. Esta combinación evita depender de Wi-Fi y no expone el servidor al resto del aula.

### 14.3 Encontrar la IP de Debian

```bash
ip -br addr
```

Ejemplo ilustrativo, no valores garantizados:

```text
lo       UNKNOWN  127.0.0.1/8
enp0s3   UP       10.0.2.15/24
enp0s8   UP       192.168.56.101/24
```

- `lo` es localhost.
- `enp0s3` suele corresponder a NAT.
- `enp0s8` suele corresponder a Host-Only.
- Use la IP Host-Only, en este ejemplo `192.168.56.101`, para conexiones desde el host.

Los nombres e IP pueden variar. Confirme también:

```bash
ip route
```

### macOS — comprobar comunicación

Abra Terminal en macOS:

```bash
ping -c 4 <IP_VM>
```

### Windows — comprobar comunicación

Abra PowerShell:

```powershell
ping <IP_VM>
```

En Windows `ping` envía cuatro solicitudes por defecto.

### Por qué Unity no debe usar localhost

Si Unity corre en macOS/Windows, `127.0.0.1` apunta al host. El servidor corre en Debian, otro sistema operativo con su propia interfaz loopback. Unity deberá usar la IP Host-Only de Debian.

### ACTIVIDAD — mapa de red

Sin copiar los ejemplos, registre:

1. nombre de la interfaz NAT;
2. IP NAT;
3. nombre de la interfaz Host-Only;
4. IP Host-Only;
5. ruta predeterminada;
6. resultado del ping desde el host.

### CHECKPOINT 5 — Red host ↔ VM funcionando

**OBJETIVO:** comunicación independiente del Wi-Fi.  
**PROCEDIMIENTO:** identificar IP Host-Only y ejecutar ping desde el host.  
**VERIFICACIÓN:** se reciben respuestas sin pérdida sostenida.  
**RESULTADO ESPERADO:** el host alcanza la IP privada de Debian.

---

## 15. Preparación de SSH

SSH crea una terminal cifrada hacia otra máquina. Así puede controlar Debian desde Terminal o PowerShell sin trabajar en la pequeña consola de VirtualBox. `scp` utiliza SSH para transferir archivos.

Si “SSH server” fue seleccionado durante la instalación, ya debe existir. Para asegurar el paquete:

```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

Busque `active (running)`. Presione `q` para salir de la vista de estado.

Compruebe el puerto SSH estándar:

```bash
sudo ss -lntp | grep ':22'
```

### macOS — conexión

```bash
ssh student@<IP_VM>
```

### Windows — conexión

PowerShell moderno incluye cliente OpenSSH:

```powershell
ssh student@<IP_VM>
```

La primera vez, SSH pregunta si confía en la huella de la VM. Compare la IP, escriba `yes` y luego la contraseña. La contraseña no muestra asteriscos mientras se escribe; es normal.

Para cerrar:

```bash
exit
```

### CHECKPOINT 6 — SSH funcionando

**OBJETIVO:** administrar Debian desde el host.  
**PROCEDIMIENTO:** comprobar servicio y conectar con `ssh`.  
**VERIFICACIÓN:** `hostname` ejecutado dentro de SSH devuelve `unity-server`.  
**RESULTADO ESPERADO:** terminal remota funcional.

---

## 16. Unity Dedicated Server

### 16.1 Concepto

```text
Proyecto Unity
├── Client build: input, cámara, render y UI
└── Dedicated Server build: simulación y networking, sin jugador local
```

El servidor futuro debería recibir solicitudes, validar reglas, mantener el estado autoritativo y replicarlo. No necesita dibujar la escena ni reproducir efectos visuales.

### 16.2 Estado real

**YA DISPONIBLE:** el módulo `Linux Dedicated Server Build Support` está instalado en el MacBook inspeccionado.  
**NO IMPLEMENTADO:** no hay lógica de servidor, transporte, Build Profile, ejecutable ni configuración de IP/puerto.

El módulo permite compilar, pero no convierte automáticamente gameplay local en multiplayer.

### 16.3 Procedimiento futuro en Unity 6000.6

> [!CAUTION]
> No realice todavía este build esperando un servidor funcional. Estos pasos se habilitan después de implementar NGO y definir escenas/roles de servidor.

La interfaz correcta de Unity 6 usa **Build Profiles**:

1. **File > Build Profiles**.
2. **Add Build Profile**.
3. Seleccionar **Linux Server**.
4. Si el módulo falta en otro computador, usar **Install with Unity Hub**.
5. **Switch Profile**.
6. Confirmar que la escena de servidor correcta esté incluida.
7. Seleccionar un directorio de salida conocido.
8. Presionar **Build**.

Referencia: [Unity — Build your application for Dedicated Server](https://docs.unity3d.com/6000.0/Documentation/Manual/dedicated-server-build.html).

No se proporciona un nombre de ejecutable porque todavía no existe uno. El futuro estudiante debe registrarlo observando el directorio generado.

### 16.4 Matriz de viabilidad

| Entorno | Debian guest | Unity Linux Server estándar | Estado |
|---|---|---|---|
| macOS Apple Silicon + VirtualBox | ARM64 | x64 | Bloqueado por arquitectura |
| Windows x86-64 + VirtualBox | amd64 | x64 | Arquitectura compatible; proyecto aún pendiente |

---

## 17. Transferencia del futuro build con `scp`

**MÉTODO PRINCIPAL:** `scp`, porque usa el SSH ya configurado y funciona igual conceptualmente en macOS y Windows. Shared Folders requeriría Guest Additions y más configuración.

### macOS — Apple Silicon

Ejemplo de sintaxis, no ruta real:

```bash
scp -r "/ruta/real/ServerBuild" student@<IP_VM>:/home/student/
```

### Windows — x86-64

```powershell
scp -r "C:\ruta\real\ServerBuild" student@<IP_VM>:/home/student/
```

Partes:

- `scp`: copia mediante SSH;
- `-r`: copia directorio completo;
- primer argumento: origen en el host;
- `student`: usuario de Debian;
- `<IP_VM>`: IP Host-Only observada;
- `/home/student/`: destino en Debian.

Verificación futura en Debian:

```bash
ls -la /home/student/ServerBuild
```

### CHECKPOINT 7 — Dedicated Server transferido

**ESTADO ACTUAL:** `PENDIENTE DE IMPLEMENTACIÓN`.  
**OBJETIVO:** copiar un build real y completo.  
**PROCEDIMIENTO:** generar el build futuro, usar `scp -r` y listar el destino.  
**VERIFICACIÓN:** ejecutable, carpeta de datos y bibliotecas aparecen en Debian.  
**RESULTADO ESPERADO:** copia íntegra; hoy no puede completarse porque no existe build.

---

## 18. Permisos y ejecución futura

Linux exige que el archivo tenga permiso de ejecución.

```bash
cd /home/student/ServerBuild
ls -l
chmod +x <NOMBRE_EJECUTABLE_REAL>
ls -l <NOMBRE_EJECUTABLE_REAL>
```

En la salida de `ls -l`, una `x` indica permiso de ejecución, por ejemplo `-rwxr-xr-x`.

No use `sudo` para ejecutar el servidor ni `chmod 777`.

Comando de inicio futuro:

```bash
./<NOMBRE_EJECUTABLE_REAL>
```

`./` significa “ejecutar el archivo ubicado en el directorio actual”. No se añaden argumentos de IP/puerto porque el proyecto actual no implementa ninguno.

### CHECKPOINT 8 — Servidor ejecutándose

**ESTADO ACTUAL:** `PENDIENTE DE IMPLEMENTACIÓN`; en Apple Silicon además está bloqueado por arquitectura.  
**OBJETIVO:** iniciar el ejecutable real.  
**PROCEDIMIENTO:** asignar `+x` y ejecutar desde su directorio.  
**VERIFICACIÓN:** el proceso permanece activo y produce logs sin error fatal.  
**RESULTADO ESPERADO:** servidor esperando conexiones; no disponible hoy.

---

## 19. Verificación del futuro servidor

### Proceso

```bash
pgrep -af <NOMBRE_EJECUTABLE_REAL>
```

Debe mostrar un PID y la línea de comando.

### Puerto

```bash
sudo ss -lntup
```

- `-l`: sockets en escucha;
- `-n`: números, sin traducir nombres;
- `-t`: TCP;
- `-u`: UDP;
- `-p`: proceso asociado.

El transporte de juego futuro definirá protocolo y puerto. No busque `7777` salvo que la implementación futura confirme ese valor.

### Logs

Observe la salida de la terminal o el archivo de log que produzca el build. Si hay un log pequeño:

```bash
cat <RUTA_REAL_DEL_LOG>
```

### ACTIVIDAD — proceso y puerto

Cuando exista el servidor:

1. anote el PID;
2. identifique protocolo TCP/UDP;
3. identifique puerto real;
4. copie una línea de log que indique inicio;
5. explique por qué un proceso visible no garantiza por sí solo que escucha red.

---

## 20. Configuración futura de clientes Unity

**PENDIENTE DE IMPLEMENTACIÓN EN EL PROYECTO DOCENTE.**

Actualmente no hay campos **Server IP** o **Server Port**, ni código que configure un transporte. No escriba la IP en ningún componente inventado.

Después de implementar NGO, la guía deberá actualizarse con:

1. nombre real del componente/UI que recibe IP;
2. componente de transporte real;
3. puerto real y protocolo;
4. procedimiento para iniciar cliente;
5. logs de conexión esperados.

Ejemplo puramente conceptual:

```text
Server IP   = 192.168.56.x   (IP Host-Only de Debian)
Server Port = <PUERTO_REAL>
```

### CHECKPOINT 9 — Primer cliente conectado

**ESTADO ACTUAL:** `PENDIENTE DE IMPLEMENTACIÓN`.  
**OBJETIVO:** conectar un cliente al endpoint real.  
**PROCEDIMIENTO:** introducir IP/puerto en la futura UI y pulsar el futuro control de conexión.  
**VERIFICACIÓN:** logs de cliente y servidor confirman una conexión.  
**RESULTADO ESPERADO:** un cliente registrado; imposible con el baseline local.

---

## 21. Multiplayer Play Mode 3.0

Multiplayer Play Mode (MPPM) ejecuta varias instancias locales para acelerar pruebas. En este proyecto el paquete 3.0.0 está instalado y Unity 6000.6 cumple sus requisitos, pero no existe un escenario configurado.

### Qué puede hacerse ahora

Puede abrir **Window > Play Mode > Scenarios**, seleccionar **Configure play mode scenarios**, pulsar `+` y estudiar las opciones. No lo interprete como networking: cada instancia cargaría el baseline que ya contiene cuatro jugadores locales.

### Uso futuro correcto

1. Abrir **Window > Play Mode > Scenarios**.
2. Crear un escenario.
3. Mantener el Editor principal y añadir hasta tres **Additional Editor Instances** para obtener cuatro Players de Editor en total.
4. Configurar cada instancia con el Build Profile/rol futuro apropiado.
5. Activar **Stream Logs to Main Editor** si se desean logs centralizados.
6. Entrar en Play Mode para lanzar el escenario.

MPPM 3.0 soporta hasta cuatro Players de Editor en total y también instancias locales construidas. Documentación: [Multiplayer Play Mode 3.0](https://docs.unity3d.com/Packages/com.unity.multiplayer.playmode@3.0/manual/index.html).

> [!IMPORTANT]
> MPPM no crea `NetworkManager`, ownership o transporte. Solo orquesta instancias del juego que ya debe saber conectarse.

### CHECKPOINT 10 — Cuatro clientes conectados

**ESTADO ACTUAL:** `PENDIENTE DE IMPLEMENTACIÓN`.  
**OBJETIVO:** cuatro procesos cliente conectados al mismo servidor.  
**PROCEDIMIENTO:** configurar un escenario futuro con cuatro instancias y endpoint común.  
**VERIFICACIÓN:** el servidor registra cuatro conexiones distintas.  
**RESULTADO ESPERADO:** cuatro clientes; no confundir con los cuatro jugadores locales actuales.

---

## 22. Prueba futura de movimiento

El baseline demuestra movimiento local, no ownership ni replicación.

La fase NGO deberá probar:

1. cada cliente controla solo su Player;
2. el input se envía según el modelo de autoridad elegido;
3. el servidor acepta/valida movimiento;
4. los demás clientes observan la posición;
5. desconectar un cliente no entrega control indebido a otro.

### CHECKPOINT 11 — Movimiento sincronizado

**ESTADO ACTUAL:** `PENDIENTE DE IMPLEMENTACIÓN`.  
**OBJETIVO:** observar el mismo estado desde todos los clientes.  
**PROCEDIMIENTO:** mover un cliente cada vez y comparar las cuatro ventanas.  
**VERIFICACIÓN:** solo el owner origina su movimiento y todos reciben el resultado.  
**RESULTADO ESPERADO:** posiciones consistentes; hoy solo existen `Transform` locales.

---

## 23. Prueba futura del PowerUp

### Flujo actual real

```text
Player 2 + Right Ctrl
        │
        ▼
PlayerInputSource (local)
        │
        ▼
PlayerPowerUp
        │
        ▼
PowerUpEvents
        │
        ▼
UI local: "Player 2 activated PowerUp"
```

No pasa por servidor y otros procesos no reciben el evento.

### Flujo futuro esperado, aún no implementado

```text
Cliente owner
    │ solicitud
    ▼
Servidor valida
    │ broadcast
    ├──► Cliente 1 UI
    ├──► Cliente 2 UI
    ├──► Cliente 3 UI
    └──► Cliente 4 UI
```

### CHECKPOINT 12 — PowerUp comunicado correctamente

**ESTADO ACTUAL:** `PENDIENTE DE IMPLEMENTACIÓN`.  
**OBJETIVO:** un evento validado por servidor visible en todos los clientes.  
**PROCEDIMIENTO:** activar el binding del owner y observar logs/UI.  
**VERIFICACIÓN:** mensaje idéntico y jugador correcto en cuatro clientes durante ~2 s.  
**RESULTADO ESPERADO:** broadcast único, sin duplicados; hoy el evento es local.

---

## 24. Diagnóstico de problemas

| Problema | Posible causa | Comando/verificación | Solución segura |
|---|---|---|---|
| VM no inicia | ISO/arquitectura incorrecta | Revise nombre `arm64` o `amd64`; `uname -m` si logra iniciar | Descargue ISO que coincida con el host; no intente guest x86 en Mac ARM |
| VM no inicia | Virtualización deshabilitada en Windows | Task Manager > Performance > CPU > Virtualization | Habilite virtualización en BIOS/UEFI con apoyo docente |
| Debian no tiene Internet | Adapter 1/NAT desconectado | `ip -br addr`, `ip route`, `ping -c 4 1.1.1.1` | Habilite Adapter 1 NAT y “Cable connected” |
| No conozco la IP | Se observa interfaz equivocada | `ip -br addr` | Identifique la interfaz Host-Only, no `lo` ni solo NAT |
| Ping host↔VM falla | Adapter 2 ausente o DHCP sin dirección | `ip -br addr`; revisar Settings > Network | Habilite Host-Only Network y DHCP; reinicie la VM si hace falta |
| SSH no conecta | Servicio detenido | `sudo systemctl status ssh` | `sudo systemctl enable --now ssh` |
| SSH no conecta | IP incorrecta | `ip -br addr` | Use IP Host-Only actual |
| `Permission denied` al ejecutar | Falta permiso `x` | `ls -l <archivo>` | `chmod +x <archivo>` |
| `Permission denied` en SSH | Usuario/contraseña incorrectos | `whoami`; revise comando | Use usuario creado en Debian; no active root SSH |
| Servidor no ejecuta en Mac M4 VM | Binario Linux x64 dentro de Debian ARM64 | `uname -m`; `file <ejecutable>` | Limitación de arquitectura; use entorno x64 compatible definido por docente |
| Servidor cierra inmediatamente | Error de runtime o proyecto | ejecutar en foreground y leer salida | Copie el error completo; no oculte logs |
| Puerto no aparece | Servidor no abrió transporte | `pgrep -af ...`; `sudo ss -lntup` | Verifique proceso, configuración y logs futuros |
| Unity no conecta | NGO/transporte aún ausentes | Package Manager, jerarquía, logs | En este baseline es esperado; espere fase NGO |
| Unity no conecta | IP/puerto futuros incorrectos | comparar UI futura con `ip -br addr` y `ss` | Use IP Host-Only y puerto real |
| Un cliente conecta, otro no | Escenario/ID/puerto o límite | logs por instancia y servidor | Comparar logs; no reiniciar todo sin identificar la instancia |
| Movimiento no aparece en otros | Solo se modifica `Transform` local | inspeccionar componente real | Requiere sincronización NGO futura |
| PowerUp no aparece en otros | `PowerUpEvents` es local | revisar flujo actual | Requiere request + validación + broadcast futuros |
| Firewall bloquea puerto | Regla local futura | `sudo nft list ruleset`; `ss` | Añada solo una regla específica cuando se conozcan protocolo/puerto; no desactive permanentemente firewall |
| `apt update` falla | NAT/DNS/reloj | `ip route`; `ping -c 4 1.1.1.1`; `ping -c 4 debian.org` | Separe problema de conectividad y DNS antes de cambiar repositorios |
| MPPM abre instancias pero no conecta | Orquestación sin networking | revisar que no existe NetworkManager | Es esperado hasta implementar NGO |

---

## 25. Comparación conceptual cliente/servidor

| Responsabilidad | Cliente | Servidor futuro |
|---|---|---|
| Leer teclado | Sí | No |
| Mostrar cámara/UI | Sí | No es necesario |
| Solicitar movimiento/PowerUp | Sí | Recibe |
| Validar reglas | No debería decidir en solitario | Sí |
| Mantener estado autoritativo | Copia/presentación | Sí |
| Replicar resultados | Recibe | Envía |

El baseline actual combina todo localmente y no tiene estas fronteras de proceso.

---

## 26. Actividades para el estudiante

### ACTIVIDAD A — Trazar gameplay

Dibuje dos secuencias con nombres reales de clases:

1. tecla de movimiento hasta `Transform.position`;
2. tecla PowerUp hasta el texto de UI.

### ACTIVIDAD B — Inventario de estado

Clasifique como implementado o pendiente: Input System, MPPM, NGO, NFE, Player prefab, Dedicated Server, IP, puerto, movimiento local, movimiento replicado y PowerUp broadcast.

### ACTIVIDAD C — Arquitectura

Ejecute `uname -m` en Debian y explique si un binario Linux x64 puede ejecutarse de forma nativa en esa VM.

### ACTIVIDAD D — Red

Identifique la IP Host-Only sin usar el ejemplo de esta guía. Justifique por qué no eligió `127.0.0.1` ni necesariamente la IP NAT.

### ACTIVIDAD E — Servicios

Demuestre con dos verificaciones diferentes que SSH funciona: estado de systemd y socket en escucha.

### ACTIVIDAD F — Futuro servidor

Cuando exista, identifique proceso, PID, protocolo, puerto y línea de log inicial. No use valores proporcionados por otro grupo.

---

## 27. Preguntas de análisis

1. ¿Por qué Unity en el host no puede usar simplemente `localhost` para llegar a Debian?
2. ¿Cuál es la diferencia entre host y guest?
3. ¿Qué función cumple un puerto además de la IP?
4. ¿Por qué se usan dos adaptadores virtuales?
5. ¿Qué ocurriría con los clientes si el servidor se cierra?
6. ¿Quién debería mantener el estado autoritativo del juego?
7. ¿Qué diferencia existe entre cliente y servidor?
8. ¿Por qué un Dedicated Server no necesita renderizar la escena?
9. ¿Qué información mínima debería enviarse para representar movimiento?
10. ¿Qué diferencia existe entre enviar PowerUp como evento y sincronizar continuamente una posición?
11. ¿Qué ventajas ofrece un servidor Linux mínimo?
12. ¿Por qué `PlayerController` no contiene teclas concretas?
13. ¿Qué ventaja aporta `PowerUpEvents` para cambiar después la fuente del evento?
14. ¿Por qué cuatro Players locales no equivalen a cuatro clientes de red?
15. ¿Por qué MPPM no reemplaza NGO o un transporte?
16. ¿Qué demuestra `ss` que `ps` no demuestra?
17. ¿Por qué Debian ARM64 es correcto para VirtualBox en M4 pero incorrecto para el Server Player Linux x64 estándar?
18. ¿Qué riesgo existe al usar Debian cuando Unity declara soporte oficial de servidor para Ubuntu AMD64?
19. ¿Por qué no es buena práctica usar `chmod 777`?
20. ¿Qué dato real debe existir antes de abrir una regla de firewall?

---

## 28. Evidencias a entregar

### Parte disponible ahora

1. captura de `LocalGameplayBaseline` en Play Mode;
2. tabla con componentes reales y responsabilidades;
3. captura de VirtualBox con la VM creada;
4. captura del login de Debian;
5. salida de `uname -m`;
6. salida de `ip -br addr`, ocultando información ajena si la hubiera;
7. ping host ↔ VM;
8. `systemctl status ssh` mostrando servicio activo;
9. sesión SSH desde macOS Terminal o Windows PowerShell;
10. respuestas a preguntas de análisis.

### Parte futura, después de NGO

11. build de servidor transferido;
12. `ls -l` con permiso de ejecución;
13. proceso del servidor;
14. puerto real en `ss`;
15. cuatro clientes conectados;
16. movimiento replicado;
17. PowerUp visible en cuatro clientes;
18. logs que relacionen cliente y servidor.

No entregue capturas simuladas de checkpoints pendientes.

---

## 29. Seguridad y buenas prácticas

- Use un usuario normal y `sudo` solo cuando sea necesario.
- No habilite login SSH de root.
- No desactive permanentemente el firewall.
- No abra “todos los puertos”. Espere a conocer protocolo y puerto reales.
- No use `chmod 777`.
- No copie comandos destructivos sin comprender ruta y efecto.
- Mantenga Host-Only para el tráfico del laboratorio; evita exposición innecesaria a la LAN.
- Actualice Debian antes de instalar servicios.
- Verifique arquitectura con `uname -m` y binarios con `file <archivo>`.
- Detenga procesos con `kill PID` antes de recurrir a señales forzadas.
- No publique contraseñas, IP externas o logs con tokens.

---

## 30. Cierre de la práctica

El proyecto demuestra un baseline local correctamente desacoplado: Input System alimenta movimiento y PowerUp; el evento de gameplay alimenta UI. La infraestructura de red aún no existe.

La parte Linux enseña virtualización, arquitectura, terminal, paquetes, red y SSH. En Windows x86-64 deja preparado un guest compatible en CPU con un futuro servidor Linux x64. En Apple Silicon deja preparado un guest ARM64 útil para Linux y redes, pero no para ejecutar el Dedicated Server Linux x64 estándar; el docente debe resolver esa incompatibilidad antes del checkpoint 7.

El siguiente trabajo de implementación del proyecto es NGO. Solo después deben definirse Player prefab de red, ownership, `NetworkManager`, transporte, IP, puerto, Build Profile, servidor y escenario MPPM. NFE permanece para una fase posterior.

---

## Apéndice A — Resumen de checkpoints

| Checkpoint | Estado con el proyecto actual |
|---|---|
| 1. Proyecto Unity comprendido | Disponible |
| 2. VirtualBox instalado | Disponible |
| 3. Debian instalado | Disponible |
| 4. Linux operativo | Disponible |
| 5. Red host ↔ VM | Disponible |
| 6. SSH funcionando | Disponible |
| 7. Dedicated Server transferido | Pendiente; no existe build |
| 8. Servidor ejecutándose | Pendiente; bloqueado en VM ARM64 de Mac M4 |
| 9. Primer cliente conectado | Pendiente; no existe networking |
| 10. Cuatro clientes conectados | Pendiente; MPPM no está configurado y no existe networking |
| 11. Movimiento sincronizado | Pendiente; movimiento es local |
| 12. PowerUp comunicado | Pendiente; evento es local |

## Apéndice B — Fuentes oficiales verificadas

- [Unity 6 — System requirements](https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html)
- [Unity 6 — Dedicated Server build](https://docs.unity3d.com/6000.0/Documentation/Manual/dedicated-server-build.html)
- [Unity — Multiplayer Play Mode 3.0](https://docs.unity3d.com/Packages/com.unity.multiplayer.playmode@3.0/manual/index.html)
- [Oracle VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads)
- [Oracle VirtualBox 7.2 User Manual](https://download.virtualbox.org/virtualbox/7.2.20/UserManual.pdf)
- [Debian stable release](https://www.debian.org/releases/stable/)
- [Debian installation media](https://www.debian.org/CD/)
- [Debian Installation Guide](https://www.debian.org/releases/stable/installmanual.en.html)
- [Debian Reference](https://www.debian.org/doc/manuals/debian-reference/)
