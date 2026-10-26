$ErrorActionPreference = 'Stop'
try {
    $data = Join-Path $PSScriptRoot 'data'
    if (!(Test-Path -LiteralPath $data -PathType Container)) { throw 'Falta la carpeta data. Descargue y extraiga el repositorio completo.' }
    $folder = (Resolve-Path -LiteralPath $data).Path + [IO.Path]::DirectorySeparatorChar
    $quoted = '"' + $folder.Replace('"','""') + '"'
    $definition = Join-Path $PSScriptRoot 'Analytics.SemanticModel\definition'
    foreach ($table in (Get-ChildItem (Join-Path $definition 'tables') -Filter '*.tmdl')) {
        $csv = Join-Path $data ($table.BaseName + '.csv')
        if (!(Test-Path -LiteralPath $csv)) { throw ('Falta ' + $csv) }
    }
    $text = 'expression DataFolder = ' + $quoted + ' meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]' + [Environment]::NewLine + [char]9 + 'kind: m' + [Environment]::NewLine
    [IO.File]::WriteAllText((Join-Path $definition 'expressions.tmdl'), $text, (New-Object Text.UTF8Encoding($false)))
    Write-Host ('Datos configurados: ' + $folder)
    Invoke-Item -LiteralPath (Join-Path $PSScriptRoot 'Analytics.pbip')
} catch {
    Write-Error $_
    exit 1
}
