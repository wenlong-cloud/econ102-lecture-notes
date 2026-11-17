param(
  [string]$OutRoot = 'D:\WILL\ECON102\assets',
  [int]$W = 1600, [int]$H = 1200
)
$ErrorActionPreference = 'Continue'
$src = 'D:\WILL\ECON102'
# file -> output folder
$map = [ordered]@{
  'Lecture 1.pptx'                          = 'lec01'
  'Lecture 1 supplement_opportunity cost.pptx' = 'lec01s'
  'Lecture 2.pptx'                          = 'lec02'
  'Lecture 3.pptx'                          = 'lec03'
  'Lecture 4 without movie clips.pptx'      = 'lec04'
  'Lecture 5.pptx'                          = 'lec05'
  'Lecture 7.ppt'                           = 'lec07'
  'Lecture 8.ppt'                           = 'lec08'
  'Lecture 8 Public good Updated 20250416.ppt' = 'lec08b'
  'Lecture 8 supplement.pptx'               = 'lec08s'
  'Lecture 9 Tax and Reg.pptx'              = 'lec09'
  'Lecture 10 Game updated 20250506.pptx'   = 'lec10'
  'Lecture 12 Information Technology.pptx'  = 'lec12'
}
$ppt = New-Object -ComObject PowerPoint.Application
foreach ($k in $map.Keys) {
  $file = Join-Path $src $k
  $dir  = Join-Path $OutRoot $map[$k]
  if (-not (Test-Path $file)) { Write-Output "MISSING $k"; continue }
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  try {
    $pres = $ppt.Presentations.Open($file, $true, $false, $false)
    $pres.Export($dir, 'PNG', $W, $H)
    $n = (Get-ChildItem $dir -Filter '*.PNG' -ErrorAction SilentlyContinue).Count
    Write-Output "OK $k -> $($map[$k]) slides=$($pres.Slides.Count) png=$n"
    $pres.Close()
  } catch {
    Write-Output "FAIL $k : $($_.Exception.Message)"
  }
}
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
