Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Fixed DFB extractor/bundler GUI
# - newline normalization
# - robust separator detection
# - exact separator matching
# - tolerant metadata handling (default encoding utf-8)
# - safe path containment checks
# - multi-line base64 handling
# - logging improvements
# NOTE: minor fixes applied to logging to avoid PowerShell parsing issue with "$var: ..."

# Create main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "DFB Converter (Fixed)"
$form.Size = New-Object System.Drawing.Size(700,500)
$form.StartPosition = "CenterScreen"

# Folder selection
$folderLabel = New-Object System.Windows.Forms.Label
$folderLabel.Location = New-Object System.Drawing.Point(10,16)
$folderLabel.Size = New-Object System.Drawing.Size(100,20)
$folderLabel.Text = "Folder:"

$folderBox = New-Object System.Windows.Forms.TextBox
$folderBox.Location = New-Object System.Drawing.Point(120,16)
$folderBox.Size = New-Object System.Drawing.Size(420,20)
$folderBox.Text = [Environment]::GetFolderPath("UserProfile")

$folderButton = New-Object System.Windows.Forms.Button
$folderButton.Location = New-Object System.Drawing.Point(550,16)
$folderButton.Size = New-Object System.Drawing.Size(100,20)
$folderButton.Text = "Browse"
$folderButton.Add_Click({
    $folder = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($folder.ShowDialog() -eq "OK") {
        $folderBox.Text = $folder.SelectedPath
    }
})

# Buttons
$extractButton = New-Object System.Windows.Forms.Button
$extractButton.Location = New-Object System.Drawing.Point(120,52)
$extractButton.Size = New-Object System.Drawing.Size(100,30)
$extractButton.Text = "Extract"

$bundleButton = New-Object System.Windows.Forms.Button
$bundleButton.Location = New-Object System.Drawing.Point(240,52)
$bundleButton.Size = New-Object System.Drawing.Size(100,30)
$bundleButton.Text = "Bundle"

# DFB text area
$dfbLabel = New-Object System.Windows.Forms.Label
$dfbLabel.Location = New-Object System.Drawing.Point(10,96)
$dfbLabel.Size = New-Object System.Drawing.Size(100,20)
$dfbLabel.Text = "DFB Content:"

$dfbBox = New-Object System.Windows.Forms.TextBox
$dfbBox.Location = New-Object System.Drawing.Point(10,116)
$dfbBox.Size = New-Object System.Drawing.Size(660,220)
$dfbBox.Multiline = $true
$dfbBox.ScrollBars = "Vertical"
$dfbBox.Font = New-Object System.Drawing.Font("Consolas", 9)

# Log area
$logLabel = New-Object System.Windows.Forms.Label
$logLabel.Location = New-Object System.Drawing.Point(10,344)
$logLabel.Size = New-Object System.Drawing.Size(100,20)
$logLabel.Text = "Log:"

$logBox = New-Object System.Windows.Forms.TextBox
$logBox.Location = New-Object System.Drawing.Point(10,364)
$logBox.Size = New-Object System.Drawing.Size(660,90)
$logBox.Multiline = $true
$logBox.ScrollBars = "Vertical"
$logBox.ReadOnly = $true
$logBox.Font = New-Object System.Drawing.Font("Consolas", 8)

# Add controls to form
$form.Controls.AddRange(@($folderLabel, $folderBox, $folderButton, $extractButton, $bundleButton, $dfbLabel, $dfbBox, $logLabel, $logBox))

# Log function
function Write-Log {
    param($Message)
    $timestamp = Get-Date -Format "HH:mm:ss"
    $logBox.AppendText("[$timestamp] $Message`r`n")
    $logBox.ScrollToCaret()
}

# DFB functions
function New-DFBSeparator {
    return "----DFB-SEP::$([System.Guid]::NewGuid())----"
}

function New-DFBFromFolder {
    param($FolderPath)
    
    if (-not (Test-Path $FolderPath)) {
        throw "Folder does not exist"
    }
    
    $separator = New-DFBSeparator
    $dfb = @("DFB V1", "SEPARATOR: $separator", "")
    
    $textExtensions = @('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.log', '.csv', '.bat', '.ps1', '.sh')
    $files = Get-ChildItem -Path $FolderPath -Recurse -File
    foreach ($file in $files) {
        try {
            $relativePath = $file.FullName.Substring($FolderPath.Length + 1) -replace "\\", "/"
            $isTextFile = $textExtensions -contains $file.Extension.ToLower()
            
            if ($isTextFile) {
                try {
                    $content = Get-Content -Raw -Encoding UTF8 -Path $file.FullName
                    $encoding = "utf-8"
                }
                catch {
                    $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
                    $content = [System.Convert]::ToBase64String($bytes)
                    $encoding = "base64"
                }
            }
            else {
                $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
                $content = [System.Convert]::ToBase64String($bytes)
                $encoding = "base64"
            }
            
            $dfb += @($separator, "FILENAME: $relativePath", "ENCODING: $encoding", "SIZE: $($file.Length)", "", $content)
            Write-Log "Added: $relativePath (encoding: $encoding)"
        }
        catch {
            Write-Log "Skipping $($file.Name): $($_.Exception.Message)"
        }
    }
    
    return $dfb -join "`n"
}

function Extract-DFB {
    param($DFBContent, $OutputFolder)
    
    if (-not $DFBContent -or -not $DFBContent.Trim()) {
        throw "No DFB content to extract"
    }
    
    # Normalize newlines to LF only to avoid CR issues
    $normalized = $DFBContent -replace "`r`n", "`n" -replace "`r", "`n"
    $lines = $normalized -split "`n"
    Write-Log "Parsing DFB with $($lines.Count) lines"
    
    # Check header (exact)
    if ($lines.Count -eq 0 -or $lines[0] -ne "DFB V1") {
        throw "Invalid DFB header"
    }
    
    # Find control block end and SEPARATOR value
    $separator = $null
    $i = 1
    while ($i -lt $lines.Count) {
        $line = $lines[$i]
        if ($line -match '^SEPARATOR:\s*(.+)$') {
            $separator = $matches[1]
        }
        if ($line -eq '') { break }   # blank line ends control block
        $i++
    }
    
    if (-not $separator) {
        throw "No separator found in control block"
    }
    Write-Log "Found separator: $separator"
    
    # Set parsing index to the line after the blank line that ended the control block
    while ($i -lt $lines.Count -and $lines[$i] -ne '') { $i++ }
    # now $i is index of blank line; move to next line
    $i++
    Write-Log "Starting to parse entries from line $i"
    
    # Parse entries
    $currentMetadata = @{}
    $currentContent = @()
    $inMetadata = $true
    $extractedFiles = @()
    
    while ($i -lt $lines.Count) {
        $line = $lines[$i]
        
        # Exact-match separator detection (no Trim)
        if ($line -eq $separator) {
            # Save previous entry if any
            if ($currentMetadata.Count -gt 0) {
                $filename = Save-DFBFile -Metadata $currentMetadata -Content $currentContent -OutputFolder $OutputFolder
                if ($filename) {
                    $extractedFiles += $filename
                    Write-Log "Extracted: $filename"
                }
            }
            # Reset for new entry
            $currentMetadata = @{}
            $currentContent = @()
            $inMetadata = $true
            Write-Log "Found separator at line $i, starting new entry"
            $i++
            continue
        }
        
        # Process metadata or content
        if ($inMetadata) {
            if ($line -eq '') {
                $inMetadata = $false
                Write-Log "Metadata complete, content starts at line $($i+1)"
            }
            else {
                if ($line -match '^([^:]+):\s*(.*)$') {
                    $key = $matches[1].Trim()
                    $value = $matches[2]  # do not over-strip value
                    $currentMetadata[$key] = $value
                    Write-Log "Added metadata: $key"
                }
            }
        }
        else {
            $currentContent += $line
        }
        
        $i++
    }
    
    # Save final entry if present
    if ($currentMetadata.Count -gt 0) {
        Write-Log "Processing final entry with metadata: $($currentMetadata.Keys -join ', ')"
        $filename = Save-DFBFile -Metadata $currentMetadata -Content $currentContent -OutputFolder $OutputFolder
        if ($filename) {
            $extractedFiles += $filename
            Write-Log "Extracted: $filename"
        }
    }
    
    Write-Log "Total entries processed, extracted $($extractedFiles.Count) files"
    return $extractedFiles
}

function Save-DFBFile {
    param($Metadata, $Content, $OutputFolder)
    
    if (-not $Metadata.ContainsKey("FILENAME")) {
        Write-Log "No FILENAME in metadata: $($Metadata.Keys -join ', ')"
        return $null
    }
    
    $filename = $Metadata["FILENAME"]
    Write-Log "Attempting to save file: $filename"
    
    try {
        # Combine and resolve full paths to prevent path traversal
        $outputPath = Join-Path -Path $OutputFolder -ChildPath $filename
        $fullOutput = [System.IO.Path]::GetFullPath($outputPath)
        $fullRoot = [System.IO.Path]::GetFullPath($OutputFolder)
        if (-not $fullOutput.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            Write-Log "Rejected filename that escapes root: $filename"
            return $null
        }
        
        $outputDir = Split-Path -Path $fullOutput -Parent
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        }
        
        $encoding = 'utf-8'
        if ($Metadata.ContainsKey("ENCODING") -and $Metadata["ENCODING"]) {
            $encoding = $Metadata["ENCODING"].ToLower()
        }
        
        Write-Log "File encoding: $encoding, content lines: $($Content.Count)"
        
        if ($encoding -eq "base64") {
            # Join all content lines and strip whitespace before decoding
            $base64Content = ($Content -join "") -replace '\s',''
            try {
                $bytes = [System.Convert]::FromBase64String($base64Content)
            } catch {
                Write-Log ("Invalid base64 for {0}: {1}" -f $filename, $_.Exception.Message)
                return $null
            }
            [System.IO.File]::WriteAllBytes($fullOutput, $bytes)
            Write-Log "Saved binary file: $filename ($($bytes.Length) bytes)"
        }
        else {
            # Treat as UTF-8 text; join lines using LF (we normalized earlier)
            $text = $Content -join "`n"
            [System.IO.File]::WriteAllText($fullOutput, $text, [System.Text.Encoding]::UTF8)
            Write-Log "Saved text file: $filename ($($Content.Count) lines)"
        }
        
        return $filename
    }
    catch {
        Write-Log ("Failed to extract {0}: {1}" -f $filename, $_.Exception.Message)
        return $null
    }
}

# Button events
$extractButton.Add_Click({
    try {
        $dfbContent = $dfbBox.Text
        if (-not $dfbContent -or -not $dfbContent.Trim()) {
            [System.Windows.Forms.MessageBox]::Show("No DFB content to extract", "Warning", "OK", "Warning")
            return
        }
        Write-Log "Starting extraction..."
        $extractedFiles = Extract-DFB -DFBContent $dfbContent -OutputFolder $folderBox.Text
        Write-Log "Extraction complete. Extracted $($extractedFiles.Count) files"
        [System.Windows.Forms.MessageBox]::Show("Files extracted to: $($folderBox.Text)", "Success", "OK", "Information")
    }
    catch {
        Write-Log "Extraction error: $($_.Exception.Message)"
        [System.Windows.Forms.MessageBox]::Show("Extraction failed: $($_.Exception.Message)", "Error", "OK", "Error")
    }
})

$bundleButton.Add_Click({
    try {
        if (-not (Test-Path $folderBox.Text)) {
            [System.Windows.Forms.MessageBox]::Show("Selected folder does not exist", "Error", "OK", "Error")
            return
        }
        Write-Log "Creating DFB from folder..."
        $dfbContent = New-DFBFromFolder -FolderPath $folderBox.Text
        $dfbBox.Text = $dfbContent
        Write-Log "DFB creation complete"
        [System.Windows.Forms.MessageBox]::Show("DFB created from folder", "Success", "OK", "Information")
    }
    catch {
        Write-Log "Creation error: $($_.Exception.Message)"
        [System.Windows.Forms.MessageBox]::Show("Creation failed: $($_.Exception.Message)", "Error", "OK", "Error")
    }
})

# Initialize
Write-Log "Application started"

# Show form
$form.ShowDialog()
