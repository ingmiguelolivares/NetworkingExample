# Unity Multiplayer Networking Lab — Local Gameplay Baseline

This project provides the framework-neutral gameplay used in class to compare Netcode for GameObjects (NGO) and Netcode for Entities (NFE). Its current state is **LOCAL BASELINE**: no networking framework is implemented.

## Open and run

- Unity version: **6000.6.0f1**.
- Render pipeline: **Universal Render Pipeline (URP) 17.6.0**.
- Open this folder in Unity Hub or Unity Editor.
- Open `Assets/Scenes/LocalGameplayBaseline.unity` and enter Play Mode.

## Gameplay and controls

Four colored local players move across the ground plane. Movement uses Unity Input System action maps stored in `Assets/Input/LocalPlayers.inputactions`, so bindings can be edited without changing `PlayerController`.

| Player | Movement | PowerUp |
|---|---|---|
| Player 1 | W A S D | Space |
| Player 2 | Arrow keys | Right Ctrl |
| Player 3 | I J K L | O |
| Player 4 | Numpad 8, 4, 5, 6 | Numpad 0 |

PowerUp activation is local and intentionally has no gameplay effect. It follows `Input → ActivatePowerUp() → gameplay event → UI`. The UI shows `Player N activated PowerUp` for approximately two seconds.

## Structure

```text
Assets/
  Input/                 Configurable Input System action maps
  Scenes/                LocalGameplayBaseline scene
  Scripts/
    Core/                Reserved for shared framework-neutral code
    Player/              Input adapter and movement
    PowerUp/             Activation and gameplay event
    UI/                  PowerUp message presentation
    Editor/              Deterministic scene builder
  Tests/PlayMode/        Automated baseline checks
```

The gameplay assembly does not reference NGO, NFE, RPCs, network objects, ghosts, authority, ownership, prediction, or synchronization.

## Planned teaching phases

After this baseline is validated, separate adapters will be added for NGO and then NFE while preserving the same observable gameplay. A later phase will run clients on the MacBook Pro and a Unity Dedicated Server in a Linux VirtualBox VM. None of those networking or server features are present yet.

Multiplayer Play Mode **3.0.0 is installed and available**, but is not used by this local baseline. It is reserved for a later networking phase.
