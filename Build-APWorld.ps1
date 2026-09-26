$src = "$PSScriptRoot\PokemonTHTOrigins"
$out = "$PSScriptRoot\PokemonTHTOrigins.apworld"
$deploy = "C:\ProgramData\Archipelago\custom_worlds\PokemonTHTOrigins.apworld"

Remove-Item $out -ErrorAction SilentlyContinue
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::Open($out, 'Create')
Get-ChildItem $src -Recurse -File | Where-Object { $_.FullName -notmatch '\\__pycache__\\' } | ForEach-Object {
    $relPath = $_.FullName.Substring($src.Length + 1).Replace("\", "/")
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, "PokemonTHTOrigins/$relPath") | Out-Null
}
$zip.Dispose()

Write-Output "Built: $out"

if (Test-Path "C:\ProgramData\Archipelago") {
    Copy-Item $out $deploy -Force
    Write-Output "Deployed to: $deploy"
}
