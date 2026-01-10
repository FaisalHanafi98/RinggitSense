# Helper script to run specify commands with proper UTF-8 encoding
# Usage: .\run-specify.ps1 <specify arguments>
# Example: .\run-specify.ps1 init --here --force

$env:PYTHONUTF8 = "1"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$uvxPath = "C:\Users\asbou\AppData\Roaming\Python\Python314\Scripts\uvx.exe"
$specifySource = "git+https://github.com/github/spec-kit.git"

& $uvxPath --from $specifySource specify $args
