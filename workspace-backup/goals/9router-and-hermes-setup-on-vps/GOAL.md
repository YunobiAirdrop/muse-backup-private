# 9Router and Hermes setup on VPS

Goal ID: goal_c457dc6996f9
Goal slug: 9router-and-hermes-setup-on-vps

## Description
Yunobi asked to install 9Router on this VPS, register a provider node and model combo via its API, save the 9Router and bridge API keys as backup, then install Hermes and point its default model at the 9Router provider. The 9Router service, OpenRouter provider node, hermes-main combo, and Hermes config are now verified working; the diagnosis pinned the last blocker as an empty OpenRouter balance (402), and Yunobi was asked to top up before the final end-to-end hermes -z test. Direct phone access to the 9Router dashboard proved impossible (no public IP, all tunnels blocked), so the assistant operates the dashboard from the VM and reports stats on request.
