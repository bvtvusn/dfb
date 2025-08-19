Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create main form
$form = New-Object System.Windows.Forms.Form
$form.Text = "DFB Converter"
$form.Size = New-Object System.Drawing.Size(600,400)
$form.StartPosition = "CenterScreen"

# Folder selection
$folderLabel = New-Object System.Windows.Forms.Label
$folderLabel.Location = New-Object System.Drawing.Point(10,20)
$folderLabel.Size = New-Object System.Drawing.Size(100,20)
$folderLabel.Text = "Folder:"

$folderBox = New-Object System.Windows.Forms.TextBox
$folderBox.Location = New-Object System.Drawing.Point(120,20)
$folderBox.Size = New-Object System.Drawing.Size(350,20)
$folderBox.Text = [Environment]::GetFolderPath("UserProfile")

$folderButton = New-Object System.Windows.Forms.Button
$folderButton.Location = New-Object System.Drawing.Point(480,20)
$folderButton.Size = New-Object System.Drawing.Size(80,20)
$folderButton.Text = "Browse"
$folderButton.Add_Click({
    $folder = New-Object System.Windows.Forms.FolderBrowserDialog
    if ($folder.ShowDialog() -eq "OK") {
        $folderBox.Text = $folder.SelectedPath
    }
})

# Buttons
$extractButton = New-Object System.Windows.Forms.Button
$extractButton.Location = New-Object System.Drawing.Point(120,60)
$extractButton.Size = New-Object System.Drawing.Size(100,30)
$extractButton.Text = "Extract"

$bundleButton = New-Object System.Windows.Forms.Button
$bundleButton.Location = New-Object System.Drawing.Point(240,60)
$bundleButton.Size = New-Object System.Drawing.Size(100,30)
$bundleButton.Text = "Bundle"

# DFB text area
$dfbLabel = New-Object System.Windows.Forms.Label
$dfbLabel.Location = New-Object System.Drawing.Point(10,110)
$dfbLabel.Size = New-Object System.Drawing.Size(100,20)
$dfbLabel.Text = "DFB Content:"

$dfbBox = New-Object System.Windows.Forms.TextBox
$dfbBox.Location = New-Object System.Drawing.Point(10,130)
$dfbBox.Size = New-Object System.Drawing.Size(560,120)
$dfbBox.Multiline = $true
$dfbBox.ScrollBars = "Vertical"
$dfbBox.Font = New-Object System.Drawing.Font("Consolas", 9)

# Log area
$logLabel = New-Object System.Windows.Forms.Label
$logLabel.Location = New-Object System.Drawing.Point(10,260)
$logLabel.Size = New-Object System.Drawing.Size(100,20)
$logLabel.Text = "Log:"

$logBox = New-Object System.Windows.Forms.TextBox
$logBox.Location = New-Object System.Drawing.Point(10,280)
$logBox.Size = New-Object System.Drawing.Size(560,100)
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
    
    $files = Get-ChildItem -Path $FolderPath -Recurse -File
    foreach ($file in $files) {
        try {
            $relativePath = $file.FullName.Substring($FolderPath.Length + 1) -replace "\\", "/"
            
            # Check if file is likely text-based by extension
            $textExtensions = @('.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.log', '.csv', '.bat', '.ps1', '.sh')
            $isTextFile = $textExtensions -contains $file.Extension.ToLower()
            
            if ($isTextFile) {
                try {
                    $content = Get-Content $file.FullName -Raw -Encoding UTF8
                    $encoding = "utf-8"
                }
                catch {
                    # Fall back to binary if text reading fails
                    $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
                    $content = [System.Convert]::ToBase64String($bytes)
                    $encoding = "base64"
                }
            }
            else {
                # Binary file - read as bytes and encode as base64
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
    
    if (-not $DFBContent.Trim()) {
        throw "No DFB content to extract"
    }
    
    $lines = $DFBContent -split "`n"
    Write-Log "Parsing DFB with $($lines.Count) lines"
    
    # Check header
    if ($lines[0].Trim() -ne "DFB V1") {
        throw "Invalid DFB header"
    }
    
    # Find separator
    $separator = $null
    for ($i = 1; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match "^SEPARATOR: (.+)$") {
            $separator = $matches[1]
            break
        }
        if (-not $lines[$i].Trim()) { break }
    }
    
    if (-not $separator) {
        throw "No separator found"
    }
    
    Write-Log "Found separator: $($separator.Substring(0, [Math]::Min(20, $separator.Length)))..."
    
    # Skip control block
    while ($i -lt $lines.Count -and $lines[$i].Trim()) { $i++ }
    $i++
    
    Write-Log "Starting to parse entries from line $i"
    
    # Parse entries
    $currentMetadata = @{}
    $currentContent = @()
    $inMetadata = $true
    $extractedFiles = @()
    
    while ($i -lt $lines.Count) {
        $line = $lines[$i]
        
        if ($line.Trim() -eq $separator) {
            # Save previous entry
            if ($currentMetadata.Count -gt 0) {
                $filename = Save-DFBFile -Metadata $currentMetadata -Content $currentContent -OutputFolder $OutputFolder
                if ($filename) {
                    $extractedFiles += $filename
                    Write-Log "Extracted: $filename"
                }
            }
            
            # Start new entry
            $currentMetadata = @{}
            $currentContent = @()
            $inMetadata = $true
            Write-Log "Found separator at line $i, starting new entry"
            $i++
            continue
        }
        
        # Process metadata and content
        if ($inMetadata) {
            if (-not $line.Trim()) {
                $inMetadata = $false
                Write-Log "Metadata complete, content starts at line $($i+1)"
            }
            else {
                if ($line -match "^(.+?): (.+)$") {
                    $key = $matches[1].Trim()
                    $value = $matches[2].Trim()
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
    
    # Save last entry
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
    
    # Security check
    if ($filename -match "\.\.|:") {
        Write-Log "Skipping unsafe filename: $filename"
        return $null
    }
    
    try {
        $outputPath = Join-Path $OutputFolder $filename
        $outputDir = Split-Path $outputPath -Parent
        
        if (-not (Test-Path $outputDir)) {
            New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
        }
        
        $encoding = $Metadata["ENCODING"].ToLower()
        Write-Log "File encoding: $encoding, content lines: $($Content.Count)"
        
        if ($encoding -eq "base64") {
            $base64Content = $Content -join "" -replace "`n|`r| "
            $bytes = [System.Convert]::FromBase64String($base64Content)
            [System.IO.File]::WriteAllBytes($outputPath, $bytes)
            Write-Log "Saved binary file: $filename ($($bytes.Length) bytes)"
        }
        else {
            [System.IO.File]::WriteAllText($outputPath, ($Content -join "`n"), [System.Text.Encoding]::UTF8)
            Write-Log "Saved text file: $filename ($($Content.Count) lines)"
        }
        
        return $filename
    }
    catch {
        Write-Log "Failed to extract $filename`: $($_.Exception.Message)"
        return $null
    }
}

# Button events
$extractButton.Add_Click({
    try {
        $dfbContent = $dfbBox.Text
        if (-not $dfbContent.Trim()) {
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
