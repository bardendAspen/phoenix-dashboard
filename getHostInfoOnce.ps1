$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
# Get machine list
$excelFile = "C:\Users\bardend\OneDrive - Aspen Technology, Inc\QE VM Hosts\VM list.xlsx"
$hostList = Get-Content -Path "C:\Users\BARDEND\Desktop\newDash\hostList.txt"
$workingDIR = "C:\Users\BARDEND\Desktop\newDash\data"

# Hit the spreadsheet
$objExcel = New-Object -ComObject Excel.Application
$objExcel.Visible = $False
$objExcel.DisplayAlerts = $False
$WorkBook = $objExcel.Workbooks.Open($excelFile)
$xlCSV = 6
$sheetNames = ($WorkBook.sheets | Select-Object -Property Name).Name
foreach ($Sheet in $sheetNames) {
    $WorkSheet = $WorkBook.sheets.item("$Sheet")
    $csv = Join-Path $workingDIR "user_$Sheet.csv"
    $WorkSheet.SaveAs($csv,$xlCSV)
}
$objExcel.quit()

# For each machine
foreach ($h in $hostList) {
    # Outfiles
    $hyperVFile = Join-Path $workingDIR "hyperV_$($h).csv"
    $otherFileOut = Join-Path $workingDIR "otherFiles_$($h).csv"
    $diskInfoFile = Join-Path $workingDIR "diskInfo_$($h).csv"
    $adminListFile = Join-Path $workingDIR "adminList_$($h).csv"

    # Open a session
    $session = New-PSSession -ComputerName $h

    # Get Hyper V Info
    $hyperV = Invoke-Command -Session $session -ScriptBlock {
        $allVMFiles = @()
        $vmList = Get-VM
        foreach ($vm in $vmList) {
            # Get all files in the path
            $allFiles = @()
            $allFiles += Get-ChildItem (split-path -parent $vm.HardDrives.Path)
            $allFiles += Get-ChildItem (Join-Path $vm.SmartPagingFilePath "\Snapshots") -Recurse
            $allFiles += Get-ChildItem (Join-Path $vm.SmartPagingFilePath "\Virtual Machines") -Recurse
            $allFiles += Get-ChildItem (Join-Path $vm.SnapshotFileLocation "\Snapshots") -Recurse
            $allFiles += Get-ChildItem (Join-Path $vm.SnapshotFileLocation "\Virtual Machines") -Recurse
            $allVMFiles += $allFiles | Sort-Object | Get-Unique
            $vmSizeGB = ($allFiles | Sort-Object | Get-Unique | Measure-Object -Property Length -Sum).Sum/1GB
            "`"$($vm.Name)`",`"$(Split-Path -Path $vm.HardDrives.Path -Qualifier)`",`"$([math]::Round($vmSizeGB,2))`""   
        }
        '--END--'
        # Get files on hard drive
        $allDiskFiles = @()
        $diskList = get-WmiObject win32_logicaldisk | Where-Object {$_.DeviceID -ne 'C:'}
        foreach ($disk in $diskList) {
            # Get all disk files, filter out
            $allDiskFiles = Get-ChildItem "$($disk.DeviceID)\" -Recurse -File
            $otherFiles = Compare-Object -ReferenceObject $allDiskFiles -DifferenceObject $allVMFiles -Property FullName -PassThru | Where-Object {$_.SideIndicator -eq "<="}
            foreach ($file in $otherFiles) {
                "`"$($disk.DeviceID)`",`"$($file.FullName)`",`"$([math]::Round($file.Length/1MB,4))`""
            }
        }
    }
    '"VM Name","Drive","VM Size (GB)"' > $hyperVFile
    '"Drive","File Path","File Size (MB)"' > $otherFileOut
    $outFile = $hyperVFile
    foreach ($line in $hyperV) {
        if ($line -eq "--END--") {
            $outFile = $otherFileOut
        } else {
            $line >> $outFile
        }
    }
    
    # Get Disk Info
    $diskInfo = Invoke-Command -Session $session -ScriptBlock {
        $diskList = get-WmiObject win32_logicaldisk
        '"Drive","Free Space (GB)","Drive Size (GB)"'
        foreach ($disk in $diskList) {
            "`"$($disk.DeviceID)`",`"$([math]::Round($disk.FreeSpace/1GB,2))`",`"$([math]::Round($disk.Size/1GB,2))`""
        }
    }
    $diskInfo > $diskInfoFile

    # Get Admin List
    $adminList = Invoke-Command -Session $session -ScriptBlock {
        net localgroup administrators
    } | sls 'CORP'
    "Admin List" > $adminListFile
    foreach ($admin in $adminList) {
        $admin >> $adminListFile
    }

    # Remove Session
    $session | Remove-PSSession

}