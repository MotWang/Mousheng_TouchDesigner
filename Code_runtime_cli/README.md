# td-cli

TouchDesigner CLI for LLM agents, artists, and terminal-driven workflows.

`td-cli` connects a live TouchDesigner project to the terminal. It is useful in two modes at the same time:

- as a command surface for LLM agents such as Codex or Claude
- as a practical live-control tool for artists who want to inspect, build, and tweak TouchDesigner projects without clicking through every network manually

## Relative to Original Download: What Was Optimized

Yes. This working version is optimized beyond the initial downloaded baseline. The main upgrades are:

- Agent loop support: added a harness surface for structured observe/apply/verify/history/rollback flows (`harness` routes and CLI commands).
- Reliability fixes: fixed multiple runtime/path issues including `disconnect`, `ops delete`, docs lookup, timeline handlers, and verify output behavior.
- FeedbackTOP correctness: iterated and finalized the safe FeedbackTOP pattern (wiring + `par.top` semantics) to prevent cook-loop and unstable feedback setups.
- Live workflow acceleration: added POP audio-visual scaffold generation (`td-cli pop av`) for faster scene bootstrapping in live sessions.
- Ink pipeline quality: introduced and tuned ripple/ink behavior (velocity-gated OSC, diffusion/noise warp, visible composite decoupling, RGB blow-up prevention).
- Integration and docs quality: upgraded `CLAUDE.md`, refreshed connector/tox session state, and improved guidance for practical artist + agent collaboration.

### Optimization Method

The optimization process was iterative and session-driven:

1. Run in real TouchDesigner sessions.
2. Reproduce pain points or visual defects.
3. Patch CLI routes/handlers and TD-side logic.
4. Re-verify with screenshot/observe workflows.
5. Document stable patterns in README and guidance files.

## English

`td-cli` is an execution layer for a running TouchDesigner session. It can inspect operators, change parameters, read and write DATs, export snapshots, apply shader templates, and execute Python inside TouchDesigner.

### What This Is Good For

- inspect a live TD scene from the terminal
- build or patch operators without hunting through the network editor
- iterate on Python DATs and GLSL shaders from local files
- automate repetitive setup tasks with an LLM or shell scripts
- give artists a recoverable workflow with backups and audit logs

### How It Works

```text
Artist / LLM / Terminal
          |
          v
td-cli (Go binary)
          |
          v
HTTP on port 9500
          |
          v
TouchDesigner Web Server DAT + Python handler
```

The TouchDesigner side writes heartbeat files to `~/.td-cli/instances/`, and `td-cli` uses those files to auto-discover running projects.

In an agent workflow, the model is the reasoning layer and `td-cli` is the execution layer.

Security note: if you set `TD_CLI_TOKEN` in both the shell running `td-cli` and the TouchDesigner process environment before launch, the server will require that shared token on every HTTP request.

### Artist Workflow

Think of `td-cli` as a live studio assistant for TouchDesigner:

1. Find the running project.
2. Inspect the current network or parameters.
3. Create or patch operators.
4. Make the result visible in a container, window, or screenshot.
5. Iterate quickly, and fall back with backups if needed.

Typical live workflow:

```powershell
td-cli status
td-cli ops list /project1 --depth 2
td-cli ops create noiseTOP /project1 --name myNoise
td-cli par get /project1/myNoise
td-cli par set /project1/myNoise period 4 amp 0.35
td-cli screenshot /project1/myNoise -o noise.png
```

### Visual Output Workflow

Creating a TOP or GLSL network is only part of the job. You still need to route it somewhere visible.

Common options:

- assign the result to a container's `Background TOP`
- point a viewer or window at a COMP
- save the result with `td-cli screenshot`

Example:

```powershell
td-cli par set /project1/myContainer top ./out1
td-cli screenshot /project1/myContainer/out1 -o frame.png
```

Important: for OP-reference parameters such as `top`, `opviewer`, `pixeldat`, `component`, or `winop`, prefer local relative paths like `./out1`. The handler will normalize resolvable local targets to relative references.

### Shader Workflow

For artists, shaders usually follow this loop:

1. inspect available templates
2. read a template before using it
3. apply it to a GLSL TOP
4. tweak DAT content or parameters live
5. route the output to a visible TOP or COMP

```powershell
td-cli shaders list
td-cli shaders get plasma
td-cli shaders apply plasma /project1/glsl1
td-cli dat read /project1/glsl1_pixel
td-cli screenshot /project1/glsl1 -o glsl.png
```

### POP Audio Visual Workflow

If you want a ready-made POP scene for live audio, `td-cli` can build one directly under a safe container instead of rewriting the whole project root.

```powershell
td-cli pop av --root /project1 --name popAudioVisual
td-cli screenshot /project1/popAudioVisual/out -o pop-av.png
```

This creates:

- `/project1/popAudioVisual` with the audio CHOP chain, POP network, and TOP post-processing
- `/project1/popAudioVisual_preview` as a preview container wired to the output TOP

### Harness Loop

The harness surface is the structured loop for agentic TouchDesigner work: observe, apply, verify, inspect history, and roll back.

```powershell
td-cli harness capabilities
td-cli harness observe /project1 --depth 2
td-cli harness apply /project1 --file patch.json
td-cli harness verify /project1 --assert '{"kind":"family","equals":"COMP"}'
td-cli harness history
td-cli harness rollback 1712900000-harness
```

`apply` expects JSON shaped like:

```json
{
  "targetPath": "/project1",
  "goal": "add preview chain",
  "operations": [
    {
      "route": "/ops/create",
      "body": { "type": "nullTOP", "parent": "/project1", "name": "out1" }
    }
  ]
}
```

Important: do not target a scope that contains `TDCliServer`. Use a child COMP scope such as `/project1/myScene`, not `/project1`, for harness mutation and rollback.

### Beginner Install Guide

#### 1. Prerequisites

- TouchDesigner installed and able to open projects
- a terminal such as PowerShell on Windows
- one of the following:
  - prebuilt `td-cli.exe` from GitHub Releases
  - Go `1.26.1` or newer if building from source

#### 2. Install the CLI

Option A: download a release binary

1. Download `td-cli.exe` from [Releases](https://github.com/0dot77/td-cli/releases).
2. Put it somewhere easy to find, for example `C:\Tools\td-cli\td-cli.exe`.
3. Either run it by full path or add that folder to `PATH`.

Example:

```powershell
C:\Tools\td-cli\td-cli.exe version
```

Option B: install with Go

```powershell
go install github.com/0dot77/td-cli/cmd/td-cli@latest
```

To build this repository directly:

```powershell
go build -o td-cli.exe ./cmd/td-cli/
```

#### 3. Install the TouchDesigner Connector

You must add the `TDCliServer` connector to your TouchDesigner project before `td-cli` can connect.

Recommended setup:

1. Open your TouchDesigner project.
2. Drag-and-drop [`tox/TDCliServer.tox`](tox/TDCliServer.tox) into the root network, or import it from TouchDesigner.
3. Make sure the imported component is named `TDCliServer`.
4. Open it and verify that `webserver1` is active on port `9500`.

Normal usage boundary:

- treat `TDCliServer` as an installed runtime connector
- use `td-cli` commands to inspect and modify the rest of the project
- avoid editing `/project1/TDCliServer/*` during normal AI or artist workflows

Developer-only reference files for connector work:

- [`td/webserver_callbacks.py`](td/webserver_callbacks.py)
- [`td/td_cli_handler.py`](td/td_cli_handler.py)
- [`td/heartbeat.py`](td/heartbeat.py)

Detailed setup notes are also in [`td/setup_instructions.md`](td/setup_instructions.md).

#### 4. Verify the Connection

```powershell
td-cli status
```

Expected result:

```text
Connected to TouchDesigner
  Project:    ...
  TD Version: ...
  Server:     td-cli v...
  Connector:  TDCliServer v...
```

If multiple TouchDesigner projects are open:

```powershell
td-cli instances
td-cli --port 9500 status
td-cli --project "C:\path\to\your\project.toe" status
```

#### 5. Bootstrap Agent Guidance

```powershell
td-cli init
```

This creates a `CLAUDE.md` file with command examples and usage notes. The CLI itself is not Claude-specific; Codex and other agents can use the same commands directly, or adapt the generated guidance into `AGENTS.md` or another instruction format.

The generated guidance tells agents to treat `TDCliServer` as the installed connector boundary and to use `td-cli` as the main execution surface.

### First Commands To Try

```powershell
td-cli status
td-cli instances
td-cli ops list /project1
td-cli ops create noiseTOP /project1 --name myNoise
td-cli par get /project1/myNoise
td-cli par set /project1/myNoise period 4
td-cli dat read /project1/text1
td-cli exec "print(op('/project1').children)"
```

### Main Commands

| Command | Description |
|------|------|
| `td-cli status` | Check TD connection |
| `td-cli instances` | List running TD instances |
| `td-cli exec "<code>"` | Execute Python in TD |
| `td-cli exec -f script.py` | Execute a local Python file in TD |
| `td-cli ops list [path]` | List operators |
| `td-cli ops create <type> <parent>` | Create an operator |
| `td-cli ops delete <path>` | Delete an operator |
| `td-cli ops info <path>` | Show operator details |
| `td-cli par get <op> [names]` | Read parameter values |
| `td-cli par set <op> <name> <value>` | Set one or more parameters |
| `td-cli connect <src> <dst>` | Connect operators |
| `td-cli disconnect <src> <dst>` | Disconnect operators |
| `td-cli dat read <path>` | Read DAT content |
| `td-cli dat write <path> <content>` | Write DAT content |
| `td-cli screenshot [path] -o file.png` | Save TOP output as PNG |
| `td-cli project info` | Show project metadata |
| `td-cli project save [path]` | Save the project |
| `td-cli backup list [--limit N]` | List recent backup artifacts |
| `td-cli backup restore <backup-id>` | Restore a previous backup |
| `td-cli logs list [--limit N]` | List recent audit log events |
| `td-cli logs tail [--limit N]` | Read recent audit log events |
| `td-cli tox export <comp> -o file.tox` | Export a COMP as `.tox` |
| `td-cli tox import <file.tox> [parent]` | Import a `.tox` file |
| `td-cli network export [path] [-o file]` | Export a network snapshot |
| `td-cli network import <file> [path]` | Import a network snapshot |
| `td-cli describe [path]` | Generate an AI-friendly network summary |
| `td-cli diff <file1> <file2>` | Compare two snapshots |
| `td-cli diff --live <file> [path]` | Compare a snapshot against live TD state |
| `td-cli watch [path] [--interval ms]` | Monitor live performance |
| `td-cli tools list` | List available tool routes for agent discovery |
| `td-cli shaders list` | List shader templates |
| `td-cli shaders get <name>` | Show shader template details |
| `td-cli shaders apply <name> <glsl_top_path>` | Apply a shader template |
| `td-cli pop av [audio-reactive] [--root /project1] [--name popAudioVisual]` | Build a POP audio reactive scene |
| `td-cli docs` | Browse offline docs |
| `td-cli docs <operator>` | Look up an operator |
| `td-cli docs api [class]` | Read Python API docs |
| `td-cli init` | Generate CLAUDE.md + AGENTS.md for agent integration |
| `td-cli doctor` | Diagnose setup and connection issues |
| `td-cli update` | Self-update from GitHub Releases |
| `td-cli version` | Show version |

### Global Flags

- `--port <N>`: connect to a specific port
- `--project <path>`: target a specific `.toe` project
- `--json`: output raw JSON
- `--debug`: log HTTP requests and responses to stderr
- `--timeout <ms>`: change request timeout, default `30000`

### Troubleshooting

Run `td-cli doctor` first — it checks the home directory, heartbeat files, port reachability, server health, and protocol version in one pass.

If `td-cli status` reports no running TouchDesigner instances:

- confirm the TouchDesigner project is actually open
- confirm `webserver1` is active on port `9500`
- confirm the heartbeat callback is running
- confirm `~/.td-cli/instances/` is being updated
- if `status` shows a connector protocol warning, replace the project connector with the current `TDCliServer.tox`

If multiple projects are running:

- check the list with `td-cli instances`
- then target the right one with `--port` or `--project`

If a visual result exists but you still do not see it:

- route the output to a visible `Background TOP`, viewer, or window
- use `td-cli screenshot` to verify that the TOP is actually rendering
- check OP-reference parameters and prefer relative paths like `./out1`

If the command is not found:

- try the full path to `td-cli.exe`
- if that works, add its folder to `PATH`

### Security

td-cli communicates with TouchDesigner over HTTP on `127.0.0.1` (localhost only). It is designed for local, single-user workflows.

**Code execution:** The `td-cli exec` command runs arbitrary Python code inside the TouchDesigner process. This is by design — it gives agents and artists full scripting access. Anyone who can reach the HTTP port can execute code with the same permissions as the TouchDesigner process.

**Authentication:** Set `TD_CLI_TOKEN` in both the shell and the TouchDesigner process environment to require HMAC token verification on every request. Without the token, any process on the same machine can use the API.

**When to enable the token:**
- Shared workstations where multiple users are logged in
- Environments where untrusted code runs alongside TouchDesigner
- Remote access via SSH tunnels

**CORS:** The server only accepts requests from `localhost` and `127.0.0.1` origins. Cross-origin requests from other hosts are rejected.

For typical local use (single user, single machine), running without a token is fine.

### Development

Build locally:

```powershell
go build -o td-cli.exe ./cmd/td-cli/
```

Show help:

```powershell
td-cli help
```


## License

MIT
