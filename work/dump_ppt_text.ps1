$ErrorActionPreference = 'Stop'
$src = 'D:\WILL\ECON102'
$out = 'D:\WILL\ECON102\work'
$map = [ordered]@{
  'Lecture 7.ppt'                              = 'lec07'
  'Lecture 8.ppt'                              = 'lec08'
  'Lecture 8 Public good Updated 20250416.ppt' = 'lec08b'
}
$ppt = New-Object -ComObject PowerPoint.Application
foreach ($k in $map.Keys) {
  $file = Join-Path $src $k
  $pres = $ppt.Presentations.Open($file, $true, $false, $false)
  $slides = @()
  for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $sl = $pres.Slides.Item($i)
    $txt = @()
    foreach ($sh in $sl.Shapes) {
      try {
        if ($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
          $t = $sh.TextFrame.TextRange.Text
          if ($t -and $t.Trim().Length -gt 0) { $txt += $t.Trim() }
        }
      } catch {}
    }
    $slides += [pscustomobject]@{ n = $i; text = ($txt -join "`n---`n"); pics = 0; notes = '' }
  }
  $obj = [pscustomobject]@{ file = $k; count = $pres.Slides.Count; size = @(720, 540); slides = $slides }
  $json = $obj | ConvertTo-Json -Depth 6
  $target = Join-Path $out ($map[$k] + '.json')
  [System.IO.File]::WriteAllText($target, $json, (New-Object System.Text.UTF8Encoding($false)))
  Write-Output "OK $k -> $($map[$k]) slides=$($pres.Slides.Count)"
  $pres.Close()
}
$ppt.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
