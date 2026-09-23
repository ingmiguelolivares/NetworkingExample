# Unity Multiplayer Networking Lab Starter Project

This repository is the teaching starter for comparing Netcode for GameObjects (NGO) and Netcode for Entities (NFE). It preserves the verified local gameplay and adds the scenes, prefabs, packages, connection panels, ECS components, Ghost configuration, and extension points that students use to complete client-server gameplay.

The project is intentionally incomplete. Seven unique `STUDENT TODO` identifiers define the programming lab: NGO movement input, NGO server movement, NGO PowerUp RPC, NFE listen/connect, NFE GoInGame and spawn, NFE predicted movement, and NFE PowerUp RPC.

## Open and run

- Unity: **6000.6.0f1**.
- Render pipeline: **URP 17.6.0**.
- Input System: **1.20.0**.
- Multiplayer Play Mode: **3.0.0**.
- Local reference: `Assets/Scenes/LocalGameplayBaseline.unity`.
- NGO starter: `Assets/Scenes/NGOGameplay.unity`, UDP **7979**.
- NFE starter: `Assets/Scenes/NFEGameplay.unity`, UDP **7980**.

Open the local baseline first and verify the four keyboard-controlled players and the PowerUp message. Then use the Word guide in `Docs/GUIA_LAB_UNITY_NETWORKING_LINUX.docx` for the NGO, NFE, Linux, container, Kubernetes, and Agones activities.

## Local controls

| Player | Movement | PowerUp |
|---|---|---|
| Player 1 | W A S D | Space |
| Player 2 | Arrow keys | Right Ctrl |
| Player 3 | I J K L | O |
| Player 4 | Numpad 8, 4, 5, 6 | Numpad 0 |

## Teaching boundary

Included now:

- framework-neutral local gameplay;
- NGO `NetworkManager`, `UnityTransport`, network Player prefab, identity, connection UI, and extension code;
- NFE client/server Worlds, ECS components, systems, Ghost prefab, SubScene, connection UI, and presentation bridge;
- editable Address and Port fields;
- reference Dockerfiles, Minikube/Agones scripts, and GameServer manifests;
- the complete student lab guide.

Student work:

- complete the seven `STUDENT TODO` activities;
- create Linux Dedicated Server builds;
- prepare Debian and host-only networking;
- build the server container;
- install Minikube and Agones;
- integrate the Agones lifecycle;
- deploy a GameServer and connect four clients.

No Dedicated Server build, VM, container image, Kubernetes cluster, or Agones deployment is generated or executed in this starter.

## Architecture limitation

The current Unity Linux Server target produces x86-64 executables. A native VirtualBox guest on Apple Silicon is ARM64 and cannot run that executable natively. Windows x86-64 with Debian amd64 has matching CPU architecture. The guide marks this limitation and requires an instructor-approved ARM64 server artifact or x86-64 environment for the Apple Silicon end-to-end checkpoint.
