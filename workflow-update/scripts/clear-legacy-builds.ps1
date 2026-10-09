[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = 'Medium')]
param()
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..')).TrimEnd('\')
$currentRoot = Join-Path $taskRoot 'workflow-update'
$releaseRoot = Join-Path $currentRoot 'release'
$latest = Get-Content -LiteralPath (Join-Path $releaseRoot 'latest.json') -Raw | ConvertFrom-Json
$retained = [IO.Path]::GetFullPath($latest.directory).TrimEnd('\')
if (-not $retained.StartsWith($releaseRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $latest.executable -PathType Leaf)) { throw 'Latest build must exist inside the current release directory.' }

# These directories were the superseded root checkout. Current npm entry points
# forward to workflow-update; its own dependency install is complete. Root .tools
# is still the active Rust/vendor dependency, and neither user profile is included.
$obsolete = @('apps','assets','crates','dist','Docs','packages','release','scripts','target','tests','node_modules',
 'Cargo.lock','Cargo.toml','rust-toolchain.toml','tsconfig.json','vite.config.ts','vitest.config.ts',
 '软件工程文档-五页重构.patch','新版入口与文档同步说明.md','workflow-change-manifest.json','workflow-changes.patch','workflow-delivery-verification.json','.local\generate-contracts.mjs')
$targets = @($obsolete | ForEach-Object { [IO.Path]::GetFullPath((Join-Path $taskRoot $_)) })
$targets += @(Get-ChildItem -LiteralPath $releaseRoot -Directory | Where-Object { $_.Name -match '^FurryPatternCAD-[\d.]+-win-x64-[a-f0-9]{8}$' -and $_.FullName -ne $retained } | Select-Object -ExpandProperty FullName)
$inventory = @()
foreach ($target in $targets) {
 if (-not $target.StartsWith($taskRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or $target -eq $currentRoot -or $target -eq $retained) { throw "Unsafe target: $target" }
 if (-not (Test-Path -LiteralPath $target)) { continue }
 $item = Get-Item -LiteralPath $target -Force
 for ($ancestor = $item; $null -ne $ancestor; $ancestor = $(if ($ancestor.PSIsContainer) { $ancestor.Parent } else { $ancestor.Directory })) {
  if ($ancestor.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint)) { throw "Refusing linked path: $($ancestor.FullName)" }
 }
 $entries = if ($item.PSIsContainer) { @(Get-ChildItem -LiteralPath $target -Recurse -Force) } else { @($item) }
 if ($entries | Where-Object { $_.Attributes.HasFlag([IO.FileAttributes]::ReparsePoint) }) { throw "Refusing linked contents: $target" }
 $files = @($entries | Where-Object { -not $_.PSIsContainer })
 $inventory += [pscustomobject]@{path=$target;files=$files.Count;bytes=($files | Measure-Object Length -Sum).Sum}
}
$results = @()
foreach ($item in $inventory) {
 if ($PSCmdlet.ShouldProcess($item.path, 'Delete verified superseded source, dependencies or application build')) {
  try { Remove-Item -LiteralPath $item.path -Recurse -Force; if(Test-Path -LiteralPath $item.path){throw 'Target still exists'}; $results += [pscustomobject]@{path=$item.path;removed=$true;bytes=$item.bytes} }
  catch { $results += [pscustomobject]@{path=$item.path;removed=$false;error=$_.Exception.Message} }
 }
}
if (-not $WhatIfPreference) {
 [ordered]@{time=[DateTime]::UtcNow.ToString('o');retained=$retained;results=$results} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $currentRoot 'Docs\软件工程文档\59-legacy-cleanup.json')
}
$inventory | Format-Table -AutoSize
if ($results | Where-Object { -not $_.removed }) { throw 'Some legacy targets could not be removed; see 59-legacy-cleanup.json.' }
