# Builds both game versions and copies the runtime files to the local RimWorld Mods folder.
# Replaces the deployed copies of these folders; the DevTests launcher refuses to run until the install matches the working tree.
$ErrorActionPreference = "Stop"

# A git worktree lives outside the workspace, so RIMWORLD_SHARED_ROOT can point at the workspace's _Shared folder.
$sharedRoot = if ($env:RIMWORLD_SHARED_ROOT) { $env:RIMWORLD_SHARED_ROOT } else { Join-Path $PSScriptRoot "..\_Shared" }
. (Join-Path $sharedRoot "RimWorldModTools.ps1")

$project = Join-Path $PSScriptRoot "Source\Spearfishing.csproj"
Invoke-RimWorldDotNetBuild -ProjectPath $project -BuildArguments @('/p:UseSharedCompilation=false', '/p:RimWorldVersion=1.6')

# Keep this list equal to DevTests/devtests.json runtimeFolders.
$folders = @("About", "1.6", "1.7", "Defs", "Patches", "Languages", "Textures") |
    Where-Object { Test-Path -LiteralPath (Join-Path $PSScriptRoot $_) }

Invoke-RimWorldModDeploy `
    -ModName "Spearfishing" `
    -SourceRoot $PSScriptRoot `
    -BuildPath $project `
    -Configuration "Release" `
    -Folders $folders `
    -Files @("LoadFolders.xml") `
    -RemoveFilePatterns @("*.pdb")
